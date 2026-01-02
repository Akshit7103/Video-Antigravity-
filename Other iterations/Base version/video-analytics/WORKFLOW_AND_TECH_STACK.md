# Video Analytics System - Workflow & Tech Stack

## Complete Tech Stack

### Backend Technologies

#### Core Framework
- **Python 3.9+**: Main programming language
- **FastAPI**: Modern, high-performance web framework
  - Auto-generated API documentation (Swagger/OpenAPI)
  - Type hints and validation with Pydantic
  - Async/await support for better performance

#### Face Recognition & Computer Vision
- **dlib**: C++ library with Python bindings
  - Face detection algorithms (HOG and CNN)
  - 68-point facial landmark detection
  - Face recognition with deep learning (99.38% accuracy on LFW)

- **face_recognition**: Python library built on dlib
  - Simplified API for face detection
  - Face encoding (128-dimensional vectors)
  - Face comparison and matching

- **OpenCV (cv2)**: Computer vision library
  - Video capture and processing
  - Image manipulation
  - Frame-by-frame video analysis
  - Camera interfacing

#### Database & Caching
- **PostgreSQL**: Relational database
  - Stores person information
  - Detection events with timestamps
  - Camera configurations
  - Session tracking

- **SQLAlchemy**: Python ORM (Object-Relational Mapping)
  - Database models and relationships
  - Query building
  - Migration support with Alembic

- **Redis**: In-memory data store
  - Caching face encodings for fast lookup
  - Session management
  - Real-time data storage

#### Web Server & Deployment
- **Uvicorn**: ASGI server
  - High-performance async server
  - WebSocket support
  - Auto-reload in development

- **Docker**: Containerization
  - Isolated environments
  - Easy deployment
  - Consistent across platforms

- **Docker Compose**: Multi-container orchestration
  - PostgreSQL container
  - Redis container
  - Backend container
  - Nginx container (optional)

#### Additional Python Libraries
- **Pillow (PIL)**: Image processing
- **NumPy**: Numerical operations and array handling
- **Pydantic**: Data validation and settings management
- **python-multipart**: Form data handling
- **loguru**: Advanced logging
- **PyYAML**: Configuration file parsing
- **python-dotenv**: Environment variable management

---

### Frontend Technologies

#### Core Web Technologies
- **HTML5**: Structure and markup
  - Semantic elements
  - Form handling
  - Canvas for webcam capture

- **CSS3**: Styling and layout
  - CSS Variables for theming
  - Flexbox and Grid for responsive layouts
  - Animations and transitions
  - Media queries for mobile responsiveness

- **Vanilla JavaScript (ES6+)**: Client-side logic
  - Fetch API for HTTP requests
  - Async/await for asynchronous operations
  - Modules for code organization
  - DOM manipulation
  - Event handling

#### Browser APIs Used
- **MediaDevices API**: Webcam access
- **Canvas API**: Image capture from video
- **Fetch API**: HTTP requests to backend
- **File API**: Image file handling
- **FormData API**: File uploads
- **Local Storage**: Client-side data (optional)

---

### Infrastructure & DevOps

- **Git**: Version control
- **Nginx**: Reverse proxy and static file serving (optional)
- **PostgreSQL Client**: Database management
- **Redis CLI**: Cache management

---

## System Workflow

### 1. Face Registration Workflow

```
User Action → Frontend → Backend → Database
```

**Detailed Steps:**

1. **User Opens Registration Page**
   - Browser loads `register.html`
   - JavaScript initializes form handlers
   - User chooses upload or webcam method

2. **Image Collection (Two Methods)**

   **Method A: Upload Images**
   - User selects 3-5 images from computer
   - JavaScript validates file types (JPEG, PNG)
   - Creates image previews using FileReader API
   - Stores files in FormData object

   **Method B: Webcam Capture**
   - JavaScript requests camera access via `navigator.mediaDevices.getUserMedia()`
   - Video stream displayed in `<video>` element
   - User clicks "Capture" 5 times
   - Each frame captured to `<canvas>`
   - Canvas converts to Blob → File object
   - Files stored in array

