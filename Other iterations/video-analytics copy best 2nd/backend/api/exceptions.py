"""
Custom exceptions and exception handlers for the API
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
from typing import Any, Dict


class VideoAnalyticsException(Exception):
    """Base exception for Video Analytics API"""
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DatabaseException(VideoAnalyticsException):
    """Exception for database errors"""
    def __init__(self, message: str = "Database error occurred"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class AuthenticationException(VideoAnalyticsException):
    """Exception for authentication errors"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationException(VideoAnalyticsException):
    """Exception for authorization errors"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class NotFoundException(VideoAnalyticsException):
    """Exception for resource not found errors"""
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", status.HTTP_404_NOT_FOUND)


class ValidationException(VideoAnalyticsException):
    """Exception for validation errors"""
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class FileProcessingException(VideoAnalyticsException):
    """Exception for file processing errors"""
    def __init__(self, message: str = "File processing failed"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class FaceDetectionException(VideoAnalyticsException):
    """Exception for face detection errors"""
    def __init__(self, message: str = "Face detection failed"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class DuplicateResourceException(VideoAnalyticsException):
    """Exception for duplicate resource errors"""
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} already exists", status.HTTP_409_CONFLICT)


# Exception Handlers

async def video_analytics_exception_handler(request: Request, exc: VideoAnalyticsException) -> JSONResponse:
    """Handler for custom VideoAnalytics exceptions"""
    logger.error(f"{exc.__class__.__name__}: {exc.message} - Path: {request.url.path}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "path": request.url.path
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler for Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    logger.error(f"Validation Error - Path: {request.url.path} - Errors: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": errors,
            "path": request.url.path
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for unhandled exceptions"""
    logger.exception(f"Unhandled Exception - Path: {request.url.path} - Error: {str(exc)}")

    # Don't expose internal error details in production
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An internal error occurred. Please try again later.",
            "path": request.url.path
        }
    )


def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app"""
    app.add_exception_handler(VideoAnalyticsException, video_analytics_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("Exception handlers registered")
