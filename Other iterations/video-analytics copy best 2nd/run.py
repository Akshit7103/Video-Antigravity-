"""
Quick start script for Video Analytics System
Run this after installing dependencies
"""
import sys
import subprocess
from pathlib import Path


def main():
    print("=" * 60)
    print("Video Analytics System - Quick Start")
    print("=" * 60)
    print()

    # Check Python version
    if sys.version_info < (3, 9):
        print("ERROR: Python 3.9 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)

    print("[OK] Python version check passed")

    # Check if running from project root
    if not Path("backend").exists() or not Path("frontend").exists():
        print("ERROR: Please run this script from the project root directory")
        sys.exit(1)

    print("[OK] Directory structure verified")

    # Check if dependencies are installed
    try:
        import fastapi
        import cv2
        print("[OK] Core dependencies found")
    except ImportError as e:
        print(f"ERROR: Missing dependencies: {e}")
        print("\nPlease install dependencies first:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

    print()
    print("Starting Video Analytics System...")
    print("-" * 60)
    print()
    print("Backend will start on: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print()
    print("To access the frontend:")
    print("  1. Open another terminal")
    print("  2. Run: python -m http.server 3000 --directory frontend")
    print("  3. Open: http://localhost:3000/pages/index.html")
    print()
    print("-" * 60)
    print()
    print("Press Ctrl+C to stop the server")
    print()

    # Start uvicorn
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "backend.api.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        print("Goodbye!")


if __name__ == "__main__":
    main()
