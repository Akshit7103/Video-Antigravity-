from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import numpy as np
import base64
from io import BytesIO
from PIL import Image

from database import get_db
from models import RegisteredPerson
from schemas import PersonResponse, PersonWithPhoto, FaceEmbeddingRequest
from services.face_service import invalidate_face_cache, find_matching_person

router = APIRouter(prefix="/api/faces", tags=["faces"])


@router.post("/register", response_model=PersonResponse)
async def register_person(
    name: str = Form(...),
    photo: UploadFile = File(...),
    embedding: str = Form(...),  # JSON string of face embedding
    db: Session = Depends(get_db)
):
    """
    Register a new person with their face photo and embedding
    """
    # Check if person already exists
    existing = db.query(RegisteredPerson).filter(RegisteredPerson.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Person with this name already registered")

    # Read and validate photo
    photo_bytes = await photo.read()
    try:
        img = Image.open(BytesIO(photo_bytes))
        img.verify()  # Verify it's a valid image
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Parse embedding
    try:
        import json
        embedding_list = json.loads(embedding)
        embedding_array = np.array(embedding_list, dtype=np.float32)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid embedding format")

    # Create new person
    new_person = RegisteredPerson(
        name=name,
        face_embedding=embedding_array.tobytes(),
        photo=photo_bytes
    )

    db.add(new_person)
    db.commit()
    db.refresh(new_person)

    # Invalidate cache
    invalidate_face_cache()

    return new_person


@router.get("/", response_model=List[PersonResponse])
def get_all_persons(db: Session = Depends(get_db)):
    """
    Get all registered persons (without photos)
    """
    persons = db.query(RegisteredPerson).order_by(RegisteredPerson.registered_at.desc()).all()
    return persons


@router.get("/with-photos", response_model=List[PersonWithPhoto])
def get_all_persons_with_photos(db: Session = Depends(get_db)):
    """
    Get all registered persons with their photos
    """
    persons = db.query(RegisteredPerson).order_by(RegisteredPerson.registered_at.desc()).all()

    result = []
    for person in persons:
        photo_base64 = base64.b64encode(person.photo).decode('utf-8')
        result.append({
            "id": person.id,
            "name": person.name,
            "registered_at": person.registered_at,
            "photo_base64": photo_base64
        })

    return result


@router.delete("/{person_id}")
def delete_person(person_id: int, db: Session = Depends(get_db)):
    """
    Delete a registered person
    """
    person = db.query(RegisteredPerson).filter(RegisteredPerson.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    db.delete(person)
    db.commit()

    # Invalidate cache
    invalidate_face_cache()

    return {"message": f"Person {person.name} deleted successfully"}


@router.post("/match")
def match_face(request: FaceEmbeddingRequest, db: Session = Depends(get_db)):
    """
    Match a face embedding against registered persons
    Returns: {name, confidence} or {name: null, confidence: null} if no match
    """
    embedding_array = np.array(request.embedding, dtype=np.float32)
    name, confidence = find_matching_person(embedding_array, db)

    return {
        "name": name,
        "confidence": confidence
    }


@router.post("/extract-embedding")
async def extract_embedding(image: UploadFile = File(...)):
    """
    Extract face embedding from an uploaded image
    This endpoint uses InsightFace to detect and extract face embedding
    Returns: {embedding: list[float], bbox: list[int]} or error if no face found
    """
    try:
        # Read image
        image_bytes = await image.read()
        img = Image.open(BytesIO(image_bytes))

        # Convert to numpy array (RGB)
        img_array = np.array(img)

        # Import InsightFace here (to avoid loading on startup)
        from insightface.app import FaceAnalysis

        # Initialize face analyzer
        app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=-1, det_size=(640, 640))

        # Detect faces
        faces = app.get(img_array)

        if not faces:
            raise HTTPException(status_code=400, detail="No face detected in image")

        # Get largest face
        largest_face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))

        # Extract embedding
        embedding = largest_face.embedding.tolist()

        # Get bounding box
        bbox = largest_face.bbox.tolist()

        return {
            "embedding": embedding,
            "bbox": bbox
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
