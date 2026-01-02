# Video Analytics - Face Recognition System

A production-ready real-time video analytics system with face registration, recognition, and timestamped event logging.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Security & Authentication](#security--authentication)
- [Usage Guide](#usage-guide)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

---

## Features

### Core Features
- **Face Registration**: Register faces via image upload or webcam capture
- **Real-time Recognition**: Detect and recognize faces in video streams with 99.8% accuracy
- **Timestamped Events**: All detections logged with precise timestamps and deduplication
- **Multi-camera Support**: Process multiple camera feeds simultaneously (RTSP/USB)
- **Analytics Dashboard**: View statistics, top visitors, and activity patterns
- **Person Management**: Full CRUD operations for registered persons
- **JWT Authentication**: Secure API access with token-based authentication
- **User Management**: Registration, login, profile management, password change

### Technical Features
- State-of-the-art face recognition using **InsightFace** (99.8% accuracy)
- 512-dimensional face embeddings for superior accuracy
- Age and gender detection capabilities
- RESTful API with **FastAPI** and auto-generated documentation
- Real-time video processing with **OpenCV**
- **PostgreSQL** database for structured data
- **Redis** caching for fast lookups
- Responsive web interface (HTML/CSS/JavaScript)
- **Docker** support for easy deployment
- Comprehensive error handling with custom exceptions
- Rate limiting for API protection
- Quality assessment for face registration
- Session tracking with entry/exit timestamps

---

## Tech Stack

### Backend
- **Framework**: Python 3.9+, FastAPI 0.104.1
- **Face Recognition**: InsightFace 0.7.3 (99.8% accuracy), OpenCV 4.8.1
- **Database**: PostgreSQL 14 + SQLAlchemy ORM
- **Cache**: Redis 7
- **Authentication**: JWT tokens with bcrypt password hashing
- **Validation**: Pydantic 2.5.0
- **Server**: Uvicorn (ASGI)
- **Logging**: Loguru with rotation

### Frontend
- **UI**: HTML5, CSS3, Vanilla JavaScript
- **Design**: Responsive, modern interface
- **API Integration**: Fetch API with async/await

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Database Migrations**: Alembic (ready to use)
- **Deployment**: Local, Docker, Cloud-ready

---

## Quick Start

### Option 1: Using Docker (Recommended)

```bash
# Navigate to project directory
cd video-analytics-copy

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials

# Start all services
docker-compose up -d

# Access the application
# Frontend: Open frontend/pages/index.html in browser
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs

# Default login credentials:
# Username: admin
# Password: admin123
# ⚠️ CHANGE IMMEDIATELY AFTER FIRST LOGIN!
```

### Option 2: Local Installation

```bash
# 1. Install PostgreSQL 14+ and Redis 7+

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your database credentials and secrets

# 5. Start the backend (database initializes automatically)
python run.py

# 6. In another terminal, serve frontend
cd frontend
python -m http.server 3000
# Then open: http://localhost:3000/pages/index.html
```

### First Time Setup

On first run, the system automatically:
- Creates all database tables
- Initializes default admin user (admin/admin123)
- Sets up logging directory
- Verifies InsightFace models

---

## Project Structure

```
video-analytics-copy/
├── backend/                     # Python FastAPI backend
│   ├── api/                    # HTTP endpoints & schemas
│   │   ├── main.py            # FastAPI application (450+ lines)
│   │   ├── schemas.py         # Pydantic request/response models
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── auth_schemas.py    # Auth data models
│   │   └── exceptions.py      # Custom exception handling
│   ├── services/               # Core business logic (1000+ lines)
│   │   ├── insightface_detection.py  # AI face detection (99.8% accuracy)
│   │   ├── face_registration.py      # Person registration logic
│   │   ├── video_processor.py        # Real-time video processing
│   │   ├── auth_service.py           # JWT & password management
│   │   └── duplicate_check.py        # Prevent duplicate registrations
│   ├── database/               # Data persistence
│   │   ├── models.py          # SQLAlchemy ORM models (User, Person, Detection, etc.)
│   │   ├── connection.py      # DB/Redis connection management
│   │   └── init_db.py         # Database initialization script
│   └── utils/                  # Helpers & configuration
│       ├── config.py          # YAML config loader
│       └── helpers.py         # Utility functions
├── frontend/                    # Web interface
│   ├── pages/                  # HTML pages (index, register, analytics, cameras, persons)
│   ├── js/                     # JavaScript modules (api, register, analytics, etc.)
│   ├── css/                    # Stylesheets
│   └── assets/                 # Static assets
├── config/                      # Configuration management
│   ├── config.yaml             # Main configuration
│   ├── config.dev.yaml         # Development settings
│   └── config.prod.yaml        # Production settings
├── data/                        # Application data (auto-created)
│   ├── faces/                  # Registered face images
│   ├── logs/                   # Application logs
│   └── videos/                 # Video archives (optional)
├── docker-compose.yml           # Multi-service orchestration (PostgreSQL, Redis, Backend)
├── Dockerfile                   # Container image definition
├── requirements.txt             # Python dependencies
├── run.py                       # Quick start script
├── .env.example                 # Environment template
└── README.md                    # This file
```

---

## Configuration

### Environment Variables (`.env`)

**CRITICAL**: Never commit the `.env` file. Use `.env.example` as template.

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=video_analytics
DB_USER=postgres
DB_PASSWORD=your-secure-database-password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Security
JWT_SECRET=generate-a-long-random-64-character-secret-string-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=43200

# API Configuration
API_KEY=your-api-key-if-needed

# Environment
CONFIG_ENV=development  # Change to 'production' for production
```

### Application Configuration (`config/config.yaml`)

```yaml
# Face Recognition Settings
face_recognition:
  detection_model: "buffalo_l"    # Options: buffalo_l (accurate), buffalo_m (balanced), buffalo_s (fast)
  recognition_threshold: 0.5      # Similarity threshold (0.0-1.0, lower = stricter)
  registration:
    min_samples: 3                # Minimum face samples required
    quality_threshold: 0.6        # Face quality threshold

# Performance Settings
performance:
  use_gpu: false                  # Enable GPU acceleration (requires CUDA)
  frame_skip: 2                   # Process every Nth frame (higher = faster, lower accuracy)
  max_workers: 4                  # Thread pool size

# Camera Configuration
cameras:
  sources:
    - id: "cam_01"
      url: 0                      # 0 = default webcam, or "rtsp://..." for IP camera
      name: "Main Entrance"
      enabled: true
      resolution: [640, 480]
      fps: 30

# Logging
logging:
  level: "INFO"                   # DEBUG, INFO, WARNING, ERROR
  rotation: "500 MB"              # Log file rotation size
  retention: "30 days"            # Log retention period

# Detection Settings
detection:
  deduplication_window: 30        # Seconds to suppress duplicate detections
  save_snapshots: true            # Save detection snapshots
  confidence_threshold: 0.7       # Minimum confidence for valid detection

# Security
security:
  rate_limit: 30                  # Requests per minute
  cors_origins:
    - "http://localhost"
    - "http://localhost:3000"
```

### Environment-Specific Configs

- **Development**: Uses `config/config.dev.yaml` (merged with config.yaml)
- **Production**: Uses `config/config.prod.yaml` (merged with config.yaml)

Set environment: `export CONFIG_ENV=production` (default: development)

---

## API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login and get JWT token | No |
| GET | `/api/auth/me` | Get current user info | Yes |
| PUT | `/api/auth/me` | Update user profile | Yes |
| POST | `/api/auth/change-password` | Change password | Yes |

### Person Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/persons/register` | Register new person with face images | Yes |
| GET | `/api/persons` | List all persons (with search/filter) | Yes |
| GET | `/api/persons/{id}` | Get person details | Yes |
| PUT | `/api/persons/{id}` | Update person information | Yes |
| DELETE | `/api/persons/{id}` | Deactivate person (soft delete) | Yes |

### Face Detection & Recognition

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/detect` | Detect and recognize faces in image | Yes |
| GET | `/api/detections` | Get detection history (with filters) | Yes |

### Analytics

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/analytics/summary` | Get analytics summary (time-filtered) | Yes |

### Camera Control

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/cameras` | List all cameras and status | Yes |
| POST | `/api/cameras/{id}/start` | Start camera stream | Yes |
| POST | `/api/cameras/{id}/stop` | Stop camera stream | Yes |

### System

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/health` | Health check (DB, face detector, API status) | No |

### Example API Calls

**1. Login to get JWT token:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**2. Register a person:**
```bash
curl -X POST "http://localhost:8000/api/persons/register" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "name=John Doe" \
  -F "email=john@example.com" \
  -F "employee_id=EMP001" \
  -F "images=@photo1.jpg" \
  -F "images=@photo2.jpg" \
  -F "images=@photo3.jpg"
```

**3. Get analytics:**
```bash
curl -X GET "http://localhost:8000/api/analytics/summary?days=7" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Security & Authentication

### Implemented Security Features

✅ **JWT Authentication**: Token-based auth with configurable expiration
✅ **Password Security**: Bcrypt hashing with salt
✅ **CORS Protection**: Restricted to specific origins
✅ **Rate Limiting**: Prevents brute force attacks (30 req/min)
✅ **Input Validation**: Pydantic models validate all inputs
✅ **Error Handling**: No sensitive data exposed in errors
✅ **Configuration Security**: Secrets in .env, not in code
✅ **Database Security**: SQL injection protection via SQLAlchemy ORM

### Default Admin Account

On first startup, a default admin account is created:
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **CRITICAL**: Change this password immediately after first login!

```bash
curl -X POST "http://localhost:8000/api/auth/change-password" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"old_password": "admin123", "new_password": "new-secure-password"}'
```

### Custom Exception Handling

The system includes comprehensive error handling:

- `AuthenticationException` - 401 Unauthorized
- `AuthorizationException` - 403 Forbidden
- `NotFoundException` - 404 Not Found
- `ValidationException` - 422 Validation Error
- `DuplicateResourceException` - 409 Conflict
- `FaceDetectionException` - Face detection errors
- `DatabaseException` - Database errors
- `FileProcessingException` - File upload errors

All errors return structured JSON responses:
```json
{
  "error": "ExceptionName",
  "message": "User-friendly error message",
  "path": "/api/endpoint",
  "details": [...]
}
```

---

## Usage Guide

### 1. Register a Person

**Via Web Interface:**
1. Navigate to "Register Face" page
2. Choose upload method (file upload or webcam capture)
3. Enter person details:
   - Name, Email, Employee ID
   - Phone, Department, Designation
4. Upload 3-5 face images from different angles
5. Click "Register Person"

**Tips for best results:**
- Use well-lit, clear face images
- Include different angles (front, left, right)
- Ensure face is clearly visible
- Minimum 3 samples recommended, 5+ for best accuracy

### 2. Start Camera Recognition

1. Go to "Cameras" page
2. Click "Start" on a configured camera
3. System begins real-time face detection and recognition
4. All detections are timestamped and logged automatically
5. Deduplication prevents spam detections (configurable window)

### 3. View Analytics

1. Navigate to "Analytics" page
2. Select time period (1 day, 7 days, 30 days)
3. View:
   - Total detections
   - Unique visitors
   - Top visitors ranking
   - Recent activity timeline
   - Per-camera statistics

### 4. Manage Persons

1. Go to "Persons" page
2. Search and filter registered persons
3. Click on any person to view:
   - Profile details
   - Registered face samples
   - Detection history
   - Last seen timestamp
4. Update or deactivate persons as needed

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] **Change default admin password**
- [ ] **Generate new JWT secret** (64+ characters random string)
- [ ] **Update database password** to strong password
- [ ] **Configure CORS origins** to your production domain
- [ ] **Set CONFIG_ENV=production** environment variable
- [ ] **Enable HTTPS/SSL** (never use HTTP in production)
- [ ] **Configure firewall** and security groups
- [ ] **Set up database backups** (automated)
- [ ] **Configure monitoring** and alerting
- [ ] **Review and update** rate limits
- [ ] **Test all endpoints** with production config

### Production Configuration

**1. Update `.env` for production:**
```env
DB_HOST=your-production-db-host
DB_PASSWORD=strong-production-password
JWT_SECRET=generate-new-64-character-random-secret
CONFIG_ENV=production
```

**2. Update CORS in `backend/api/main.py`:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**3. Use production config:**
```bash
export CONFIG_ENV=production
python run.py
```

**4. Deploy with Docker:**
```bash
# Production docker-compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Recommended Production Setup

```
                    Internet
                       ↓
                 HTTPS (SSL/TLS)
                       ↓
              Nginx Reverse Proxy
              (Load Balancing)
                       ↓
         ┌──────────────┴──────────────┐
         ↓                             ↓
   FastAPI Instance 1          FastAPI Instance 2
         ↓                             ↓
         └──────────────┬──────────────┘
                        ↓
            PostgreSQL (Primary-Replica)
                        +
                   Redis Cluster
```

### Performance Tuning

**For faster processing:**
- Use `buffalo_s` model (sacrifices some accuracy)
- Increase `frame_skip` to process fewer frames
- Reduce camera resolution
- Enable GPU if available (`use_gpu: true`)

**For better accuracy:**
- Use `buffalo_l` model (requires more resources)
- Decrease `recognition_threshold`
- Register more face samples per person (5-7 recommended)
- Use higher camera resolution

### Scaling Considerations

- **Horizontal Scaling**: Deploy multiple FastAPI instances behind load balancer
- **Database**: Use PostgreSQL replication (primary-replica)
- **Cache**: Use Redis cluster for high availability
- **Storage**: Use object storage (S3, MinIO) for face images in distributed setup
- **Monitoring**: Implement Prometheus + Grafana for metrics

---

## Troubleshooting

### Common Issues

**1. Database connection error**
```
Error: Could not connect to database
```
**Solution:**
- Verify PostgreSQL is running: `systemctl status postgresql` (Linux) or check Windows services
- Check credentials in `.env` file
- Ensure database exists: `createdb video_analytics`
- Verify network connectivity to DB host

**2. Face not detected**
```
No faces detected in image
```
**Solution:**
- Ensure good lighting conditions
- Face should be clearly visible and frontal
- Minimum face size: 80x80 pixels
- Try different images or adjust camera angle
- Check `quality_threshold` in config (lower for lenient detection)

**3. Authentication failed**
```
401 Unauthorized
```
**Solution:**
- Verify JWT token is included in `Authorization: Bearer TOKEN` header
- Check token expiration (default: 30 days)
- Ensure `JWT_SECRET` in `.env` matches the one used to generate token
- Try logging in again to get fresh token

**4. InsightFace model download issues**
```
Model download failed
```
**Solution:**
- Ensure internet connectivity
- Models auto-download on first run (requires ~150MB)
- Manual download: Check InsightFace documentation
- Verify disk space availability

**5. Performance issues (slow detection)**
```
Low FPS, laggy video
```
**Solution:**
- Increase `frame_skip` value (process fewer frames)
- Reduce camera resolution in config
- Use `buffalo_s` instead of `buffalo_l` model
- Limit concurrent camera streams
- Consider GPU acceleration

**6. Port already in use**
```
Error: Address already in use (port 8000)
```
**Solution:**
```bash
# Find process using port
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in run.py
```

**7. Module import errors**
```
ModuleNotFoundError: No module named 'insightface'
```
**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Debug Mode

Enable debug logging in `config/config.yaml`:
```yaml
logging:
  level: "DEBUG"
```

Check logs at: `data/logs/app.log`

### Health Check

Verify system status:
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "face_detector": "initialized",
  "api": "running"
}
```

---

## Development

### Run in Development Mode

```bash
# Backend with auto-reload
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
python -m http.server 3000
```

### Database Migrations (Alembic)

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# With coverage
pytest --cov=backend tests/
```

