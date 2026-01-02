from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models import PersonDetectionLog, PhoneDetectionLog
from schemas import (
    PersonDetectionLogCreate,
    PersonDetectionLogResponse,
    PhoneDetectionLogCreate,
    PhoneDetectionLogResponse
)

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.post("/person", response_model=PersonDetectionLogResponse)
def create_person_log(
    log: PersonDetectionLogCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new person detection log
    """
    new_log = PersonDetectionLog(
        person_name=log.person_name,
        is_authorized=log.is_authorized,
        confidence=log.confidence,
        track_id=log.track_id
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


@router.post("/phone", response_model=PhoneDetectionLogResponse)
def create_phone_log(
    log: PhoneDetectionLogCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new phone detection log
    """
    new_log = PhoneDetectionLog()
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


@router.get("/person", response_model=List[PersonDetectionLogResponse])
def get_person_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    person_name: Optional[str] = None,
    is_authorized: Optional[bool] = None,
    hours: Optional[int] = Query(None, description="Filter logs from last N hours"),
    db: Session = Depends(get_db)
):
    """
    Get person detection logs with optional filters
    """
    query = db.query(PersonDetectionLog)

    # Apply filters
    if person_name:
        query = query.filter(PersonDetectionLog.person_name == person_name)

    if is_authorized is not None:
        query = query.filter(PersonDetectionLog.is_authorized == is_authorized)

    if hours:
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(PersonDetectionLog.detected_at >= time_threshold)

    # Order by most recent first
    query = query.order_by(desc(PersonDetectionLog.detected_at))

    # Pagination
    logs = query.offset(offset).limit(limit).all()
    return logs


@router.get("/phone", response_model=List[PhoneDetectionLogResponse])
def get_phone_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    hours: Optional[int] = Query(None, description="Filter logs from last N hours"),
    db: Session = Depends(get_db)
):
    """
    Get phone detection logs with optional filters
    """
    query = db.query(PhoneDetectionLog)

    if hours:
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(PhoneDetectionLog.detected_at >= time_threshold)

    # Order by most recent first
    query = query.order_by(desc(PhoneDetectionLog.detected_at))

    # Pagination
    logs = query.offset(offset).limit(limit).all()
    return logs


@router.get("/person/stats")
def get_person_stats(db: Session = Depends(get_db)):
    """
    Get statistics about person detections
    """
    total_detections = db.query(PersonDetectionLog).count()
    authorized_count = db.query(PersonDetectionLog).filter(PersonDetectionLog.is_authorized == True).count()
    unauthorized_count = db.query(PersonDetectionLog).filter(PersonDetectionLog.is_authorized == False).count()

    return {
        "total_detections": total_detections,
        "authorized_detections": authorized_count,
        "unauthorized_detections": unauthorized_count
    }
