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
    db_config = config['database']['postgres']
    return f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"


def get_redis_url(config: Dict[str, Any]) -> str:
    """
    Build Redis URL from configuration

    Args:
        config: Configuration dictionary

    Returns:
        Redis connection URL
    """
    redis_config = config['database']['redis']
    return f"redis://{redis_config['host']}:{redis_config['port']}/{redis_config['db']}"
