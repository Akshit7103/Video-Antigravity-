# Quick Installation Guide

## Step-by-Step Installation with Virtual Environment

### Prerequisites
- Python 3.9 or higher installed
- PostgreSQL installed (or use Docker)
- Git (optional)

---

## Windows Installation

### Step 1: Open Command Prompt or PowerShell
```cmd
# Navigate to the project directory
cd "C:\Users\akshi\OneDrive\Desktop\New folder (2)\video-analytics"
```

### Step 2: Create Virtual Environment
```cmd
# Create virtual environment named 'venv'
python -m venv venv
```

### Step 3: Activate Virtual Environment
```cmd
# For Command Prompt:
venv\Scripts\activate

# For PowerShell (if you get execution policy error, see troubleshooting below):
venv\Scripts\Activate.ps1
```

After activation, you should see `(venv)` at the beginning of your command prompt.

### Step 4: Upgrade pip
```cmd
python -m pip install --upgrade pip
```

### Step 5: Install Dependencies

**Option A: Install Core Dependencies First (Recommended)**

This installs dependencies in stages to catch errors early:

```cmd
# Install build tools and basic packages
pip install wheel setuptools

# Install CMake (needed for dlib)
pip install cmake

# Install numpy first (many packages depend on it)
pip install numpy==1.24.3

# Install dlib (this may take 5-10 minutes)
pip install dlib==19.24.2

# Install face_recognition
pip install face-recognition==1.3.0

# Install OpenCV
pip install opencv-python==4.8.1.78 opencv-contrib-python==4.8.1.78

# Install remaining packages
pip install -r requirements.txt
```

**Option B: Install All at Once**
```cmd
pip install -r requirements.txt
```

### Step 6: Install and Setup PostgreSQL

**Option 1: Using Docker (Easier)**
```cmd
# Install Docker Desktop from https://www.docker.com/products/docker-desktop
# Then run:
docker-compose up -d postgres redis
```

**Option 2: Manual PostgreSQL Installation**
1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Install with default settings
3. Remember the password you set for user `postgres`
4. Open SQL Shell (psql) and create database:
```sql
CREATE DATABASE video_analytics;
```

### Step 7: Configure Environment
```cmd
# Copy example environment file
copy .env.example .env

# Edit .env file with your database password
notepad .env
```

Update these lines in `.env`:
```
DB_PASSWORD=your_postgres_password_here
```

### Step 8: Initialize Database
```cmd
python backend/database/init_db.py
```

### Step 9: Run the Application
```cmd
# Start the backend server
python run.py
```

The server should start at: http://localhost:8000

### Step 10: Access the Frontend
Open a NEW command prompt/terminal and run:
```cmd
cd "C:\Users\akshi\OneDrive\Desktop\New folder (2)\video-analytics"
python -m http.server 3000 --directory frontend
```

Then open your browser to: http://localhost:3000/pages/index.html

---

## Linux/macOS Installation

### Step 1: Navigate to Project
```bash
cd "/path/to/video-analytics"
```

### Step 2: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake libopencv-dev \
    libboost-all-dev python3-dev python3-pip postgresql redis-server
```

**macOS:**
```bash
brew install cmake boost opencv postgresql redis
```

### Step 3: Create Virtual Environment
```bash
python3 -m venv venv
```

### Step 4: Activate Virtual Environment
```bash
source venv/bin/activate
```

### Step 5: Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Setup PostgreSQL

**Ubuntu/Debian:**
```bash
sudo systemctl start postgresql
sudo -u postgres createdb video_analytics
```

**macOS:**
```bash
brew services start postgresql
createdb video_analytics
```

### Step 7: Setup Redis
```bash
# Ubuntu/Debian
sudo systemctl start redis

# macOS
brew services start redis
```

### Step 8: Configure Environment
```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

### Step 9: Initialize Database
```bash
python backend/database/init_db.py
```

### Step 10: Run the Application
```bash
# Terminal 1: Backend
python run.py

# Terminal 2: Frontend
python -m http.server 3000 --directory frontend
```

