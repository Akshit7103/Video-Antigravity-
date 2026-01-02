"""
Database models for Video Analytics System
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON, ARRAY

Base = declarative_base()


class User(Base):
    """Model for system users (authentication)"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))

    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Person(Base):
    """Model for registered persons"""
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True)
    employee_id = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    department = Column(String(100))
    designation = Column(String(100))

    face_encoding = Column(LargeBinary, nullable=False)

    registration_date = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)

    profile_image = Column(String(500))
    sample_images = Column(JSON)  # List of image paths

    detections = relationship("Detection", back_populates="person", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Person(id={self.id}, name='{self.name}', employee_id='{self.employee_id}')>"


class Detection(Base):
    """Model for face detection events"""
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False, index=True)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    camera_id = Column(String(50), nullable=False, index=True)
    camera_name = Column(String(255))

    confidence = Column(Float, nullable=False)
    face_distance = Column(Float)

    bbox_x = Column(Integer)
    bbox_y = Column(Integer)
    bbox_width = Column(Integer)
    bbox_height = Column(Integer)

    snapshot_path = Column(String(500))

    video_file = Column(String(500))
    frame_number = Column(Integer)

    # FIXED
    meta_data = Column(JSON)

    person = relationship("Person", back_populates="detections")

    def __repr__(self):
        return f"<Detection(id={self.id}, person_id={self.person_id}, timestamp='{self.timestamp}')>"


class Camera(Base):
    """Model for camera configurations"""
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)

    url = Column(String(500), nullable=False)
    username = Column(String(100))
    password = Column(String(100))

    is_active = Column(Boolean, default=True)
    resolution_width = Column(Integer, default=1280)
    resolution_height = Column(Integer, default=720)
    fps = Column(Integer, default=30)

    location = Column(String(255))
    description = Column(Text)

    status = Column(String(50), default="offline")
    last_online = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Camera(id={self.id}, camera_id='{self.camera_id}', name='{self.name}')>"


class Session(Base):
    """Model for tracking person sessions (entry/exit)"""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False, index=True)
    camera_id = Column(String(50), nullable=False, index=True)

    entry_time = Column(DateTime, nullable=False, index=True)
    exit_time = Column(DateTime)
    duration_seconds = Column(Integer)

    is_active = Column(Boolean, default=True)

    # FIXED
    meta_data = Column(JSON)

    def __repr__(self):
        return f"<Session(id={self.id}, person_id={self.person_id}, entry_time='{self.entry_time}')>"


class SystemLog(Base):
    """Model for system logs and events"""
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    level = Column(String(20), nullable=False)
    module = Column(String(100))
    message = Column(Text, nullable=False)

    user_id = Column(Integer)
    camera_id = Column(String(50))

    # FIXED
    meta_data = Column(JSON)

    def __repr__(self):
        return f"<SystemLog(id={self.id}, level='{self.level}', timestamp='{self.timestamp}')>"


class Alert(Base):
    """Model for system alerts and notifications"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text)

    camera_id = Column(String(50), index=True)
    person_id = Column(Integer, ForeignKey("persons.id"))
    detection_id = Column(Integer, ForeignKey("detections.id"))

    is_read = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(255))

    # FIXED
    meta_data = Column(JSON)

    def __repr__(self):
        return f"<Alert(id={self.id}, type='{self.alert_type}', severity='{self.severity}')>"
