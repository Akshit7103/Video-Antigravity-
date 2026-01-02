"""
Helper utility functions
"""
import numpy as np
import pickle
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from pathlib import Path
import hashlib
import re


def serialize_encoding(encoding: np.ndarray) -> bytes:
    """
    Serialize face encoding to bytes for database storage

    Args:
        encoding: Face encoding array

    Returns:
        Serialized bytes
    """
    return pickle.dumps(encoding)


def deserialize_encoding(data: bytes) -> np.ndarray:
    """
    Deserialize face encoding from bytes

    Args:
        data: Serialized encoding bytes

    Returns:
        Face encoding array
    """
    return pickle.loads(data)


def calculate_face_distance(encoding1: np.ndarray, encoding2: np.ndarray) -> float:
    """
    Calculate Euclidean distance between two face encodings

    Args:
        encoding1: First face encoding
        encoding2: Second face encoding

    Returns:
        Distance (lower = more similar)
    """
    return float(np.linalg.norm(encoding1 - encoding2))


def is_match(encoding1: np.ndarray, encoding2: np.ndarray, threshold: float = 0.6) -> bool:
    """
    Check if two face encodings match

    Args:
        encoding1: First face encoding
        encoding2: Second face encoding
        threshold: Matching threshold (default 0.6)

    Returns:
        True if faces match
    """
    distance = calculate_face_distance(encoding1, encoding2)
    return distance < threshold


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    return filename


def generate_person_id(name: str, email: str) -> str:
    """
    Generate unique person ID from name and email

    Args:
        name: Person's name
        email: Person's email

    Returns:
        Unique ID string
    """
    data = f"{name}_{email}_{datetime.utcnow().isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def get_timestamp_string(dt: datetime = None, format: str = "%Y%m%d_%H%M%S") -> str:
    """
    Get formatted timestamp string

    Args:
        dt: Datetime object (default: current time)
        format: String format

    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.utcnow()
    return dt.strftime(format)


def parse_camera_url(url: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Parse camera URL to extract connection details

    Args:
        url: Camera URL (can be device ID, RTSP URL, etc.)

    Returns:
        Tuple of (url_type, parsed_url, credentials)
    """
    # Check if it's a device ID (integer)
    if url.isdigit():
        return ('device', int(url), None)

    # Check if it's an RTSP URL
    if url.startswith('rtsp://'):
        return ('rtsp', url, None)

    # Check if it's an HTTP/HTTPS URL
    if url.startswith(('http://', 'https://')):
        return ('http', url, None)

    # Default: treat as file path
    return ('file', url, None)


def get_bbox_area(bbox: Tuple[int, int, int, int]) -> int:
    """
    Calculate bounding box area

    Args:
        bbox: Bounding box (x, y, width, height)

    Returns:
        Area in pixels
    """
    x, y, w, h = bbox
    return w * h


def expand_bbox(bbox: Tuple[int, int, int, int],
                expand_ratio: float = 0.2,
                max_width: int = None,
                max_height: int = None) -> Tuple[int, int, int, int]:
    """
    Expand bounding box by a ratio

    Args:
        bbox: Original bounding box (x, y, width, height)
        expand_ratio: Expansion ratio (default 0.2 = 20%)
        max_width: Maximum image width for clipping
        max_height: Maximum image height for clipping

    Returns:
        Expanded bounding box
    """
    x, y, w, h = bbox

    # Calculate expansion
    expand_w = int(w * expand_ratio)
    expand_h = int(h * expand_ratio)

    # Apply expansion
    new_x = max(0, x - expand_w // 2)
    new_y = max(0, y - expand_h // 2)
    new_w = w + expand_w
    new_h = h + expand_h

    # Clip to image boundaries
    if max_width:
        new_w = min(new_w, max_width - new_x)
    if max_height:
        new_h = min(new_h, max_height - new_y)

    return (new_x, new_y, new_w, new_h)


def is_within_dedup_window(last_detection: datetime,
                           current_time: datetime = None,
                           window_seconds: int = 30) -> bool:
    """
    Check if current detection is within deduplication window

    Args:
        last_detection: Timestamp of last detection
        current_time: Current timestamp (default: now)
        window_seconds: Deduplication window in seconds

    Returns:
        True if within window (should skip)
    """
    if current_time is None:
        current_time = datetime.utcnow()

    time_diff = (current_time - last_detection).total_seconds()
    return time_diff < window_seconds


def format_duration(seconds: int) -> str:
    """
    Format duration in human-readable format

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "2h 15m", "45m", "30s")
    """
    if seconds < 60:
        return f"{seconds}s"

    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if remaining_minutes == 0:
        return f"{hours}h"
    return f"{hours}h {remaining_minutes}m"


def get_date_range(days: int = 7) -> Tuple[datetime, datetime]:
    """
    Get date range for analytics queries

    Args:
        days: Number of days to look back

    Returns:
        Tuple of (start_date, end_date)
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    return (start_date, end_date)
