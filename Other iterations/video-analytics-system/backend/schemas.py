from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PersonCreate(BaseModel):
    name: str


class PersonResponse(BaseModel):
    id: int
    name: str
    registered_at: datetime

    class Config:
        from_attributes = True


class PersonWithPhoto(PersonResponse):
    photo_base64: str  # Base64 encoded image


class PersonDetectionLogCreate(BaseModel):
    person_name: str
    is_authorized: bool
    confidence: Optional[float] = None
    track_id: Optional[int] = None


class PersonDetectionLogResponse(BaseModel):
    id: int
    person_name: str
    is_authorized: bool
    confidence: Optional[float]
    detected_at: datetime
    track_id: Optional[int]

    class Config:
        from_attributes = True


class PhoneDetectionLogCreate(BaseModel):
    pass  # Only timestamp needed


class PhoneDetectionLogResponse(BaseModel):
    id: int
    detected_at: datetime

    class Config:
        from_attributes = True


class FaceEmbeddingRequest(BaseModel):
    embedding: list[float]  # Face embedding to search
