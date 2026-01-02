"""
Centralized Logging Configuration
"""
import sys
import os
from pathlib import Path
from loguru import logger
from datetime import datetime


def setup_logging(log_dir: str = "data/logs", log_level: str = "INFO"):
    """
    Configure centralized logging with rotation

    Args:
        log_dir: Directory for log files
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR)
    """
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Remove default handler
    logger.remove()

    # Console handler - colorized output
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )

    # Main log file - all levels with rotation
    logger.add(
        log_path / "app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",  # Rotate when file reaches 10MB
        retention="30 days",  # Keep logs for 30 days
        compression="zip",  # Compress rotated logs
        encoding="utf8"
    )

    # Error log file - errors only
    logger.add(
        log_path / "error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
        level="ERROR",
        rotation="5 MB",
        retention="60 days",  # Keep error logs longer
        compression="zip",
        encoding="utf8",
        backtrace=True,  # Include full traceback
        diagnose=True  # Include variable values
    )

    # API requests log - for debugging API calls
    logger.add(
        log_path / "api.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="INFO",
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        encoding="utf8",
        filter=lambda record: "API" in record["message"] or "endpoint" in record["extra"]
    )

    # Performance log - for tracking slow operations
    logger.add(
        log_path / "performance.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
        level="INFO",
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        encoding="utf8",
        filter=lambda record: "performance" in record["extra"] or "duration" in record["message"].lower()
    )

    # JSON log file - structured logging for parsing
    logger.add(
        log_path / "app.json",
        format="{message}",
        level="INFO",
        rotation="20 MB",
        retention="30 days",
        compression="zip",
        encoding="utf8",
        serialize=True  # Output as JSON
    )

    logger.info(f"Logging system initialized - Log directory: {log_path.absolute()}")
    logger.info(f"Log level: {log_level}")

    return logger


def log_api_request(method: str, endpoint: str, status_code: int, duration_ms: float, user: str = None):
    """
    Log API request details

    Args:
        method: HTTP method
        endpoint: API endpoint path
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        user: Username if authenticated
    """
    user_str = f"user={user}" if user else "anonymous"

    logger.bind(endpoint=endpoint).info(
        f"API {method} {endpoint} - {status_code} - {duration_ms:.2f}ms - {user_str}"
    )


def log_performance(operation: str, duration_ms: float, details: dict = None):
    """
    Log performance metrics

    Args:
        operation: Operation name
        duration_ms: Duration in milliseconds
        details: Additional details dict
    """
    details_str = f" - {details}" if details else ""

    logger.bind(performance=True).info(
        f"PERFORMANCE: {operation} took {duration_ms:.2f}ms{details_str}"
    )


def log_face_detection(num_faces: int, processing_time_ms: float, image_size: tuple):
    """
    Log face detection event

    Args:
        num_faces: Number of faces detected
        processing_time_ms: Processing time
        image_size: Image dimensions (width, height)
    """
    logger.info(
        f"Face Detection: {num_faces} faces in {processing_time_ms:.2f}ms | Image: {image_size[0]}x{image_size[1]}"
    )


def log_database_operation(operation: str, table: str, duration_ms: float, affected_rows: int = None):
    """
    Log database operation

    Args:
        operation: SQL operation (SELECT, INSERT, UPDATE, DELETE)
        table: Table name
        duration_ms: Query duration
        affected_rows: Number of affected rows
    """
    rows_str = f" | {affected_rows} rows" if affected_rows is not None else ""

    logger.debug(
        f"DB {operation} on {table} - {duration_ms:.2f}ms{rows_str}"
    )


class LogContext:
    """Context manager for logging operations with timing"""

    def __init__(self, operation: str, log_performance: bool = True):
        """
        Initialize log context

        Args:
            operation: Operation name
            log_performance: Whether to log performance metrics
        """
        self.operation = operation
        self.log_performance = log_performance
        self.start_time = None

    def __enter__(self):
        """Start timing"""
        self.start_time = datetime.now()
        logger.debug(f"START: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log"""
        duration_ms = (datetime.now() - self.start_time).total_seconds() * 1000

        if exc_type is not None:
            logger.error(f"FAILED: {self.operation} after {duration_ms:.2f}ms - {exc_val}")
            return False  # Re-raise exception

        logger.debug(f"END: {self.operation} - {duration_ms:.2f}ms")

        if self.log_performance:
            log_performance(self.operation, duration_ms)

        return True


# Example usage:
# with LogContext("Face Detection"):
#     # Your code here
#     pass
