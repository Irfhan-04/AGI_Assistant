"""Storage management for cleanup and monitoring."""

import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any
from src.config import STORAGE_CONFIG, SESSIONS_DIR
from src.storage.database import Database
from src.logger import get_logger

logger = get_logger(__name__)


class StorageManager:
    """Manages storage cleanup and monitoring."""
    
    def __init__(self, database: Database):
        """Initialize storage manager.
        
        Args:
            database: Database instance
        """
        self.database = database
        self.config = STORAGE_CONFIG
        logger.info("Storage manager initialized")
    
    def cleanup_old_sessions(self) -> int:
        """Clean up old session data.
        
        Returns:
            Number of sessions cleaned up
        """
        retention_days = self.config["sessions"]["retention_days"]
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        logger.info(f"Cleaning up sessions older than {retention_days} days")
        
        # Get all sessions from database
        sessions = self.database.get_all_sessions()
        
        cleaned_count = 0
        for session in sessions:
            try:
                # Check if session should be deleted
                start_time_str = session.get("start_time")
                if not start_time_str:
                    continue
                
                start_time = datetime.fromisoformat(start_time_str)
                
                # Delete if old and has learned workflow (or delete_after_learning is True)
                should_delete = False
                if start_time < cutoff_date:
                    if self.config["sessions"]["delete_after_learning"]:
                        # Delete if workflow was learned
                        if session.get("learned_workflow_id"):
                            should_delete = True
                    else:
                        # Delete if no workflow was learned
                        if not session.get("learned_workflow_id"):
                            should_delete = True
                
                if should_delete:
                    session_id = session.get("session_id")
                    session_dir = SESSIONS_DIR / session_id
                    
                    if session_dir.exists():
                        # Delete directory
                        shutil.rmtree(session_dir)
                        logger.info(f"Deleted session directory: {session_id}")
                    
                    # Mark as deleted in database
                    self.database.conn.execute(
                        "UPDATE sessions SET deleted = 1, deleted_at = ? WHERE session_id = ?",
                        (datetime.now().isoformat(), session_id)
                    )
                    self.database.conn.commit()
                    
                    cleaned_count += 1
                    
            except Exception as e:
                logger.error(f"Error cleaning up session {session.get('session_id')}: {e}")
        
        logger.info(f"Cleaned up {cleaned_count} old sessions")
        return cleaned_count
    
    def get_storage_usage(self) -> Dict[str, Any]:
        """Get current storage usage statistics.
        
        Returns:
            Dictionary with storage stats
        """
        total_size = 0
        session_count = 0
        
        # Calculate sessions directory size
        if SESSIONS_DIR.exists():
            for session_dir in SESSIONS_DIR.iterdir():
                if session_dir.is_dir():
                    session_count += 1
                    try:
                        for file_path in session_dir.rglob("*"):
                            if file_path.is_file():
                                total_size += file_path.stat().st_size
                    except Exception as e:
                        logger.debug(f"Error calculating size for {session_dir}: {e}")
        
        # Get database size
        db_size = 0
        if self.database.db_path.exists():
            db_size = self.database.db_path.stat().st_size
        
        total_size += db_size
        
        max_size = self.config["max_total_size"]
        usage_percentage = (total_size / max_size) * 100 if max_size > 0 else 0
        
        return {
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "total_size_gb": total_size / (1024 * 1024 * 1024),
            "max_size_bytes": max_size,
            "max_size_gb": max_size / (1024 * 1024 * 1024),
            "usage_percentage": usage_percentage,
            "session_count": session_count,
            "db_size_bytes": db_size
        }
    
    def check_storage_threshold(self) -> bool:
        """Check if storage threshold is exceeded.
        
        Returns:
            True if threshold exceeded
        """
        usage = self.get_storage_usage()
        threshold = self.config["cleanup_triggers"]["storage_threshold"]
        
        return usage["usage_percentage"] >= (threshold * 100)
    
    def compress_screenshots(self, session_dir: Path) -> int:
        """Compress screenshots in a session directory.
        
        Args:
            session_dir: Session directory path
            
        Returns:
            Number of screenshots compressed
        """
        screenshots_dir = session_dir / "screenshots"
        if not screenshots_dir.exists():
            return 0
        
        compressed_count = 0
        quality = self.config["sessions"]["jpeg_quality"]
        
        try:
            from PIL import Image
            
            for screenshot_file in screenshots_dir.glob("*.jpg"):
                try:
                    # Open and re-save with compression
                    img = Image.open(screenshot_file)
                    img.save(screenshot_file, "JPEG", quality=quality, optimize=True)
                    compressed_count += 1
                except Exception as e:
                    logger.debug(f"Error compressing {screenshot_file}: {e}")
            
            logger.info(f"Compressed {compressed_count} screenshots in {session_dir.name}")
        except Exception as e:
            logger.error(f"Error compressing screenshots: {e}")
        
        return compressed_count
    
    def cleanup_if_needed(self) -> bool:
        """Check storage and cleanup if needed.
        
        Returns:
            True if cleanup was performed
        """
        if self.check_storage_threshold():
            logger.info("Storage threshold exceeded, starting cleanup")
            self.cleanup_old_sessions()
            return True
        return False