---

## Troubleshooting

### Windows PowerShell Execution Policy Error
If you get an error activating the virtual environment in PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### dlib Installation Fails on Windows

**Error: "Microsoft Visual C++ 14.0 or greater is required"**

**Solution:**
1. Download and install "Build Tools for Visual Studio" from:
   https://visualstudio.microsoft.com/downloads/
2. During installation, select "Desktop development with C++"
3. Restart your computer
4. Try installing dlib again:
   ```cmd
   pip install dlib
   ```

### CMake Not Found

**Windows:**
Download and install CMake from: https://cmake.org/download/

**Linux:**
```bash
sudo apt-get install cmake
```

**macOS:**
```bash
brew install cmake
```

### PostgreSQL Connection Error

**Check if PostgreSQL is running:**
```bash
# Windows (Command Prompt as Admin)
sc query postgresql-x64-14  # or your version

# Linux
sudo systemctl status postgresql

# macOS
brew services list
```

**Start PostgreSQL if not running:**
```bash
# Windows
net start postgresql-x64-14

# Linux
sudo systemctl start postgresql

# macOS
brew services start postgresql
```

### Redis Connection Error

**Check if Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

**Start Redis if not running:**
```bash
# Windows (if using WSL)
sudo service redis-server start

# Linux
sudo systemctl start redis

# macOS
brew services start redis
```

### Import Errors After Installation

Make sure you're in the virtual environment:
- You should see `(venv)` in your command prompt
- If not, run the activation command again

### Port Already in Use

If port 8000 or 3000 is already in use:

**Find what's using the port (Windows):**
```cmd
netstat -ano | findstr :8000
```

**Find what's using the port (Linux/macOS):**
```bash
lsof -i :8000
```

**Use a different port:**
```cmd
# Backend on different port
uvicorn backend.api.main:app --port 8001

# Frontend on different port
python -m http.server 3001 --directory frontend
```

---

## Verify Installation

### Check Python Packages
```bash
pip list | grep -E "face-recognition|opencv|fastapi|dlib"
```

Should show:
- dlib
- face-recognition
- opencv-python
- fastapi
- (and related packages)

### Test API
Open browser to: http://localhost:8000/api/health

Should return:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "version": "1.0.0"
}
```

### Check Database Connection
```bash
python -c "from backend.database import get_db_manager; print('Database OK')"
```

---

## Using Docker Instead (Easiest Option)

If you encounter too many issues with manual installation, use Docker:

### Step 1: Install Docker
Download from: https://www.docker.com/products/docker-desktop

### Step 2: Build and Run
```bash
cd "C:\Users\akshi\OneDrive\Desktop\New folder (2)\video-analytics"
docker-compose up -d
```

### Step 3: Initialize Database
```bash
docker-compose exec backend python backend/database/init_db.py
```

### Step 4: Access Application
- Backend: http://localhost:8000
- Frontend: http://localhost (if nginx is configured) or open `frontend/pages/index.html`

---

## Next Steps After Installation

1. **Register your first person:**
   - Go to http://localhost:3000/pages/register.html
   - Upload 3-5 face images or use webcam
   - Fill in details and click "Register"

2. **Start camera recognition:**
   - Go to Cameras page
   - Click "Start" on a camera
   - System will detect and recognize faces

3. **View analytics:**
   - Go to Analytics page
   - See statistics and visitor patterns

---

## Deactivating Virtual Environment

When you're done working:
```bash
deactivate
```

## Reactivating Later

To work on the project again:
```bash
# Navigate to project
cd "C:\Users\akshi\OneDrive\Desktop\New folder (2)\video-analytics"

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate

# Run the application
python run.py
```

---

## Getting Help

If you encounter issues:
1. Check the error message carefully
2. Look in the Troubleshooting section above
3. Check logs: `data/logs/app.log`
4. Review `SETUP_GUIDE.md` for more details
5. Ensure all prerequisites are installed

Enjoy your Video Analytics System! 🚀
