@echo off
REM Video Analytics - Windows Installation Script
echo ============================================================
echo Video Analytics System - Automated Installation
echo ============================================================
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/8] Python found
python --version

REM Create virtual environment
echo.
echo [2/8] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully

REM Activate virtual environment
echo.
echo [3/8] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated

REM Upgrade pip
echo.
echo [4/8] Upgrading pip...
python -m pip install --upgrade pip
echo pip upgraded

REM Install dependencies
echo.
echo [5/8] Installing dependencies (this may take 10-15 minutes)...
echo Installing build tools...
pip install wheel setuptools cmake
echo.
echo Installing core packages...
pip install numpy==1.24.3
echo.
echo Installing dlib (this is the longest step, please be patient)...
pip install dlib==19.24.2
echo.
echo Installing remaining packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo WARNING: Some packages may have failed to install
    echo Check the error messages above
    echo You may need to install Visual Studio Build Tools
    echo.
    pause
)
echo All packages installed

REM Copy environment file
echo.
echo [6/8] Setting up configuration...
if not exist .env (
    copy .env.example .env
    echo Configuration file created: .env
    echo IMPORTANT: Edit .env file with your database password
) else (
    echo .env file already exists, skipping...
)

REM Create data directories
echo.
echo [7/8] Creating data directories...
if not exist data\faces mkdir data\faces
if not exist data\logs mkdir data\logs
if not exist data\videos mkdir data\videos
echo Data directories created

echo.
echo [8/8] Installation complete!
echo.
echo ============================================================
echo NEXT STEPS:
echo ============================================================
echo.
echo 1. Install PostgreSQL:
echo    - Download from: https://www.postgresql.org/download/windows/
echo    - Or use Docker: docker-compose up -d postgres redis
echo.
echo 2. Edit .env file with your database password:
echo    notepad .env
echo.
echo 3. Initialize database:
echo    python backend\database\init_db.py
echo.
echo 4. Run the application:
echo    python run.py
echo.
echo 5. In another terminal, serve frontend:
echo    python -m http.server 3000 --directory frontend
echo.
echo 6. Open browser to:
echo    http://localhost:3000/pages/index.html
echo.
echo ============================================================
echo.
echo NOTE: If dlib installation failed, you need to install
echo Visual Studio Build Tools from:
echo https://visualstudio.microsoft.com/downloads/
echo.
pause
