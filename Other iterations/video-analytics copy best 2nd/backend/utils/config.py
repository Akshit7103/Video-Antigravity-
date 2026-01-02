"""
Configuration loader and manager
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from loguru import logger


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file

    Args:
        config_path: Path to config file. If None, uses default path.

    Returns:
        Configuration dictionary
    """
    if config_path is None:
        # Default path: project_root/config/config.yaml
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {e}")
        raise


def get_storage_paths(config: Dict[str, Any]) -> Dict[str, Path]:
    """
    Get storage paths from configuration and ensure they exist

    Args:
        config: Configuration dictionary

    Returns:
        Dictionary of Path objects
    """
    project_root = Path(__file__).parent.parent.parent

    paths = {
        'faces': project_root / config['storage']['faces_dir'],
        'videos': project_root / config['storage']['videos_dir'],
        'logs': project_root / config['storage']['logs_dir']
    }

    # Create directories if they don't exist
    for name, path in paths.items():
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Storage path '{name}': {path}")

    return paths


def get_database_url(config: Dict[str, Any]) -> str:
    """
    Build database URL from configuration

    Args:
        config: Configuration dictionary

    Returns:
        Database connection URL
    """
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    db_config = config['database']['postgres']

    # Get values from environment variables or config (env vars take precedence)
    host = os.getenv('DB_HOST', db_config.get('host', 'localhost'))
    port = os.getenv('DB_PORT', db_config.get('port', 5432))
    database = os.getenv('DB_NAME', db_config.get('database', 'video_analytics'))
    user = os.getenv('DB_USER', db_config.get('user', 'postgres'))
    password = os.getenv('DB_PASSWORD')  # Must be in .env file

    if not password:
        logger.error("DB_PASSWORD not found in environment variables")
        raise ValueError("DB_PASSWORD must be set in .env file")

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def get_redis_url(config: Dict[str, Any]) -> str:
    """
    Build Redis URL from configuration

    Args:
        config: Configuration dictionary

    Returns:
        Redis connection URL
    """
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    redis_config = config['database']['redis']

    # Get values from environment variables or config (env vars take precedence)
    host = os.getenv('REDIS_HOST', redis_config.get('host', 'localhost'))
    port = os.getenv('REDIS_PORT', redis_config.get('port', 6379))
    db = os.getenv('REDIS_DB', redis_config.get('db', 0))

    return f"redis://{host}:{port}/{db}"
