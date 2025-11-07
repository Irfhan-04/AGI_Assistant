"""Session manager orchestrates all observation components."""

import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from src.observation.screen_recorder import ScreenRecorder
from src.observation.audio_recorder import AudioRecorder
from src.observation.event_tracker import EventTracker
from src.config import SESSIONS_DIR
from src.logger import get_logger

logger = get_logger(__name__)


class SessionManager:
    """Manages recording sessions and coordinates all observation components."""
    
    def __init__(self):
        """Initialize session manager."""
        self.current_session_id: Optional[str] = None
        self.current_session_dir: Optional[Path] = None
        
        self.screen_recorder: Optional[ScreenRecorder] = None
        self.audio_recorder: Optional[AudioRecorder] = None
        self.event_tracker: Optional[EventTracker] = None
        
        self.start_time: Optional[float] = None
        self.is_recording = False
        
        logger.info("Session manager initialized")
    
    def start_session(self) -> str:
        """Start a new recording session.
        
        Returns:
            Session ID string
        """
        if self.is_recording:
            logger.warning("Session already in progress")
            return self.current_session_id or ""
        
        # Generate session ID
        self.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session_dir = SESSIONS_DIR / self.current_session_id
        self.current_session_dir.mkdir(parents=True, exist_ok=True)
        
        self.start_time = time.time()
        self.is_recording = True
        
        # Initialize recorders
        self.screen_recorder = ScreenRecorder(self.current_session_dir)
        self.audio_recorder = AudioRecorder(self.current_session_dir)
        self.event_tracker = EventTracker(self.current_session_dir)
        
        # Start all recorders
        self.screen_recorder.start()
        self.audio_recorder.start()
        self.event_tracker.start()
        
        logger.info(f"Started recording session: {self.current_session_id}")
        return self.current_session_id
    
    def stop_session(self) -> Dict[str, Any]:
        """Stop current recording session.
        
        Returns:
            Dictionary with session summary
        """
        if not self.is_recording:
            logger.warning("No active session to stop")
            return {}
        
        # Stop all recorders
        if self.screen_recorder:
            self.screen_recorder.stop()
        if self.audio_recorder:
            self.audio_recorder.stop()
        if self.event_tracker:
            self.event_tracker.stop()
        
        # Calculate duration
        duration = int(time.time() - self.start_time) if self.start_time else 0
        
        # Get stats from all recorders
        screen_stats = self.screen_recorder.get_stats() if self.screen_recorder else {}
        audio_stats = self.audio_recorder.get_stats() if self.audio_recorder else {}
        event_stats = self.event_tracker.get_stats() if self.event_tracker else {}
        
        # Calculate storage size
        storage_size = self._calculate_storage_size()
        
        # Create session summary
        session_summary = {
            "session_id": self.current_session_id,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
            "end_time": datetime.now().isoformat(),
            "duration": duration,
            "screenshots_count": screen_stats.get("screenshot_count", 0),
            "audio_clips_count": audio_stats.get("audio_clip_count", 0),
            "events_count": event_stats.get("event_count", 0),
            "storage_size": storage_size,
            "session_dir": str(self.current_session_dir)
        }
        
        self.is_recording = False
        self.current_session_id = None
        self.current_session_dir = None
        
        logger.info(f"Stopped recording session. Duration: {duration}s")
        return session_summary
    
    def _calculate_storage_size(self) -> int:
        """Calculate total storage size of session directory.
        
        Returns:
            Size in bytes
        """
        if not self.current_session_dir or not self.current_session_dir.exists():
            return 0
        
        total_size = 0
        try:
            for file_path in self.current_session_dir.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception as e:
            logger.error(f"Error calculating storage size: {e}")
        
        return total_size
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics.
        
        Returns:
            Dictionary with current stats
        """
        if not self.is_recording:
            return {}
        
        screen_stats = self.screen_recorder.get_stats() if self.screen_recorder else {}
        audio_stats = self.audio_recorder.get_stats() if self.audio_recorder else {}
        event_stats = self.event_tracker.get_stats() if self.event_tracker else {}
        
        elapsed = int(time.time() - self.start_time) if self.start_time else 0
        
        return {
            "session_id": self.current_session_id,
            "elapsed_seconds": elapsed,
            "screenshots": screen_stats.get("screenshot_count", 0),
            "audio_clips": audio_stats.get("audio_clip_count", 0),
            "events": event_stats.get("event_count", 0),
            "is_recording": self.is_recording
        }
    
    def get_current_session_dir(self) -> Optional[Path]:
        """Get current session directory.
        
        Returns:
            Path to session directory or None
        """
        return self.current_session_dir

