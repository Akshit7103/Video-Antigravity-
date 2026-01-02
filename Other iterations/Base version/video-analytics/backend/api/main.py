"""
Main FastAPI application
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
import cv2
import numpy as np
from pathlib import Path
import io
from loguru import logger

from ..database import (
    init_database,
    get_db,
    get_redis,
    Person,
    Detection,
    Camera,
    SystemLog
)
from ..services import (
    FaceRegistrationService,
    VideoProcessor,
    CameraManager
)
from ..services.insightface_detection import InsightFaceDetectionService
from ..utils import (
    load_config,
    get_storage_paths,
    get_database_url,
    get_redis_url,
    deserialize_encoding
)

from .schemas import (
    PersonCreate,
    PersonResponse,
    DetectionResponse,
    CameraResponse,
    AnalyticsResponse,
    RegisterResponse
)


# Initialize FastAPI app
app = FastAPI(
    title="Video Analytics API",
    description="Face recognition and video analytics system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
config = None
face_detector = None
registration_service = None
video_processor = None
camera_manager = None
storage_paths = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global config, face_detector, registration_service, video_processor, camera_manager, storage_paths

    logger.info("Starting Video Analytics API...")

    # Load configuration
    config = load_config()

    # Initialize database
    db_url = get_database_url(config)
    redis_url = get_redis_url(config)
    init_database(db_url, redis_url)

    # Get storage paths
    storage_paths = get_storage_paths(config)

    # Initialize InsightFace service
    logger.info("Using InsightFace engine")
    face_detector = InsightFaceDetectionService(
        detection_model=config['face_recognition']['detection_model'],
        use_gpu=config['performance'].get('use_gpu', False)
    )

    registration_service = FaceRegistrationService(
        face_detector=face_detector,
        storage_path=storage_paths['faces']
    )

    # Mount static files for serving images
    app.mount("/static", StaticFiles(directory=str(storage_paths['faces'].parent)), name="static")

    logger.success("Video Analytics API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Video Analytics API...")

    if camera_manager:
        camera_manager.stop_all()

    logger.success("Video Analytics API shutdown complete")


# ==================== Person Management ====================

@app.post("/api/persons/register", response_model=RegisterResponse)
async def register_person(
    name: str = Form(...),
    email: Optional[str] = Form(None),
    employee_id: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    designation: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Register a new person with face images

    Args:
        name: Person's name (required)
        email: Email address
        employee_id: Employee ID
        phone: Phone number
        department: Department
        designation: Job designation
        notes: Additional notes
        images: Face images (min 1, recommended 5+)

    Returns:
        Registration result with person details
    """
    try:
        logger.info(f"Registering person: {name}")

        # Check if email or employee_id already exists
        if email:
            existing = db.query(Person).filter(Person.email == email).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already registered")

        if employee_id:
            existing = db.query(Person).filter(Person.employee_id == employee_id).first()
            if existing:
                raise HTTPException(status_code=400, detail="Employee ID already registered")

        # Save uploaded images temporarily
        temp_paths = []
        for idx, image in enumerate(images):
            # Read image
            contents = await image.read()
            nparr = np.frombuffer(contents, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                logger.warning(f"Could not decode image {idx}")
                continue

            # Convert to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Save temporarily
            temp_path = storage_paths['faces'] / f"temp_{name}_{idx}.jpg"
            cv2.imwrite(str(temp_path), img)
            temp_paths.append(str(temp_path))

        if not temp_paths:
            raise HTTPException(status_code=400, detail="No valid images provided")

        # Register person
        person = registration_service.register_from_images(
            name=name,
            image_paths=temp_paths,
            email=email,
            employee_id=employee_id,
            phone=phone,
            department=department,
            designation=designation,
            notes=notes
        )

        if not person:
            raise HTTPException(status_code=400, detail="Failed to register person. No valid faces found.")

        # Add to database
        db.add(person)
        db.commit()
        db.refresh(person)

        # Clean up temp files
        for path in temp_paths:
            Path(path).unlink(missing_ok=True)

        # Reload video processor if running
        if video_processor:
            persons = db.query(Person).filter(Person.is_active == True).all()
            video_processor.reload_persons(persons)

        logger.success(f"Person registered: {name} (ID: {person.id})")

        return RegisterResponse(
            success=True,
            message=f"Successfully registered {name}",
            person_id=person.id,
            person_name=person.name
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering person: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/persons", response_model=List[PersonResponse])
async def get_persons(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get list of registered persons"""
    query = db.query(Person)

    if active_only:
        query = query.filter(Person.is_active == True)

    persons = query.offset(skip).limit(limit).all()

    return [PersonResponse.from_orm(p) for p in persons]


@app.get("/api/persons/{person_id}", response_model=PersonResponse)
async def get_person(person_id: int, db: Session = Depends(get_db)):
    """Get person by ID"""
    person = db.query(Person).filter(Person.id == person_id).first()

    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    return PersonResponse.from_orm(person)


@app.put("/api/persons/{person_id}")
async def update_person(
    person_id: int,
    update_data: dict,
    db: Session = Depends(get_db)
):
    """Update person details"""
    person = db.query(Person).filter(Person.id == person_id).first()

    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    # Update fields if provided in the request body
    if 'name' in update_data and update_data['name']:
        person.name = update_data['name']
    if 'email' in update_data:
        person.email = update_data['email']
    if 'employee_id' in update_data:
        person.employee_id = update_data['employee_id']
    if 'phone' in update_data:
        person.phone = update_data['phone']
    if 'department' in update_data:
        person.department = update_data['department']
    if 'designation' in update_data:
        person.designation = update_data['designation']
    if 'notes' in update_data:
        person.notes = update_data['notes']

    db.commit()
    db.refresh(person)

    logger.info(f"Person updated: {person.name} (ID: {person.id})")

    return {"success": True, "message": f"Person {person.name} updated successfully"}


@app.delete("/api/persons/{person_id}")
async def delete_person(person_id: int, db: Session = Depends(get_db)):
    """Delete person (soft delete - marks as inactive)"""
    person = db.query(Person).filter(Person.id == person_id).first()

    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    person.is_active = False
    db.commit()

    # Reload video processor
    if video_processor:
        persons = db.query(Person).filter(Person.is_active == True).all()
        video_processor.reload_persons(persons)

    return {"success": True, "message": f"Person {person.name} deactivated"}


# ==================== Detection & Recognition ====================

@app.post("/api/detect", response_model=List[DetectionResponse])
async def detect_faces(
    image: UploadFile = File(...),
    camera_id: str = Form("unknown"),
    save_detection: bool = Form(True),
    db: Session = Depends(get_db)
):
    """
    Detect and recognize faces in an uploaded image

    Args:
        image: Image file
        camera_id: Camera identifier
        save_detection: Whether to save detections to database

    Returns:
        List of detected persons
    """
    try:
        # Read image
        contents = await image.read()
        logger.info(f"Received image, size: {len(contents)} bytes")

        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        logger.info(f"Image decoded successfully, shape: {img.shape}")

        # Convert to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Get known persons
        persons = db.query(Person).filter(Person.is_active == True).all()
        logger.info(f"Found {len(persons)} known persons in database")

        # Create temporary processor with frame_skip=1 for API calls
        processor = VideoProcessor(
            face_detector=face_detector,
            known_persons=persons,
            recognition_threshold=config['face_recognition']['recognition_threshold'],
            frame_skip=1  # Process every frame for API calls
        )

        # Process frame
        logger.info(f"Processing frame for camera: {camera_id}")
        detections = processor.process_frame(img, camera_id)
        logger.info(f"Detection complete: {len(detections)} faces found")

        # Save detections to database
        results = []
        for det in detections:
            if save_detection and det['matched']:
                detection_record = Detection(
                    person_id=det['person_id'],
                    timestamp=det['timestamp'],
                    camera_id=camera_id,
                    confidence=float(det['confidence']),
                    face_distance=float(det['distance']),
                    bbox_x=int(det['bbox'][0]),
                    bbox_y=int(det['bbox'][1]),
                    bbox_width=int(det['bbox'][2]),
                    bbox_height=int(det['bbox'][3])
                )
                db.add(detection_record)

            results.append(DetectionResponse(
                person_id=det.get('person_id'),
                person_name=det.get('person_name', 'Unknown'),
                confidence=det['confidence'],
                timestamp=det['timestamp'],
                camera_id=camera_id,
                is_unknown=det['is_unknown'],
                bbox=det.get('bbox')  # Add bbox to response
            ))

        if save_detection:
            db.commit()

        return results

    except Exception as e:
        logger.error(f"Error in face detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/detections", response_model=List[DetectionResponse])
async def get_detections(
    person_id: Optional[int] = None,
    camera_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get detection history with filters"""
    query = db.query(Detection).join(Person)

    if person_id:
        query = query.filter(Detection.person_id == person_id)

    if camera_id:
        query = query.filter(Detection.camera_id == camera_id)

    if start_date:
        query = query.filter(Detection.timestamp >= start_date)

    if end_date:
        query = query.filter(Detection.timestamp <= end_date)

    detections = query.order_by(Detection.timestamp.desc()).limit(limit).all()

    return [
        DetectionResponse(
            person_id=d.person_id,
            person_name=d.person.name,
            confidence=d.confidence,
            timestamp=d.timestamp,
            camera_id=d.camera_id,
            is_unknown=False
        )
        for d in detections
    ]


# ==================== Analytics ====================

@app.get("/api/analytics/summary", response_model=AnalyticsResponse)
async def get_analytics_summary(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get analytics summary for the specified number of days"""
    try:
        logger.info(f"Getting analytics summary for {days} days")

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Total detections
        total_detections = db.query(Detection).filter(
            Detection.timestamp >= start_date
        ).count()
        logger.info(f"Total detections: {total_detections}")

        # Unique persons detected
        unique_persons = db.query(Detection.person_id).filter(
            Detection.timestamp >= start_date
        ).distinct().count()

        # Total registered persons
        total_persons = db.query(Person).filter(Person.is_active == True).count()

        # Active cameras
        active_cameras = db.query(Camera).filter(Camera.is_active == True).count()

        # Detections by person (top 10)
        top_persons = db.query(
            Person.name,
            func.count(Detection.id).label('count')
        ).join(Detection).filter(
            Detection.timestamp >= start_date
        ).group_by(Person.id, Person.name).order_by(
            func.count(Detection.id).desc()
        ).limit(10).all()

        logger.info(f"Analytics: detections={total_detections}, unique={unique_persons}, registered={total_persons}")

        return AnalyticsResponse(
            total_detections=total_detections,
            unique_persons=unique_persons,
            total_registered=total_persons,
            active_cameras=active_cameras,
            top_persons=[{"name": name, "count": count} for name, count in top_persons],
            period_days=days
        )

    except Exception as e:
        logger.error(f"Error in analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Camera Management ====================

@app.get("/api/cameras", response_model=List[CameraResponse])
async def get_cameras(db: Session = Depends(get_db)):
    """Get all configured cameras"""
    cameras = db.query(Camera).all()
    return [CameraResponse.from_orm(c) for c in cameras]


@app.post("/api/cameras/{camera_id}/start")
async def start_camera(camera_id: str, db: Session = Depends(get_db)):
    """Start processing a camera stream"""
    global video_processor, camera_manager

    camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()

    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # Initialize video processor if not exists
    if not video_processor:
        persons = db.query(Person).filter(Person.is_active == True).all()
        video_processor = VideoProcessor(
            face_detector=face_detector,
            known_persons=persons,
            recognition_threshold=config['face_recognition']['recognition_threshold'],
            frame_skip=config['camera']['frame_skip'],
            dedup_window=config['analytics']['dedup_window']
        )
        camera_manager = CameraManager(video_processor)

    # Detection callback to save to database
    def save_detection(detections):
        with get_db() as session:
            for det in detections:
                if det['matched']:
                    detection = Detection(
                        person_id=det['person_id'],
                        timestamp=det['timestamp'],
                        camera_id=camera_id,
                        confidence=det['confidence'],
                        face_distance=det['distance'],
                        bbox_x=det['bbox'][0],
                        bbox_y=det['bbox'][1],
                        bbox_width=det['bbox'][2],
                        bbox_height=det['bbox'][3]
                    )
                    session.add(detection)
            session.commit()

    # Start camera
    camera_manager.start_camera(camera_id, camera.url, save_detection)

    camera.status = "online"
    camera.last_online = datetime.utcnow()
    db.commit()

    return {"success": True, "message": f"Camera {camera_id} started"}


@app.post("/api/cameras/{camera_id}/stop")
async def stop_camera(camera_id: str, db: Session = Depends(get_db)):
    """Stop processing a camera stream"""
    if not camera_manager:
        raise HTTPException(status_code=400, detail="Camera manager not initialized")

    camera_manager.stop_camera(camera_id)

    camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if camera:
        camera.status = "offline"
        db.commit()

    return {"success": True, "message": f"Camera {camera_id} stopped"}


# ==================== Health Check ====================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