3. **Form Submission**
   - User fills personal details (name, email, employee_id, etc.)
   - Clicks "Register Person"
   - JavaScript prevents default form submission
   - Creates FormData with all fields and images
   - Sends POST request to `/api/persons/register`

4. **Backend Processing**
   ```
   API Endpoint (main.py)
        ↓
   Read uploaded images
        ↓
   Convert to numpy arrays (OpenCV)
        ↓
   FaceDetectionService.detect_and_encode()
        ↓
   For each image:
     - Detect face location (dlib/face_recognition)
     - Generate 128-D face encoding
     - Assess quality (size, brightness, aspect ratio)
     - Filter low-quality images
        ↓
   Calculate average encoding (multiple samples)
        ↓
   FaceRegistrationService.register_from_images()
        ↓
   Save images to data/faces/PersonName_Timestamp/
        ↓
   Serialize face encoding (pickle)
        ↓
   Create Person database record
        ↓
   Commit to PostgreSQL
        ↓
   Reload VideoProcessor with new person
        ↓
   Return success response
   ```

5. **Response Handling**
   - Frontend receives JSON response
   - Shows success message
   - Redirects to persons list page
   - New person now appears in system

---

### 2. Real-Time Face Recognition Workflow

```
Camera → Video Stream → Frame Processing → Face Detection →
Face Recognition → Database Logging → Frontend Updates
```

**Detailed Steps:**

1. **Camera Initialization**
   - User navigates to Cameras page
   - Clicks "Start" on a camera
   - Frontend sends POST to `/api/cameras/{id}/start`

2. **Backend Camera Setup**
   ```
   API receives start request
        ↓
   VideoProcessor initialized with known persons
        ↓
   Load all active Person records from database
        ↓
   Deserialize face encodings from database
        ↓
   Create CameraManager instance
        ↓
   Start new thread for camera stream
        ↓
   OpenCV opens video capture:
     - cv2.VideoCapture(0) for webcam
     - cv2.VideoCapture(rtsp_url) for IP camera
   ```

3. **Continuous Frame Processing Loop**
   ```
   While camera is active:
     ↓
   Read frame from camera (cv2.VideoCapture.read())
     ↓
   Check frame_skip setting (process every Nth frame)
     ↓
   Convert BGR to RGB (OpenCV uses BGR)
     ↓
   FaceDetectionService.detect_and_encode(frame)
     ↓
   For each detected face:
     ├─ Get face location (top, right, bottom, left)
     ├─ Generate face encoding (128-D vector)
     └─ Compare with known encodings
        ↓
   Face matching process:
     ├─ Calculate Euclidean distance to all known faces
     ├─ Find minimum distance
     ├─ Check if distance < threshold (0.6)
     └─ If match found:
          ├─ Get Person from database
          ├─ Check deduplication window (avoid spam)
          ├─ If not duplicate:
          │    ├─ Create Detection record
          │    ├─ Save to PostgreSQL with timestamp
          │    ├─ Update person's last_seen
          │    └─ Trigger callback (optional WebSocket)
          └─ Return detection result
     ↓
   Continue to next frame
   ```

4. **Detection Storage**
   ```
   Detection record contains:
     - person_id (foreign key to Person)
     - timestamp (precise datetime)
     - camera_id (which camera)
     - confidence (1 - distance)
     - face_distance (Euclidean distance)
     - bbox coordinates (x, y, width, height)
     - snapshot_path (optional face image)
     ↓
   Stored in PostgreSQL detections table
   ```

5. **Deduplication Logic**
   ```
   If person detected:
     ↓
   Check last detection time for this person + camera
     ↓
   If < 30 seconds ago (configurable):
     └─ Skip logging (same detection)
   Else:
     └─ Log new detection event
   ```

---

### 3. Analytics Dashboard Workflow

```
User Request → API Query → Database Aggregation →
JSON Response → Frontend Rendering
```

**Detailed Steps:**

1. **Page Load**
   - User navigates to `analytics.html`
   - JavaScript loads on DOMContentLoaded
   - Calls `loadAnalytics(7)` for 7-day period

2. **API Request**
   ```
   GET /api/analytics/summary?days=7
   ```

