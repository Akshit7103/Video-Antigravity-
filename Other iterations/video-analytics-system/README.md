# Video Analytics System

A comprehensive real-time video analytics system for detecting and tracking authorized and unauthorized people using webcam, with phone detection capabilities.

## Features

- **Real-time Person Detection**: YOLOv8-powered person detection
- **Multi-Person Tracking**: BoT-SORT tracker for continuous person tracking
- **Face Recognition**: SCRFD face detection with InsightFace ArcFace embeddings
- **Phone Detection**: Automatic detection of phones in frame
- **Authorization System**: Identify authorized vs unauthorized individuals
- **Web Dashboard**: Modern web interface for registration and monitoring
- **Real-time Updates**: WebSocket-based live log updates
- **Fast & Accurate**: Optimized for CPU-based inference with low latency
- **Zero Setup Database**: SQLite - no database installation required!

## Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **SQLite**: Zero-configuration file-based database
- **SQLAlchemy**: ORM for database operations
- **In-memory caching**: Fast face embedding lookups

### Computer Vision (Local Script)
- **YOLOv8**: Person and phone detection
- **BoT-SORT**: Multi-object tracking
- **SCRFD**: Fast and accurate face detection
- **InsightFace (ArcFace)**: State-of-the-art face recognition
- **OpenCV**: Video capture and processing

### Frontend
- **HTML/CSS/JavaScript**: Modern, responsive UI
- **WebSocket**: Real-time communication

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Local Detection Script                   │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  Webcam     │→ │  YOLOv8      │→ │  BoT-SORT        │   │
│  │  Capture    │  │  Person/Phone│  │  Tracker         │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
│                           ↓                                  │
│                    ┌──────────────┐                         │
│                    │  SCRFD Face  │                         │
│                    │  Detection   │                         │
│                    └──────────────┘                         │
│                           ↓                                  │
│                    ┌──────────────┐                         │
│                    │  ArcFace     │                         │
│                    │  Recognition │                         │
│                    └──────────────┘                         │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
                         ↓
            ┌────────────────────────┐
            │   FastAPI Backend      │
            │   ┌──────────────┐    │
            │   │ SQLite DB    │    │
            │   │ (file-based) │    │
            │   └──────────────┘    │
            └───────────┬────────────┘
                        │ WebSocket
                        ↓
            ┌────────────────────────┐
            │   Web Dashboard        │
            │  • Face Registration   │
            │  • Registered People   │
            │  • Detection Logs      │
            └────────────────────────┘
```

## Installation

### Prerequisites

- **Python 3.9+**
- **Webcam** (built-in or external)
- **Windows OS** (tested on Windows, adaptable for Linux/Mac)

That's it! No Docker, no database installation needed!

### Step 1: Clone/Download Project

```bash
cd video-analytics-system
```

### Step 2: Setup Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux/Mac

pip install -r requirements.txt
```

### Step 3: Setup Local Detection Script

```bash
cd ../local_script
python -m venv venv
venv\Scripts\activate  # On Windows

pip install -r requirements.txt
```

### Step 4: Download Model Files

The first time you run the scripts, they will automatically download:
- YOLOv8 weights (~6MB)
- InsightFace models (~350MB)

These will be cached locally for future use.

## Usage

### Quick Start (Using Batch Files)

**Easiest way on Windows:**

1. **Start Backend**: Double-click `start_backend.bat`
2. **Open Dashboard**: Go to http://localhost:8000
3. **Register People**: Use the "Face Registration" tab
4. **Start Detection**: Double-click `start_detection.bat`

### Manual Start

**1. Start the Backend Server**

```bash
cd backend
venv\Scripts\activate
python main.py
```

The API will be available at `http://localhost:8000`

Access the web dashboard at `http://localhost:8000`

**2. Register Authorized People**

1. Open web dashboard: `http://localhost:8000`
2. Go to "Face Registration" tab
3. Click "Start Camera"
4. Position face in frame
5. Click "Capture Photo"
6. Enter person's name
7. Click "Register Person"

**3. Start Local Detection Script**

In a new terminal:

```bash
cd local_script
venv\Scripts\activate
python main.py
```

This will:
- Open webcam feed
- Start real-time person detection and tracking
- Detect and recognize faces
- Detect phones in frame
- Send logs to backend
- Display annotated video with bounding boxes

**4. Monitor Dashboard**

Open `http://localhost:8000` and go to "Dashboard" tab to see:
- Real-time person detection logs (timestamp, name, status)
- Real-time phone detection logs
- Statistics (total, authorized, unauthorized)

## Features Explained

### Person Detection & Tracking

- Uses **YOLOv8** to detect all persons in frame
- **BoT-SORT** tracker assigns unique IDs and tracks movements
- Logs once when person enters frame
- Tracks continuously while in frame
- Logs again if person exits and re-enters

### Face Recognition

- **SCRFD** detects faces within person bounding boxes
- **ArcFace** generates 512-dimensional embeddings
- Cosine similarity matching against database
- Threshold: 0.5 (configurable)
- In-memory caching for fast lookups

### Phone Detection

- Detects cell phones using YOLOv8
- Logs whenever phone appears in frame
- 2-second cooldown to avoid duplicate logs
- Separate log section in dashboard

