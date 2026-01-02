from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Database (SQLite - no installation needed)
    database_url: str = "sqlite:///./video_analytics.db"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Face Recognition
    face_similarity_threshold: float = 0.5

    # CORS
    cors_origins: list = ["http://localhost:8000", "http://127.0.0.1:8000"]

    # Cache directory for face embeddings
    cache_dir: str = "./cache"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    # Create cache directory if it doesn't exist
    os.makedirs(settings.cache_dir, exist_ok=True)
    return settings
