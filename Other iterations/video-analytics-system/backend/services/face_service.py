import numpy as np
import pickle
import os
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from models import RegisteredPerson
from config import get_settings

settings = get_settings()

# In-memory cache for face embeddings
_face_embeddings_cache = None
_cache_timestamp = 0


def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """Calculate cosine similarity between two embeddings"""
    return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))


def get_cached_embeddings(db: Session) -> dict:
    """Get face embeddings from cache or database"""
    global _face_embeddings_cache, _cache_timestamp

    import time
    current_time = time.time()

    # Cache for 5 minutes
    if _face_embeddings_cache is not None and (current_time - _cache_timestamp) < 300:
        return _face_embeddings_cache

    # Load from database
    persons = db.query(RegisteredPerson).all()
    _face_embeddings_cache = {
        person.name: np.frombuffer(person.face_embedding, dtype=np.float32)
        for person in persons
    }
    _cache_timestamp = current_time

    return _face_embeddings_cache


def find_matching_person(face_embedding: np.ndarray, db: Session) -> Tuple[Optional[str], Optional[float]]:
    """
    Find matching person from database using face embedding
    Returns: (person_name, confidence) or (None, None) if no match
    """
    registered_embeddings = get_cached_embeddings(db)

    if not registered_embeddings:
        return None, None

    # Find best match
    best_match = None
    best_similarity = 0.0

    for name, stored_embedding in registered_embeddings.items():
        similarity = cosine_similarity(face_embedding, stored_embedding)
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = name

    # Check against threshold
    if best_similarity >= settings.face_similarity_threshold:
        return best_match, float(best_similarity)

    return None, None


def invalidate_face_cache():
    """Invalidate face embeddings cache (call when new person registered)"""
    global _face_embeddings_cache, _cache_timestamp
    _face_embeddings_cache = None
    _cache_timestamp = 0
