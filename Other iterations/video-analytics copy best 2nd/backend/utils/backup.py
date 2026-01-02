"""
Database Backup Utility
"""
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from loguru import logger
import shutil


class BackupManager:
    """Handles database backups and restores"""

    def __init__(self, backup_dir: str = "backups"):
        """
        Initialize backup manager

        Args:
            backup_dir: Directory to store backups
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, db_config: Dict[str, Any]) -> str:
        """
        Create database backup

        Args:
            db_config: Database configuration dict

        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"backup_{timestamp}.sql"

        try:
            # Use pg_dump to create backup
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config.get('password', '')

            cmd = [
                'pg_dump',
                '-h', db_config.get('host', 'localhost'),
                '-p', str(db_config.get('port', 5432)),
                '-U', db_config.get('user', 'postgres'),
                '-d', db_config.get('database', 'video_analytics'),
                '-F', 'p',  # Plain text format
                '-f', str(backup_file)
            ]

            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )

            if result.returncode != 0:
                raise Exception(f"pg_dump failed: {result.stderr}")

            # Create metadata file
            metadata = {
                'timestamp': timestamp,
                'database': db_config.get('database'),
                'size_bytes': backup_file.stat().st_size,
                'created_at': datetime.now().isoformat()
            }

            metadata_file = self.backup_dir / f"backup_{timestamp}.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.success(f"Backup created: {backup_file}")
            return str(backup_file)

        except FileNotFoundError:
            logger.error("pg_dump not found. Please install PostgreSQL client tools.")
            raise Exception("pg_dump command not found. Install PostgreSQL client tools.")
        except subprocess.TimeoutExpired:
            logger.error("Backup timeout exceeded")
            raise Exception("Backup timeout - database too large or unresponsive")
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            # Clean up partial backup
            if backup_file.exists():
                backup_file.unlink()
            raise

    def create_sqlite_backup(self, db_path: str) -> str:
        """
        Create SQLite database backup

        Args:
            db_path: Path to SQLite database file

        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"backup_{timestamp}.db"

        try:
            # Copy SQLite database file
            shutil.copy2(db_path, backup_file)

            # Create metadata
            metadata = {
                'timestamp': timestamp,
                'type': 'sqlite',
                'size_bytes': backup_file.stat().st_size,
                'created_at': datetime.now().isoformat()
            }

            metadata_file = self.backup_dir / f"backup_{timestamp}.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.success(f"SQLite backup created: {backup_file}")
            return str(backup_file)

        except Exception as e:
            logger.error(f"SQLite backup failed: {e}")
            if backup_file.exists():
                backup_file.unlink()
            raise

    def list_backups(self) -> list:
        """
        List all available backups

        Returns:
            List of backup info dicts
        """
        backups = []

        for metadata_file in self.backup_dir.glob("backup_*.json"):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)

                # Check if backup file exists
                timestamp = metadata['timestamp']
                backup_file = self.backup_dir / f"backup_{timestamp}.sql"

                if not backup_file.exists():
                    backup_file = self.backup_dir / f"backup_{timestamp}.db"

                if backup_file.exists():
                    metadata['file'] = str(backup_file)
                    backups.append(metadata)

            except Exception as e:
                logger.warning(f"Error reading metadata: {e}")
                continue

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x['timestamp'], reverse=True)

        return backups

    def cleanup_old_backups(self, keep_count: int = 7):
        """
        Remove old backups, keeping only the most recent ones

        Args:
            keep_count: Number of backups to keep
        """
        backups = self.list_backups()

        if len(backups) <= keep_count:
            logger.info(f"Only {len(backups)} backups found, no cleanup needed")
            return

        # Delete old backups
        for backup in backups[keep_count:]:
            try:
                backup_file = Path(backup['file'])
                metadata_file = backup_file.parent / f"{backup_file.stem}.json"

                if backup_file.exists():
                    backup_file.unlink()
                    logger.info(f"Deleted old backup: {backup_file}")

                if metadata_file.exists():
                    metadata_file.unlink()

            except Exception as e:
                logger.error(f"Error deleting backup: {e}")

        logger.success(f"Cleaned up old backups, kept {keep_count} most recent")

    def restore_backup(self, backup_file: str, db_config: Dict[str, Any]):
        """
        Restore database from backup

        Args:
            backup_file: Path to backup file
            db_config: Database configuration
        """
        try:
            backup_path = Path(backup_file)

            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_file}")

            # Use psql to restore
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config.get('password', '')

            cmd = [
                'psql',
                '-h', db_config.get('host', 'localhost'),
                '-p', str(db_config.get('port', 5432)),
                '-U', db_config.get('user', 'postgres'),
                '-d', db_config.get('database', 'video_analytics'),
                '-f', str(backup_path)
            ]

            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                raise Exception(f"psql restore failed: {result.stderr}")

            logger.success(f"Database restored from: {backup_file}")

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise
