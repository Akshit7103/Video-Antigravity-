"""Database package"""
from .models import Base, User, Person, Detection, Camera, Session, SystemLog, Alert
from .connection import (
    DatabaseManager,
    init_database,
    get_db_manager,
    get_db,
    get_redis
)

__all__ = [
    'Base',
    'User',
    'Person',
    'Detection',
    'Camera',
    'Session',
    'SystemLog',
    'Alert',
    'DatabaseManager',
    'init_database',
    'get_db_manager',
    'get_db',
    'get_redis'
]