### Authorization System

- **Authorized**: Recognized person (name shown)
- **Unauthorized**: Unknown person (logged as "Unknown")
- Color coding: Green = Authorized, Red = Unauthorized

## Configuration

### Backend Configuration

Edit `backend/config.py` or `.env`:

- `DATABASE_URL`: Database path (default: sqlite:///./video_analytics.db)
- `API_PORT`: Backend server port (default: 8000)
- `FACE_SIMILARITY_THRESHOLD`: Recognition threshold (0.0-1.0, default: 0.5)
- `CACHE_DIR`: Directory for cache files

### Local Script Configuration

Edit `local_script/config.py` or `local_script/.env`:

- `API_BASE_URL`: Backend API URL (default: http://localhost:8000)
- `CAMERA_INDEX`: Webcam index (0 for default, 1 for external)
- `DETECTION_FPS`: Target FPS (default: 30)
- `YOLO_CONF_THRESHOLD`: Detection confidence (default: 0.5)
- `DISPLAY_VIDEO`: Show video window (default: True)

## API Documentation

Once backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

**Face Management:**
- `POST /api/faces/register` - Register new person
- `GET /api/faces/with-photos` - Get all registered people
- `DELETE /api/faces/{id}` - Delete person
- `POST /api/faces/match` - Match face embedding
- `POST /api/faces/extract-embedding` - Extract embedding from image

**Logging:**
- `POST /api/logs/person` - Log person detection
- `POST /api/logs/phone` - Log phone detection
- `GET /api/logs/person` - Get person logs (with filters)
- `GET /api/logs/phone` - Get phone logs
- `GET /api/logs/person/stats` - Get statistics

**WebSocket:**
- `WS /ws` - Real-time updates

## Performance Optimization

### For CPU-based Systems

The system is optimized for CPU:
- YOLOv8 nano model (fastest)
- Efficient tracking algorithm
- In-memory caching for embeddings
- Optimized detection pipeline
- SQLite for minimal overhead

### Recommended Hardware

- **CPU**: Intel i5 or AMD Ryzen 5 (or better)
- **RAM**: 8GB minimum, 16GB recommended
- **Webcam**: 720p or higher
- **Storage**: 2GB for models and cache

### Expected Performance

- **Detection**: 15-30 FPS on modern CPU
- **Recognition Latency**: <100ms per face
- **Database Query**: <10ms (with in-memory cache)

## Troubleshooting

### Camera Not Opening

- Check `CAMERA_INDEX` in config (try 0, 1, 2)
- Ensure no other app is using webcam
- Check camera permissions

### Face Not Detected During Registration

- Ensure good lighting
- Face should be front-facing
- Move closer to camera
- Remove glasses/masks if possible

### Low FPS / Performance Issues

- Close other applications
- Reduce `DETECTION_FPS` in config
- Ensure no GPU drivers interfering with CPU inference
- Check Task Manager for CPU usage

### WebSocket Not Connecting

- Check browser console for errors
- Ensure backend is running
- Clear browser cache
- Try different browser

### "Module not found" errors

- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

## Project Structure

```
video-analytics-system/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── config.py           # Configuration
│   ├── database.py         # Database setup
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas
│   ├── routes/             # API routes
│   ├── services/           # Business logic
│   ├── requirements.txt
│   └── video_analytics.db  # SQLite database (auto-created)
├── local_script/            # Detection script
│   ├── main.py             # Main detection loop
│   ├── config.py           # Configuration
│   ├── detectors/          # Detection modules
│   ├── tracking/           # BoT-SORT tracker
│   ├── utils/              # Utilities
│   └── requirements.txt
├── frontend/                # Web interface
│   ├── index.html
│   ├── css/
│   └── js/
├── start_backend.bat        # Windows: Start backend
├── start_detection.bat      # Windows: Start detection
├── .env.example            # Environment template
├── QUICKSTART.md           # Quick start guide
└── README.md               # This file
```

## Database Location

The SQLite database is automatically created as `backend/video_analytics.db`. This file contains:
- Registered persons (names, photos, face embeddings)
- Person detection logs
- Phone detection logs

To backup your data, simply copy this file. To reset the system, delete this file (it will be recreated on next start).

## Security Considerations

### For Production Use

1. **Use HTTPS** for web interface
2. **Implement authentication** for web dashboard
3. **Restrict API access** with API keys
4. **Use environment variables** for sensitive data
5. **Regular backups** of database file
6. **GDPR compliance** for face data storage

### Privacy

- Only metadata is stored (no video recordings)
- Face photos stored in database
- Configurable data retention policies
- Clear consent required for registration

## Future Enhancements

- [ ] GPU acceleration support
- [ ] Multiple camera support
- [ ] Email/SMS alerts for unauthorized detection
- [ ] Advanced analytics and reporting
- [ ] Mobile app integration
- [ ] Cloud deployment guides
- [ ] Export logs to CSV/PDF

## License

This project is provided as-is for educational and authorized security purposes only.

---

**Built with cutting-edge computer vision technology for real-time security monitoring.**

**No Docker. No complex setup. Just Python and go!**
