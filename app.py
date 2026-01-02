from flask import Flask, render_template, request, jsonify, Response
import database
import os
import cv2
import numpy as np
import base64
import time

app = Flask(__name__)
database.init_db()

# Directory to store registered faces and snapshots
FACES_DIR = "data/faces"
SNAPSHOTS_DIR = "static/snapshots"
os.makedirs(FACES_DIR, exist_ok=True)
os.makedirs(SNAPSHOTS_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/users')
def users_page():
    return render_template('users.html')

@app.route('/api/register', methods=['POST'])
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
def api_get_users():
    users = database.get_users()
    return jsonify(users)

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    # Also delete face images
    import shutil
    user_dir = os.path.join(FACES_DIR, str(user_id))
    if os.path.exists(user_dir):
        shutil.rmtree(user_dir)
        
    database.delete_user(user_id)
    return jsonify({'success': True})

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def api_update_user(user_id):
    data = request.json
    new_name = data.get('name')
    if new_name:
        database.update_user(user_id, new_name)
        return jsonify({'success': True})
    return jsonify({'error': 'No name provided'}), 400

@app.route('/api/logs')
def api_logs():
    logs = database.get_logs()
    return jsonify(logs)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
