"""
Database initialization script
Run this to create database tables and initial data
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from loguru import logger
from backend.database.connection import init_database
from backend.database.models import Base, Camera
from backend.utils.config import load_config


def initialize_database():
    """Initialize database with tables and default data"""

    # Load configuration
    config = load_config()

    # Build database URL
    db_config = config['database']['postgres']
    database_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

    # Build Redis URL
    redis_config = config['database']['redis']
    redis_url = f"redis://{redis_config['host']}:{redis_config['port']}/{redis_config['db']}"

    logger.info("Initializing database connection...")

    try:
        # Initialize database manager
        db_manager = init_database(database_url, redis_url)

        # Create all tables
        logger.info("Creating database tables...")
        db_manager.create_tables()

        # Add default cameras from config
        logger.info("Adding default camera configurations...")
        with db_manager.get_session() as session:
            for cam_config in config['camera']['sources']:
                # Check if camera already exists
                existing = session.query(Camera).filter_by(camera_id=cam_config['id']).first()
                if not existing:
                    camera = Camera(
                        camera_id=cam_config['id'],
                        name=cam_config['name'],
                        url=str(cam_config['url']),
                        is_active=cam_config['enabled'],
                        resolution_width=config['camera']['width'],
                        resolution_height=config['camera']['height'],
                        fps=config['camera']['fps']
                    )
                    session.add(camera)
                    logger.info(f"Added camera: {cam_config['name']} ({cam_config['id']})")
                else:
                    logger.info(f"Camera already exists: {cam_config['name']} ({cam_config['id']})")

        logger.success("Database initialized successfully!")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


if __name__ == "__main__":
    # Configure logger
    logger.add(
        "data/logs/db_init.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO"
    )

    initialize_database()
