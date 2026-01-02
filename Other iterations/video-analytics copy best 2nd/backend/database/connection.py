"""
Database connection management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import redis
from typing import Generator
from loguru import logger

from .models import Base


class DatabaseManager:
    """Manages database connections and sessions"""

    def __init__(self, database_url: str, redis_url: str = None):
        """
        Initialize database manager

        Args:
            database_url: PostgreSQL connection URL
            redis_url: Redis connection URL (optional)
        """
        # PostgreSQL
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            echo=False
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Redis (for caching)
        self.redis_client = None
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=False)
                self.redis_client.ping()
                logger.info("Connected to Redis successfully")
            except Exception as e:
                logger.warning(f"Could not connect to Redis: {e}")
                self.redis_client = None

    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise

    def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("All database tables dropped")
        except Exception as e:
            logger.error(f"Error dropping database tables: {e}")
            raise

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get database session with automatic cleanup

        Usage:
            with db_manager.get_session() as session:
                person = session.query(Person).first()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def get_redis_client(self):
        """Get Redis client"""
        return self.redis_client


# Global database manager instance
_db_manager = None


def init_database(database_url: str, redis_url: str = None) -> DatabaseManager:
    """
    Initialize global database manager

    Args:
        database_url: PostgreSQL connection URL
        redis_url: Redis connection URL (optional)

    Returns:
        DatabaseManager instance
    """
    global _db_manager
    _db_manager = DatabaseManager(database_url, redis_url)
    return _db_manager


def get_db_manager() -> DatabaseManager:
    """Get global database manager instance"""
    if _db_manager is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _db_manager


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database session

    Usage in FastAPI:
        @app.get("/persons")
        def get_persons(db: Session = Depends(get_db)):
            return db.query(Person).all()
    """
    db_manager = get_db_manager()
    session = db_manager.SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_redis():
    """
    Dependency for FastAPI to get Redis client

    Usage in FastAPI:
        @app.get("/cached")
        def get_cached(redis_client = Depends(get_redis)):
            return redis_client.get("key")
    """
    db_manager = get_db_manager()
    return db_manager.get_redis_client()
