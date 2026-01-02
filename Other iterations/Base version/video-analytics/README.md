# Video Analytics - Face Recognition System

A production-ready real-time video analytics system with face registration, recognition, and timestamped event logging.

## Features

### Core Features
- **Face Registration**: Register faces via image upload or webcam capture
- **Real-time Recognition**: Detect and recognize faces in video streams
- **Timestamped Events**: All detections logged with precise timestamps
- **Multi-camera Support**: Process multiple camera feeds simultaneously
- **Analytics Dashboard**: View statistics, top visitors, and activity patterns
- **Person Management**: Add, view, and manage registered persons

### Technical Features
- State-of-the-art face recognition using InsightFace (99.8% accuracy)
- 512-dimensional face embeddings for superior accuracy
- Age and gender detection capabilities
- RESTful API with FastAPI
- Real-time video processing with OpenCV
- PostgreSQL database for structured data
- Redis caching for fast lookups
- Responsive web interface (HTML/CSS/JavaScript)
- Docker support for easy deployment

## Tech Stack

### Backend
- **Framework**: Python 3.9+, FastAPI
- **Face Recognition**: InsightFace (99.8% accuracy), OpenCV
- **Database**: PostgreSQL (structured data) + Redis (caching)
- **Video Processing**: OpenCV, multithreading

### Frontend
- **UI**: HTML5, CSS3, Vanilla JavaScript
- **Design**: Responsive, modern interface
- **API Integration**: Fetch API with async/await

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Web Server**: Uvicorn (ASGI)
- **Reverse Proxy**: Nginx (optional)

## Quick Start

### Option 1: Using Docker (Recommended)

```bash
# Clone the repository
cd video-analytics

# Start all services
docker-compose up -d

# Initialize database
docker-compose exec backend python backend/database/init_db.py

# Access the application
# Frontend: http://localhost or open frontend/pages/index.html
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Installation

```bash
# 1. Install PostgreSQL and Redis (see SETUP_GUIDE.md)

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 5. Initialize database
python backend/database/init_db.py

# 6. Run the system
python run.py

# 7. In another terminal, serve frontend
python -m http.server 3000 --directory frontend
# Then open: http://localhost:3000/pages/index.html
```

## Project Structure

```
video-analytics/
├── backend/                    # Python backend
│   ├── api/                   # FastAPI endpoints & schemas
│   ├── services/              # Core services (detection, registration, video)
│   ├── database/              # Models & database management
│   └── utils/                 # Configuration & helpers
├── frontend/                   # Web interface
│   ├── pages/                 # HTML pages (home, register, analytics)
│   ├── css/                   # Stylesheets
│   ├── js/                    # JavaScript (API client, utilities)
│   └── assets/                # Static assets
├── config/                     # Configuration files
│   └── config.yaml            # Main configuration
├── data/                       # Application data
│   ├── faces/                 # Registered face images
│   ├── logs/                  # Application logs
│   └── videos/                # Video archives (optional)
├── ml_pipeline/               # Model training (future)
├── docker-compose.yml         # Docker services definition
├── Dockerfile                 # Container image
├── requirements.txt           # Python dependencies
├── run.py                     # Quick start script
└── SETUP_GUIDE.md            # Detailed setup instructions
```

## Usage

### 1. Register a Person

**Via Web Interface:**
1. Navigate to "Register Face" page
2. Choose upload method (files) or webcam capture
3. Enter person details (name, email, employee ID, etc.)
4. Upload 3-5 face images from different angles
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

1. Go to "Cameras" page
2. Click "Start" on a configured camera
3. System begins real-time face detection and recognition
4. All detections are timestamped and logged automatically

### 3. View Analytics

1. Navigate to "Analytics" page
2. Select time period (1 day, 7 days, 30 days)
3. View:
   - Total detections
   - Unique visitors
   - Top visitors ranking
   - Recent activity timeline

### 4. Manage Persons

1. Go to "Persons" page
2. Search and filter registered persons
3. Click on any person to view detailed information
4. Delete or deactivate persons as needed

## Configuration

### Main Configuration (`config/config.yaml`)

```yaml
# Database
database:
  postgres:
    host: "localhost"
    port: 5432
    database: "video_analytics"
    user: "postgres"
    password: "your-password"

# Face Recognition
face_recognition:
  detection_model: "hog"        # 'hog' (CPU) or 'cnn' (GPU)
  recognition_threshold: 0.6    # Lower = stricter (0.0-1.0)

# Cameras
camera:
  sources:
    - id: "cam_01"
      url: 0                    # 0 = default webcam, or RTSP URL
      name: "Main Entrance"
      enabled: true
```

### Frontend Configuration (`frontend/js/config.js`)

```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    // ... customize as needed
};
```

## API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/persons/register` - Register new person
- `GET /api/persons` - List all persons
- `GET /api/persons/{id}` - Get person details
- `DELETE /api/persons/{id}` - Delete person
- `POST /api/detect` - Detect faces in image
- `GET /api/detections` - Get detection history
- `GET /api/analytics/summary` - Get analytics summary
- `GET /api/cameras` - List cameras
- `POST /api/cameras/{id}/start` - Start camera stream
- `POST /api/cameras/{id}/stop` - Stop camera stream

## Advanced Topics

### Performance Tuning

For faster processing:
- Use `hog` detection model (CPU-friendly)
- Increase `frame_skip` to process fewer frames
- Reduce camera resolution

For better accuracy:
- Use `cnn` detection model (requires GPU)
- Decrease `recognition_threshold`
- Register more face samples per person

### Production Deployment

1. Use environment variables for sensitive data
2. Enable HTTPS with SSL certificates
3. Set up reverse proxy (Nginx/Apache)
4. Configure firewall and security groups
5. Enable database backups
6. Set up monitoring and alerting

See `SETUP_GUIDE.md` for detailed deployment instructions.

## Troubleshooting

### Common Issues

**Database connection error:**
- Verify PostgreSQL is running
- Check credentials in config.yaml
- Ensure database exists

**Face not detected:**
- Ensure good lighting conditions
- Face should be clearly visible and frontal
- Try adjusting `upsample_times` in config

**Installation issues:**
- On Windows: Install Visual Studio Build Tools for dlib
- On Linux: Install build-essential, cmake, libboost
- See SETUP_GUIDE.md for platform-specific instructions

**Performance issues:**
- Reduce camera resolution
- Increase frame_skip value
- Use 'hog' instead of 'cnn' detection model
- Limit concurrent camera streams

For detailed troubleshooting, see `SETUP_GUIDE.md`.

## Development

### Run in Development Mode

```bash
# Backend with auto-reload
uvicorn backend.api.main:app --reload

# Frontend
python -m http.server 3000 --directory frontend
```

### Run Tests

```bash
pytest tests/
```

### Code Structure

- **Services**: Business logic and face recognition
- **API**: HTTP endpoints and request/response handling
- **Database**: Models and data persistence
- **Utils**: Configuration, helpers, utilities

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For detailed setup instructions, see `SETUP_GUIDE.md`

For questions and issues:
- Check API documentation: http://localhost:8000/docs
- Review logs: `data/logs/app.log`
- Consult SETUP_GUIDE.md troubleshooting section

---

Built with ❤️ for secure and efficient video analytics