---

## Database Schema

### Core Models

1. **User** - System authentication
   - id, username, email, hashed_password
   - full_name, is_active, is_superuser
   - created_at, updated_at, last_login

2. **Person** - Registered individuals
   - id, name, email, employee_id, phone
   - department, designation
   - face_encodings (512-D binary)
   - is_active, created_at, updated_at

3. **Detection** - Face detection events
   - id, person_id, camera_id, timestamp
   - confidence, bounding_box
   - snapshot_path

4. **Camera** - Camera configurations
   - id, name, url, resolution, fps
   - is_active, status

5. **Session** - Entry/exit tracking
   - id, person_id, camera_id
   - entry_time, exit_time, duration

6. **SystemLog** - Application logs
7. **Alert** - System notifications

**Relationships:**
- Person ↔ Detection (one-to-many)
- Camera ↔ Detection (one-to-many)
- Person ↔ Session (one-to-many)

---

## License

MIT License - Free for commercial and personal use.

---

## Support

**Documentation:**
- This README
- API Documentation: http://localhost:8000/docs

**Logs:**
- Application logs: `data/logs/app.log`

**Issues:**
- Check GitHub issues or create new issue

---

**Built for secure and efficient video analytics** | Production-ready | 99.8% Accuracy | Real-time Processing
