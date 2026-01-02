"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PersonCreate(BaseModel):
    """Schema for creating a new person"""
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    employee_id: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)
    designation: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class PersonResponse(BaseModel):
    """Schema for person response"""
    id: int
    name: str
    email: Optional[str]
    employee_id: Optional[str]
    phone: Optional[str]
    department: Optional[str]
    designation: Optional[str]
    registration_date: datetime
    last_seen: Optional[datetime]
    is_active: bool
    profile_image: Optional[str]

    class Config:
        from_attributes = True


class RegisterResponse(BaseModel):
    """Schema for registration response"""
    success: bool
    message: str
    person_id: int
    person_name: str


class DetectionResponse(BaseModel):
    """Schema for detection response"""
    person_id: Optional[int]
    person_name: str
    confidence: float
    timestamp: datetime
    camera_id: str
    is_unknown: bool
    bbox: Optional[List[int]] = None  # [x, y, width, height]


class CameraResponse(BaseModel):
    """Schema for camera response"""
    id: int
    camera_id: str
    name: str
    location: Optional[str]
    status: str
    is_active: bool
    last_online: Optional[datetime]

    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    """Schema for analytics summary"""
    total_detections: int
    unique_persons: int
    total_registered: int
    active_cameras: int
    top_persons: List[Dict[str, Any]]
    period_days: int


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