3. **Backend Processing**
   ```
   Calculate date range (now - 7 days to now)
     ↓
   Query database:
     ├─ COUNT(detections) WHERE timestamp >= start_date
     ├─ COUNT(DISTINCT person_id)
     ├─ COUNT(persons WHERE is_active=true)
     ├─ COUNT(cameras WHERE is_active=true)
     └─ TOP 10 persons by detection count
        ↓
   Aggregate results
        ↓
   Return JSON response
   ```

4. **Data Aggregation Queries**
   ```sql
   -- Total detections
   SELECT COUNT(*) FROM detections
   WHERE timestamp >= '2025-01-13' AND timestamp <= '2025-01-20';

   -- Unique persons
   SELECT COUNT(DISTINCT person_id) FROM detections
   WHERE timestamp >= '2025-01-13';

   -- Top visitors
   SELECT p.name, COUNT(d.id) as count
   FROM persons p
   JOIN detections d ON p.id = d.person_id
   WHERE d.timestamp >= '2025-01-13'
   GROUP BY p.id, p.name
   ORDER BY count DESC
   LIMIT 10;
   ```

5. **Frontend Rendering**
   - Receive JSON data
   - Update stat cards (total detections, unique visitors, etc.)
   - Render top visitors table with percentages
   - Create bar chart visualizations
   - Format timestamps for display

6. **Auto-Refresh**
   ```javascript
   setInterval(() => {
     loadAnalytics(currentPeriod);
   }, 30000); // Refresh every 30 seconds
   ```

---

### 4. Person Management Workflow

**View All Persons:**
```
Frontend → GET /api/persons → Database Query →
Return JSON → Render Grid
```

**View Person Details:**
```
Click Person Card → GET /api/persons/{id} →
Load from Database → Show Modal with Details
```

**Delete Person:**
```
Click Delete → Confirm Dialog → DELETE /api/persons/{id} →
Set is_active=false → Reload VideoProcessor → Refresh List
```

**Search/Filter:**
```
User types in search → JavaScript filters client-side →
Re-render filtered results
```

---

## Data Flow Architecture

### Complete Request-Response Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      WEB BROWSER (Client)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    HTML      │  │     CSS      │  │  JavaScript  │      │
│  │   Pages      │  │   Styles     │  │   API Calls  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/HTTPS
                            │ (Fetch API)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND (Server)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Layer (main.py)                     │   │
│  │  - Route handlers                                    │   │
│  │  - Request validation (Pydantic)                     │   │
│  │  - Response formatting                               │   │
│  └────────────┬─────────────────────────────────────────┘   │
│               │                                              │
│  ┌────────────▼─────────────────────────────────────────┐   │
│  │         Services Layer                               │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │   │
│  │  │ Face         │  │ Face         │  │ Video     │  │   │
│  │  │ Detection    │  │ Registration │  │ Processor │  │   │
│  │  └──────────────┘  └──────────────┘  └───────────┘  │   │
│  └────────────┬─────────────────────────────────────────┘   │
│               │                                              │
│  ┌────────────▼─────────────────────────────────────────┐   │
│  │         ML/CV Layer                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │   │
│  │  │ dlib         │  │ OpenCV       │  │ NumPy     │  │   │
│  │  │ (face rec)   │  │ (video)      │  │ (arrays)  │  │   │
│  │  └──────────────┘  └──────────────┘  └───────────┘  │   │
│  └────────────┬─────────────────────────────────────────┘   │
│               │                                              │
│  ┌────────────▼─────────────────────────────────────────┐   │
│  │         Database Layer                               │   │
│  │  - SQLAlchemy ORM                                    │   │
│  │  - Connection pooling                                │   │
│  │  - Query building                                    │   │
│  └────────────┬─────────────────────────────────────────┘   │
└───────────────┼──────────────────────────────────────────────┘
                │
       ┌────────┴────────┐
       │                 │
       ▼                 ▼
