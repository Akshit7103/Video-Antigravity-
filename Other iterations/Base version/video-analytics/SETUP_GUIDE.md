# Video Analytics System - Setup Guide

Complete setup guide for the Face Recognition Video Analytics System.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [Running the System](#running-the-system)
5. [Usage](#usage)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **OS**: Windows, Linux, or macOS
- **Python**: 3.9 or higher
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 10GB free space
- **Camera**: Webcam or IP camera (optional for testing)

### Software Dependencies
- Python 3.9+
- PostgreSQL 12+ (or Docker)
- Redis 6+ (or Docker)
- Git (for cloning)

---

## Installation Methods

### Method 1: Docker (Recommended)

Docker provides the easiest setup with all dependencies included.

#### Step 1: Install Docker
- Download from https://www.docker.com/get-started
- Install Docker Desktop (includes Docker Compose)

#### Step 2: Clone Repository
```bash
git clone <your-repo-url>
cd video-analytics
```

#### Step 3: Build and Run
```bash
# Build containers
docker-compose build

# Start all services
docker-compose up -d

# Initialize database
docker-compose exec backend python backend/database/init_db.py
```

#### Step 4: Access Application
- Backend API: http://localhost:8000
- Frontend: http://localhost (if using nginx) or open `frontend/pages/index.html`
- API Docs: http://localhost:8000/docs

---

### Method 2: Local Installation

For development or if you prefer not to use Docker.

#### Step 1: Install PostgreSQL
**Windows:**
- Download from https://www.postgresql.org/download/windows/
- Install and remember your password
- Create database: `CREATE DATABASE video_analytics;`

**Linux:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres createdb video_analytics
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
createdb video_analytics
```

#### Step 2: Install Redis
**Windows:**
- Download from https://github.com/microsoftarchive/redis/releases
- Or use WSL with: `sudo apt-get install redis-server`

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

#### Step 3: Install CMake and Build Tools
**Windows:**
- Install Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/
- Install CMake: https://cmake.org/download/

**Linux:**
```bash
sudo apt-get install build-essential cmake libopencv-dev
```

**macOS:**
```bash
brew install cmake
```

#### Step 4: Create Python Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/macOS)
source venv/bin/activate
```

#### Step 5: Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** If `dlib` installation fails:
- Windows: Install Visual Studio C++ Build Tools first
- Linux: `sudo apt-get install libboost-all-dev`
- macOS: `brew install boost`

#### Step 6: Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your database credentials
```

#### Step 7: Initialize Database
```bash
python backend/database/init_db.py
```

#### Step 8: Run Backend
```bash
cd backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 9: Serve Frontend
Open `frontend/pages/index.html` in your browser, or use a simple HTTP server:

```bash
# Python 3
python -m http.server 3000 --directory frontend

# Then open http://localhost:3000/pages/index.html
```

---

## Configuration

### Edit `config/config.yaml`

#### Database Configuration
```yaml
database:
  postgres:
    host: "localhost"
    port: 5432
    database: "video_analytics"
    user: "postgres"
    password: "your-password"
```

#### Camera Configuration
```yaml
camera:
  sources:
    - id: "cam_01"
      url: 0  # 0 for default webcam, or RTSP URL
      name: "Main Camera"
      enabled: true
```

#### Face Recognition Settings
```yaml
face_recognition:
  detection_model: "hog"  # 'hog' (CPU) or 'cnn' (GPU)
  recognition_threshold: 0.6  # Lower = stricter matching
```

#### Frontend Configuration
Edit `frontend/js/config.js`:
```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    // ... other settings
};
```

---

## Running the System

### Start Services

#### Using Docker:
```bash
docker-compose up -d
```

#### Manual:
```bash
# Terminal 1: Start Backend
cd video-analytics
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Serve Frontend
python -m http.server 3000 --directory frontend
```

### Stop Services

#### Using Docker:
```bash
docker-compose down
```

#### Manual:
Press `Ctrl+C` in each terminal

---

## Usage

### 1. Register Persons

**Via Web Interface:**
1. Open http://localhost:3000/pages/register.html (or your frontend URL)
2. Choose upload or webcam method
3. Fill in person details
4. Upload 3-5 clear face images from different angles
5. Click "Register Person"

**Via API:**
```bash
curl -X POST http://localhost:8000/api/persons/register \
  -F "name=John Doe" \
  -F "email=john@example.com" \
  -F "employee_id=EMP001" \
  -F "images=@photo1.jpg" \
  -F "images=@photo2.jpg" \
  -F "images=@photo3.jpg"
```

### 2. Start Camera Recognition

1. Go to Cameras page
2. Click "Start" on a camera
3. System will detect and recognize faces in real-time
4. Events are timestamped and logged to database

### 3. View Analytics

1. Go to Analytics page
2. Select time period (1 day, 7 days, 30 days, etc.)
3. View:
   - Total detections
   - Unique visitors
   - Top visitors
   - Recent activity

### 4. Manage Persons

1. Go to Persons page
2. View all registered persons
3. Click on a person to view details
4. Delete persons if needed

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Error
```
Error: could not connect to server
```
**Solution:**
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify credentials in `config/config.yaml`
- Test connection: `psql -U postgres -d video_analytics`

#### 2. Redis Connection Error
```
Error: Connection refused
```
**Solution:**
- Check Redis is running: `redis-cli ping`
- Should return `PONG`
- Start Redis: `sudo systemctl start redis`

#### 3. Face Recognition Not Working
```
No faces detected
```
**Solution:**
- Ensure good lighting
- Face should be clearly visible
- Try increasing `upsample_times` in config
- Check camera permissions

#### 4. dlib Installation Fails
**Windows:**
```bash
# Install Visual Studio Build Tools first
# Then try:
pip install cmake
pip install dlib
```

**Linux:**
```bash
sudo apt-get install build-essential cmake libboost-all-dev
pip install dlib
```

#### 5. CORS Errors in Browser
**Solution:**
- Backend CORS is configured to allow all origins in development
- For production, update CORS settings in `backend/api/main.py`

#### 6. Webcam Not Accessible
**Solution:**
- Check browser permissions
- On Linux, user may need to be in `video` group:
  ```bash
  sudo usermod -a -G video $USER
  ```
- Close other applications using the webcam

#### 7. Out of Memory
**Solution:**
- Reduce `frame_skip` in config (process fewer frames)
- Use `hog` instead of `cnn` detection model
- Reduce number of simultaneous camera streams

### Performance Optimization

#### For Better Speed:
```yaml
face_recognition:
  detection_model: "hog"  # Faster than CNN

camera:
  frame_skip: 3  # Process every 3rd frame
  fps: 15  # Lower FPS
```

#### For Better Accuracy:
```yaml
face_recognition:
  detection_model: "cnn"  # More accurate (requires GPU)
  recognition_threshold: 0.5  # Stricter matching

registration:
  samples_required: 7  # More samples per person
```

### Logs

Check logs for debugging:

**Docker:**
```bash
docker-compose logs backend
docker-compose logs postgres
```

**Manual:**
```bash
# Application logs
tail -f data/logs/app.log

# Database initialization logs
tail -f data/logs/db_init.log
```

### Getting Help

1. Check logs: `data/logs/app.log`
2. Verify configuration: `config/config.yaml`
3. Test API health: http://localhost:8000/api/health
4. Review API docs: http://localhost:8000/docs

---

## Next Steps

1. **Production Deployment:**
   - Use environment variables for secrets
   - Enable HTTPS
   - Set up reverse proxy (Nginx)
   - Configure firewall rules

2. **Advanced Features:**
   - Add liveness detection
   - Implement access control
   - Set up email notifications
   - Add video recording

3. **Monitoring:**
   - Set up logging aggregation
   - Add performance monitoring
   - Create alert rules

4. **Scaling:**
   - Deploy multiple camera processors
   - Use load balancer
   - Implement caching strategies

---

## Support

For issues and questions:
- Check troubleshooting section
- Review API documentation
- Check system logs

Enjoy using Video Analytics System!
