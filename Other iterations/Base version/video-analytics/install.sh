#!/bin/bash
# Video Analytics - Linux/macOS Installation Script

set -e  # Exit on error

echo "============================================================"
echo "Video Analytics System - Automated Installation"
echo "============================================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

echo "[1/8] Python found"
python3 --version

# Detect OS
OS=$(uname -s)
echo "Operating System: $OS"

# Install system dependencies
echo ""
echo "[2/8] Installing system dependencies..."
if [ "$OS" = "Linux" ]; then
    if command -v apt-get &> /dev/null; then
        echo "Installing packages for Ubuntu/Debian..."
        sudo apt-get update
        sudo apt-get install -y build-essential cmake libopencv-dev \
            libboost-all-dev python3-dev python3-pip python3-venv
    elif command -v yum &> /dev/null; then
        echo "Installing packages for CentOS/RHEL..."
        sudo yum install -y gcc gcc-c++ cmake opencv-devel \
            boost-devel python3-devel python3-pip
    else
        echo "WARNING: Unknown Linux distribution. Please install dependencies manually."
    fi
elif [ "$OS" = "Darwin" ]; then
    echo "Installing packages for macOS..."
    if ! command -v brew &> /dev/null; then
        echo "ERROR: Homebrew is not installed"
        echo "Install from: https://brew.sh/"
        exit 1
    fi
    brew install cmake boost opencv python3
fi

# Create virtual environment
echo ""
echo "[3/8] Creating virtual environment..."
python3 -m venv venv
echo "Virtual environment created"

# Activate virtual environment
echo ""
echo "[4/8] Activating virtual environment..."
source venv/bin/activate
echo "Virtual environment activated"

# Upgrade pip
echo ""
echo "[5/8] Upgrading pip..."
pip install --upgrade pip
echo "pip upgraded"

# Install dependencies
echo ""
echo "[6/8] Installing Python dependencies (this may take 10-15 minutes)..."
echo "Installing build tools..."
pip install wheel setuptools cmake

echo ""
echo "Installing core packages..."
pip install numpy==1.24.3

echo ""
echo "Installing dlib (this may take 5-10 minutes)..."
pip install dlib==19.24.2

echo ""
echo "Installing remaining packages..."
pip install -r requirements.txt
echo "All packages installed"

# Copy environment file
echo ""
echo "[7/8] Setting up configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Configuration file created: .env"
    echo "IMPORTANT: Edit .env file with your database credentials"
else
    echo ".env file already exists, skipping..."
fi

# Create data directories
echo ""
echo "[8/8] Creating data directories..."
mkdir -p data/faces data/logs data/videos
echo "Data directories created"

echo ""
echo "============================================================"
echo "Installation complete!"
echo "============================================================"
echo ""
echo "NEXT STEPS:"
echo "============================================================"
echo ""
echo "1. Install PostgreSQL and Redis:"

if [ "$OS" = "Linux" ]; then
    echo "   sudo apt-get install postgresql redis-server"
    echo "   sudo systemctl start postgresql redis"
    echo "   sudo -u postgres createdb video_analytics"
elif [ "$OS" = "Darwin" ]; then
    echo "   brew install postgresql redis"
    echo "   brew services start postgresql redis"
    echo "   createdb video_analytics"
fi

echo ""
echo "   OR use Docker:"
echo "   docker-compose up -d postgres redis"
echo ""
echo "2. Edit .env file with your database password:"
echo "   nano .env"
echo ""
echo "3. Activate virtual environment (in new terminals):"
echo "   source venv/bin/activate"
echo ""
echo "4. Initialize database:"
echo "   python backend/database/init_db.py"
echo ""
echo "5. Run the application:"
echo "   python run.py"
echo ""
echo "6. In another terminal, serve frontend:"
echo "   python -m http.server 3000 --directory frontend"
echo ""
echo "7. Open browser to:"
echo "   http://localhost:3000/pages/index.html"
echo ""
echo "============================================================"
echo ""
echo "For detailed instructions, see: INSTALL.md"
echo ""