┌──────────────┐   ┌──────────────┐
│  PostgreSQL  │   │    Redis     │
│   Database   │   │    Cache     │
│              │   │              │
│ - Persons    │   │ - Encodings  │
│ - Detections │   │ - Sessions   │
│ - Cameras    │   │              │
└──────────────┘   └──────────────┘
```

---

## Key Algorithms & Techniques

### 1. Face Detection (HOG - Histogram of Oriented Gradients)
```
Input: RGB Image
  ↓
Convert to grayscale
  ↓
Calculate gradients (edge detection)
  ↓
Divide into small cells (8x8 pixels)
  ↓
Create histogram of gradient directions
  ↓
Normalize across blocks
  ↓
Use trained classifier to find face patterns
  ↓
Output: Bounding boxes [(top, right, bottom, left), ...]
```

### 2. Face Recognition (Deep Neural Network)
```
Input: Face image (cropped to face region)
  ↓
Align face (rotate to standard position)
  ↓
Pass through ResNet-based neural network
  ↓
Output: 128-dimensional vector (face encoding)
  ↓
This vector uniquely represents the face
```

### 3. Face Matching (Euclidean Distance)
```
Known face encoding: [0.1, 0.5, -0.3, ..., 0.2] (128 values)
Unknown face encoding: [0.2, 0.4, -0.2, ..., 0.3] (128 values)
  ↓
Calculate Euclidean distance:
  distance = sqrt(sum((known[i] - unknown[i])^2 for i in 0..127))
  ↓
If distance < 0.6:
  → Same person (MATCH)
Else:
  → Different person (NO MATCH)
```

### 4. Quality Assessment
```
Face bounding box: (x, y, width, height)
  ↓
Calculate metrics:
  - Face size (area relative to image)
  - Aspect ratio (should be ~1:1 for frontal face)
  - Brightness (average pixel value)
  - Sharpness (edge detection)
  ↓
Quality score = weighted sum of metrics
  ↓
If score > 0.5:
  → Good quality, use for registration
Else:
  → Poor quality, reject
```

---

## Performance Optimizations

### 1. Frame Skipping
```python
frame_count = 0
while capturing:
    frame_count += 1
    if frame_count % frame_skip != 0:
        continue  # Skip this frame
    # Process frame
```

### 2. Redis Caching
```python
# Check cache first
encoding = redis.get(f"person:{person_id}:encoding")
if not encoding:
    # Load from database
    encoding = db.query(Person).get(person_id).face_encoding
    # Cache for future
    redis.set(f"person:{person_id}:encoding", encoding)
```

### 3. Database Indexing
```sql
CREATE INDEX idx_detections_timestamp ON detections(timestamp);
CREATE INDEX idx_detections_person_id ON detections(person_id);
CREATE INDEX idx_detections_camera_id ON detections(camera_id);
```

### 4. Connection Pooling
```python
# SQLAlchemy connection pool
engine = create_engine(
    database_url,
    pool_size=10,      # Keep 10 connections
    max_overflow=20    # Allow 20 more if needed
)
```

---

## Security Measures

1. **Face Encoding Storage**: Stored as encrypted binary (pickle serialization)
2. **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
3. **Input Validation**: Pydantic validates all API inputs
4. **CORS Configuration**: Controlled cross-origin access
5. **Environment Variables**: Sensitive data in .env file
6. **Password Hashing**: Database passwords never in code
7. **File Upload Validation**: Only images accepted, size limits enforced

---

## Scalability Considerations

### Horizontal Scaling
- **Multiple Backend Instances**: Load balancer distributes requests
- **Separate Camera Processors**: Each camera on different server
- **Database Replication**: Master-slave PostgreSQL setup

### Vertical Scaling
- **GPU Acceleration**: Use CNN model with CUDA
- **More RAM**: Cache more face encodings
- **Faster CPU**: Quicker frame processing

### Optimization Strategies
- **Reduce Resolution**: Lower camera resolution (720p instead of 1080p)
- **Increase Frame Skip**: Process fewer frames per second
- **Batch Processing**: Process multiple faces in one batch
- **Async Operations**: Use async/await for I/O operations

---

This is the complete tech stack and workflow for the Video Analytics System! The system uses modern, production-ready technologies and follows best practices for performance, security, and scalability.
