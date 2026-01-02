import cv2
import numpy as np
import base64
import time
import os
import shutil
import io
import csv
from typing import List, Optional

from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

import socketio
import uvicorn
from werkzeug.security import check_password_hash

import database

# --- Configuration ---
FACES_DIR = "data/faces"
SNAPSHOTS_DIR = "static/snapshots"
SECRET_KEY = "super_secret_key_change_this_later"

os.makedirs(FACES_DIR, exist_ok=True)
os.makedirs(SNAPSHOTS_DIR, exist_ok=True)

# --- Database Init ---
database.init_db()

# --- FastAPI App ---
app = FastAPI(title="Video Analytics Dashboard")

# Session Middleware (for Auth)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static & Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- SocketIO Setup (ASGI) ---
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

# --- Auth Dependencies ---
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        return None
    return user

def login_required(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"}
        )
    return user

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    admin = database.get_admin(username)
    if admin and check_password_hash(admin['password_hash'], password):
        request.session["user"] = {"id": admin['id'], "username": admin['username']}
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    # Check auth manually for page loads to redirect instead of 401
    if not request.session.get("user"): return RedirectResponse("/login")
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/users", response_class=HTMLResponse)
async def users_page(request: Request):
    if not request.session.get("user"): return RedirectResponse("/login")
    return templates.TemplateResponse("users.html", {"request": request})

# --- API Routes ---

@app.post("/api/register")
async def api_register(request: Request, data: dict):
    if not request.session.get("user"): raise HTTPException(401)
    
    name = data.get('name')
    images = data.get('images')
    
    if not name or not images:
        return JSONResponse({"error": "Missing data"}, status_code=400)
    
    user_id = database.add_user(name)
    user_dir = os.path.join(FACES_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    
    for i, img_data in enumerate(images):
        if img_data.startswith('data:image'):
            header, encoded = img_data.split(",", 1)
            file_data = base64.b64decode(encoded)
            with open(os.path.join(user_dir, f"{i}.jpg"), "wb") as f:
                f.write(file_data)
                
    return {"success": True, "user_id": user_id}

@app.get("/api/users")
async def api_get_users(request: Request):
    if not request.session.get("user"): raise HTTPException(401)
    users = database.get_users()
    return users

@app.delete("/api/users/{user_id}")
async def api_delete_user(request: Request, user_id: int):
    if not request.session.get("user"): raise HTTPException(401)
    
    user_dir = os.path.join(FACES_DIR, str(user_id))
    if os.path.exists(user_dir):
        shutil.rmtree(user_dir)
        
    database.delete_user(user_id)
    return {"success": True}

@app.put("/api/users/{user_id}")
async def api_update_user(request: Request, user_id: int, data: dict):
    if not request.session.get("user"): raise HTTPException(401)
    
    new_name = data.get('name')
    if new_name:
        database.update_user(user_id, new_name)
        return {"success": True}
    return JSONResponse({"error": "No name provided"}, status_code=400)

@app.get("/api/logs")
async def api_logs(
    request: Request,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    event_type: Optional[str] = None
):
    if not request.session.get("user"): raise HTTPException(401)
    
    if search or start_date or end_date or (event_type and event_type != 'all'):
        logs = database.search_logs(search, start_date, end_date, event_type)
    else:
        logs = database.get_logs(limit=100)
    return logs

@app.get("/api/export_logs")
async def export_logs(
    request: Request,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    event_type: Optional[str] = None
):
    if not request.session.get("user"): raise HTTPException(401)
    
    logs = database.search_logs(search, start_date, end_date, event_type)
    
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'User', 'Event Type', 'Timestamp'])
    for log in logs:
        cw.writerow([log['id'], log['user_name'], log['event_type'], log['timestamp']])
    
    return StreamingResponse(
        iter([si.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=security_logs.csv"}
    )

# --- WebSockets ---

@sio.event
async def connect(sid, environ):
    # We could check session cookies here (environ['HTTP_COOKIE']) but complex for now.
    print("Client Connected:", sid)

@sio.event
async def disconnect(sid):
    print("Client Disconnected:", sid)

@sio.event
async def log_event(sid, data):
    # Broadcast to all
    await sio.emit('new_log', data)

# Run instructions:
# Option 1: uvicorn main:socket_app --host 0.0.0.0 --port 5000 --reload
# Option 2: python main.py

if __name__ == "__main__":
    uvicorn.run("main:socket_app", host="0.0.0.0", port=5000, reload=True)
