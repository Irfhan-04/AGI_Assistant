"""Screen recording module using mss for fast screenshot capture."""

import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable
from PIL import Image
import mss
from src.config import OBSERVATION_CONFIG
from src.logger import get_logger

logger = get_logger(__name__)


class ScreenRecorder:
    """Records screen activity by capturing screenshots at intervals."""
    
    def __init__(self, session_dir: Path, on_screenshot: Optional[Callable] = None):
        """Initialize screen recorder.
        
        Args:
            session_dir: Directory to save screenshots
            on_screenshot: Optional callback when screenshot is taken
        """
        self.session_dir = session_dir
        self.screenshots_dir = session_dir / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        self.on_screenshot = on_screenshot
        self.is_recording = False
        self.recording_thread: Optional[threading.Thread] = None
        
        self.config = OBSERVATION_CONFIG["screenshot"]
        self.interval_ms = self.config["interval_ms"]
        self.quality = self.config["quality"]
        
        self.screenshot_count = 0
        self.last_screenshot: Optional[Image.Image] = None
        
        self.sct = mss.mss()
        logger.info(f"Screen recorder initialized for session: {session_dir.name}")
    
    def start(self):
        """Start recording screenshots."""
        if self.is_recording:
            logger.warning("Screen recording already in progress")
            return
        
        self.is_recording = True
        self.screenshot_count = 0
        self.recording_thread = threading.Thread(target=self._recording_loop, daemon=True)
        self.recording_thread.start()
        logger.info("Screen recording started")
    
    def stop(self):
        """Stop recording screenshots."""
        if not self.is_recording:
            return
        
        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)
        logger.info(f"Screen recording stopped. Total screenshots: {self.screenshot_count}")
    
    def _recording_loop(self):
        """Main recording loop running in separate thread."""
        while self.is_recording:
            try:
                self._capture_screenshot()
                time.sleep(self.interval_ms / 1000.0)
            except Exception as e:
                logger.error(f"Error capturing screenshot: {e}", exc_info=True)
                time.sleep(1.0)  # Wait a bit before retrying
    
    def _capture_screenshot(self):
        """Capture a single screenshot."""
        try:
            # Capture screen
            screenshot = self.sct.grab(self.sct.monitors[1])  # Primary monitor
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
            # Check for activity if configured
            if self.config.get("only_on_activity", False):
                if not self._has_activity(img):
                    return  # Skip if no activity detected
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # milliseconds
            filename = f"screenshot_{timestamp}.jpg"
            filepath = self.screenshots_dir / filename
            
            # Save with compression
            img.save(filepath, "JPEG", quality=self.quality, optimize=True)
            
            self.screenshot_count += 1
            self.last_screenshot = img
            
            # Callback if provided
            if self.on_screenshot:
                try:
                    self.on_screenshot(filepath, timestamp)
                except Exception as e:
                    logger.error(f"Error in screenshot callback: {e}")
            
            logger.debug(f"Captured screenshot: {filename}")
            
        except Exception as e:
            logger.error(f"Error in screenshot capture: {e}", exc_info=True)
    
    def _has_activity(self, current_img: Image.Image) -> bool:
        """Check if there's activity compared to last screenshot.
        
        Args:
            current_img: Current screenshot image
            
        Returns:
            True if activity detected, False otherwise
        """
        if self.last_screenshot is None:
            return True  # First screenshot always counts as activity
        
        try:
            # Simple pixel difference check
            # Convert to grayscale for comparison
            current_gray = current_img.convert("L")
            last_gray = self.last_screenshot.convert("L")
            
            # Resize if dimensions differ
            if current_gray.size != last_gray.size:
                last_gray = last_gray.resize(current_gray.size)
            
            # Calculate difference
            import numpy as np
            current_array = np.array(current_gray)
            last_array = np.array(last_gray)
            
            diff = np.abs(current_array.astype(int) - last_array.astype(int))
            change_percentage = np.sum(diff > 10) / diff.size  # Threshold of 10
            
            # Consider activity if more than 1% of pixels changed
            return change_percentage > 0.01
            
        except Exception as e:
            logger.error(f"Error checking activity: {e}")
            return True  # Default to capturing if check fails
    
    def get_stats(self) -> dict:
        """Get recording statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            "screenshot_count": self.screenshot_count,
            "is_recording": self.is_recording,
            "screenshots_dir": str(self.screenshots_dir)
        }

