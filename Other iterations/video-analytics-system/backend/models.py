from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, Float, Boolean
from sqlalchemy.sql import func
from datetime import datetime
from database import Base


class RegisteredPerson(Base):
    __tablename__ = "registered_persons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    face_embedding = Column(LargeBinary, nullable=False)  # Stored as binary (numpy array bytes)
    photo = Column(LargeBinary, nullable=False)  # JPEG/PNG image bytes
    registered_at = Column(DateTime, default=datetime.utcnow)


class PersonDetectionLog(Base):
    __tablename__ = "person_detection_logs"

    id = Column(Integer, primary_key=True, index=True)
    person_name = Column(String, nullable=False, index=True)  # Name or "Unknown"
    is_authorized = Column(Boolean, nullable=False, default=False)
    confidence = Column(Float, nullable=True)  # Face recognition confidence (None for Unknown)
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    track_id = Column(Integer, nullable=True)  # Tracker ID from BoT-SORT


class PhoneDetectionLog(Base):
    __tablename__ = "phone_detection_logs"

    id = Column(Integer, primary_key=True, index=True)
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
