# Quick Start Guide

Get the Video Analytics System up and running in 3 minutes!

## Prerequisites

- Python 3.9+ installed
- Webcam connected

**That's it! No Docker, no database installation needed!**

## Windows Quick Start (Easiest!)

### 1. Install Dependencies

Open terminal in project root:

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Local Script:**
```bash
cd ../local_script
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start the System

**Option A: Using Batch Files (Easiest)**

1. Double-click `start_backend.bat`
2. Wait for "Uvicorn running on http://0.0.0.0:8000"
3. Open browser: http://localhost:8000
4. Double-click `start_detection.bat` in a new window

**Option B: Manual Start**

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
python main.py
```

**Terminal 2 - Detection:**
```bash
cd local_script
venv\Scripts\activate
python main.py
```

## First Time Setup

### Step 1: Register Your First Person

1. Open http://localhost:8000
2. Click "Face Registration" tab
3. Click "Start Camera"
4. Position your face in frame (good lighting!)
5. Click "Capture Photo"
6. Enter your name
7. Click "Register Person"

Wait for success message!

### Step 2: Test Detection

The detection script should now be running with:
- Live webcam feed in a window
- Your face should show GREEN box with your name
- Console logs showing detections

### Step 3: View Dashboard

1. Go to http://localhost:8000
2. Click "Dashboard" tab
3. Watch real-time logs as you move!

## Testing Features

### ✅ Test Authorized Person
- Stand in front of camera
- Should see GREEN box with your name
- Dashboard logs: "Authorized"

### ✅ Test Unauthorized Person
- Have someone else stand in front of camera (or cover your face)
- Should see RED box with "Unknown"
- Dashboard logs: "Unauthorized"

### ✅ Test Phone Detection
- Hold your phone in front of camera
- Should see MAGENTA box around phone
- Check "Phone Detection Logs" in dashboard

### ✅ Test Multi-Person Tracking
- Multiple people in frame
- Each gets unique Track ID
- All tracked separately

## Controls

### Detection Window
- **'q'** - Quit detection
- **'s'** - Save screenshot

### Dashboard
- Auto-updates via WebSocket
- Manual refresh buttons available
- View registered people in "Registered People" tab

## What Gets Created

On first run, these files/folders are auto-created:

```
backend/
  └── video_analytics.db    # SQLite database (all your data)
  └── cache/                # Cache folder

local_script/
  └── (model downloads in ~/.insightface/ and YOLOv8 cache)
```

## Stopping the System

1. **Detection Window**: Press 'q'
2. **Backend Terminal**: Press Ctrl+C
3. **Close Browser**

## Restarting

To start again, just run:
```bash
# Terminal 1
cd backend
venv\Scripts\activate
python main.py

# Terminal 2
cd local_script
venv\Scripts\activate
python main.py
```

Or use the batch files!

## Common Issues

### ❌ "Camera not opening"
**Solution:**
- Try `CAMERA_INDEX=1` or `2` in `local_script/.env`
- Close other apps using webcam
- Check camera permissions in Windows Settings

### ❌ "No face detected" during registration
**Solution:**
- Improve lighting
- Face camera directly
- Move closer to camera
- Remove glasses temporarily

### ❌ "Module not found" errors
**Solution:**
```bash
# Make sure venv is activated (you should see (venv) in terminal)
venv\Scripts\activate
pip install -r requirements.txt
```

### ❌ Backend won't start
**Solution:**
- Make sure port 8000 is free
- Check if another instance is running
- Kill any python processes and try again

### ❌ Low FPS / Slow detection
**Solution:**
- Close other heavy applications
- Edit `local_script/config.py`: set `DETECTION_FPS = 15`
- First run is slower (downloading models)

## Performance Tips

**First run will be slow** (~2-5 minutes) because it downloads:
- YOLOv8 model (~6MB)
- InsightFace models (~350MB)

After first run, everything is cached and starts instantly!

**Expected FPS:**
- Modern laptop (i5/Ryzen 5): 20-30 FPS
- Older laptop: 10-15 FPS
- Still very usable even at 10 FPS!

## Next Steps

✨ **You're all set!** The system is now:
- Detecting people in real-time
- Recognizing authorized faces
- Tracking movement
- Detecting phones
- Logging everything to dashboard

**Customize:**
- Adjust detection threshold in `backend/config.py`
- Change camera settings in `local_script/config.py`
- Register more people via web interface

**Explore:**
- API documentation: http://localhost:8000/docs
- View all logs in Dashboard
- Delete/manage registered people

---

**Happy monitoring!** 🎥👁️
