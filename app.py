from flask import Flask, render_template, request, jsonify, Response, redirect, url_for
import database
import os
import cv2
import numpy as np
import base64
import time
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_this_later' # Required for session
socketio = SocketIO(app, cors_allowed_origins="*") # Initialize SocketIO

database.init_db()

# --- Auth Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class AdminUser(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    admin = database.get_admin_by_id(user_id)
    if admin:
        return AdminUser(admin['id'], admin['username'])
    return None

# Directory to store registered faces and snapshots
FACES_DIR = "data/faces"
SNAPSHOTS_DIR = "static/snapshots"
os.makedirs(FACES_DIR, exist_ok=True)
os.makedirs(SNAPSHOTS_DIR, exist_ok=True)

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = database.get_admin(username)
        if admin and check_password_hash(admin['password_hash'], password):
            user = AdminUser(admin['id'], admin['username'])
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register')
@login_required
def register():
    return render_template('register.html')

@app.route('/users')
@login_required
def users_page():
    return render_template('users.html')

@app.route('/api/register', methods=['POST'])
@login_required
def api_register():
    data = request.json
    name = data.get('name')
    images = data.get('images') # List of base64 strings

    if not name or not images:
        return jsonify({'error': 'Missing name or images'}), 400

    # Create user in DB
    user_id = database.add_user(name)
    
    # Save images
    user_folder = os.path.join(FACES_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    
    for i, img_data in enumerate(images):
        # Remove header if present (data:image/jpeg;base64,...)
        if ',' in img_data:
            img_data = img_data.split(',')[1]
        
        img_bytes = base64.b64decode(img_data)
        img_arr = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
        
        if img is not None:
            cv2.imwrite(os.path.join(user_folder, f"{i}.jpg"), img)
    
    return jsonify({'success': True, 'user_id': user_id})

@app.route('/api/users', methods=['GET'])
@login_required
def api_get_users():
    users = database.get_users()
    return jsonify(users)

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def api_delete_user(user_id):
    # Also delete face images
    import shutil
    user_dir = os.path.join(FACES_DIR, str(user_id))
    if os.path.exists(user_dir):
        shutil.rmtree(user_dir)
        
    database.delete_user(user_id)
    return jsonify({'success': True})

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
def api_update_user(user_id):
    data = request.json
    new_name = data.get('name')
    if new_name:
        database.update_user(user_id, new_name)
        return jsonify({'success': True})
    return jsonify({'error': 'No name provided'}), 400

@app.route('/api/logs')
@login_required
def api_logs():
    # If query params exist, use search instead of default get_logs
    query = request.args.get('search')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    event_type = request.args.get('event_type')
    
    if query or start_date or end_date or (event_type and event_type != 'all'):
        logs = database.search_logs(query, start_date, end_date, event_type)
    else:
        logs = database.get_logs(limit=100)
    return jsonify(logs)

@app.route('/api/export_logs')
@login_required
def export_logs():
    import csv
    import io
    from flask import make_response
    
    # Get filtered logs (same logic/params as search usually, or just all)
    # For simplicity, let's export ALL logs or filtered if params passed
    query = request.args.get('search')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    event_type = request.args.get('event_type')
    
    logs = database.search_logs(query, start_date, end_date, event_type)
    
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'User', 'Event Type', 'Timestamp'])
    for log in logs:
        cw.writerow([log['id'], log['user_name'], log['event_type'], log['timestamp']])
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=security_logs.csv"
    output.headers["Content-type"] = "text/csv"
    return output

# SocketIO Event to receive logs from detect.py (if using client) 
# OR just a broadcast function we call from a REST endpoint.
# But here we will assume detect.py connects as a client and emits 'new_log'.

@socketio.on('log_event')
def handle_log_event(data):
    # Broadcast to all connected web clients
    emit('new_log', data, broadcast=True)

if __name__ == '__main__':
    # Use socketio.run instead of app.run
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
