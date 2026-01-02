import sqlite3
import datetime
import os

DB_NAME = "data/database.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Logs table
    # type: 'entry', 'phone_detected', 'unauthorized', 'unknown_person'
    # REMOVED snapshot_path
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER, 
                  user_name TEXT,
                  event_type TEXT NOT NULL,
                  timestamp TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    # Admins table
    c.execute('''CREATE TABLE IF NOT EXISTS admins
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL UNIQUE,
                  password_hash TEXT NOT NULL)''')
                  
    conn.commit()
    conn.close()

    # Create default admin if none exists
    create_default_admin()

def create_default_admin():
    from werkzeug.security import generate_password_hash
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT count(*) FROM admins")
    if c.fetchone()[0] == 0:
        # Default: admin / admin123
        hashed = generate_password_hash("admin123")
        c.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)", ("admin", hashed))
        print("Default admin created: admin / admin123")
        conn.commit()
    conn.close()

def get_admin(username):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM admins WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_admin_by_id(admin_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def add_user(name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO users (name) VALUES (?)", (name,))
    user_id = c.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_users():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    c.execute("DELETE FROM logs WHERE user_id = ?", (user_id,)) # Optional: Keep logs or delete? usually keep logs but nullify user_id
    conn.commit()
    conn.close()

def update_user(user_id, new_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET name = ? WHERE id = ?", (new_name, user_id))
    conn.commit()
    conn.close()

def log_event(user_id, user_name, event_type):
    # Use accurate local time string
    local_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO logs (user_id, user_name, event_type, timestamp) VALUES (?, ?, ?, ?)",
              (user_id, user_name, event_type, local_time))
    conn.commit()
    conn.close()

def get_local_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_logs(limit=50):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def search_logs(query=None, start_date=None, end_date=None, event_type=None):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    sql = "SELECT * FROM logs WHERE 1=1"
    params = []
    
    if query:
        sql += " AND (user_name LIKE ? OR event_type LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
    
    if event_type and event_type != 'all':
        sql += " AND event_type = ?"
        params.append(event_type)
        
    if start_date:
        sql += " AND timestamp >= ?"
        params.append(start_date)
        
    if end_date:
        sql += " AND timestamp <= ?"
        params.append(end_date + " 23:59:59")
        
    sql += " ORDER BY timestamp DESC"
    
    c.execute(sql, params)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
