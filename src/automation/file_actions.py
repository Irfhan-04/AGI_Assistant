"""File operations automation."""

import shutil
from pathlib import Path
from typing import Optional
from src.logger import get_logger

logger = get_logger(__name__)


class FileActions:
    """File system operations wrapper."""
    
    def __init__(self):
        """Initialize file actions."""
        logger.info("File actions initialized")
    
    def open_file(self, file_path: str) -> bool:
        """Open a file with default application.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if successful
        """
        try:
            import subprocess
            import os
            
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            # Use OS default application
            if os.name == 'nt':  # Windows
                os.startfile(str(file_path_obj))
            elif os.name == 'posix':  # macOS/Linux
                subprocess.Popen(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', str(file_path_obj)])
            
            logger.info(f"Opened file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error opening file {file_path}: {e}")
            return False
    
    def save_file(self, content: str, file_path: str) -> bool:
        """Save content to a file.
        
        Args:
            content: Content to save
            file_path: Path to save file
            
        Returns:
            True if successful
        """
        try:
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path_obj, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Saved file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving file {file_path}: {e}")
            return False
    
    def move_file(self, source: str, destination: str) -> bool:
        """Move a file.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            True if successful
        """
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                logger.error(f"Source file not found: {source}")
                return False
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_path), str(dest_path))
            
            logger.info(f"Moved file from {source} to {destination}")
            return True
        except Exception as e:
            logger.error(f"Error moving file from {source} to {destination}: {e}")
            return False
    
    def rename_file(self, old_path: str, new_path: str) -> bool:
        """Rename a file.
        
        Args:
            old_path: Current file path
            new_path: New file path
            
        Returns:
            True if successful
        """
        try:
            old_path_obj = Path(old_path)
            new_path_obj = Path(new_path)
            
            if not old_path_obj.exists():
                logger.error(f"File not found: {old_path}")
                return False
            
            old_path_obj.rename(new_path_obj)
            logger.info(f"Renamed file from {old_path} to {new_path}")
            return True
        except Exception as e:
            logger.error(f"Error renaming file from {old_path} to {new_path}: {e}")
            return False
    
    def copy_file(self, source: str, destination: str) -> bool:
        """Copy a file.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            True if successful
        """
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                logger.error(f"Source file not found: {source}")
                return False
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(source_path), str(dest_path))
            
            logger.info(f"Copied file from {source} to {destination}")
            return True
        except Exception as e:
            logger.error(f"Error copying file from {source} to {destination}: {e}")
            return False
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if successful
        """
        try:
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                file_path_obj.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            else:
                logger.warning(f"File not found: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file exists
        """
        return Path(file_path).exists()

