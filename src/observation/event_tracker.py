"""Event tracking module for mouse, keyboard, and window changes."""

import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, Dict, Any
from pynput import mouse, keyboard
import psutil
from src.config import OBSERVATION_CONFIG
from src.logger import get_logger

logger = get_logger(__name__)


class EventTracker:
    """Tracks mouse clicks, keyboard input, and window changes."""
    
    def __init__(self, session_dir: Path, on_event: Optional[Callable] = None):
        """Initialize event tracker.
        
        Args:
            session_dir: Directory to save event logs
            on_event: Optional callback when event is captured
        """
        self.session_dir = session_dir
        self.events_file = session_dir / "events.json"
        
        self.on_event = on_event
        self.is_tracking = False
        
        self.config = OBSERVATION_CONFIG["events"]
        self.events: list = []
        self.last_window_title = ""
        
        # Listeners
        self.mouse_listener: Optional[mouse.Listener] = None
        self.keyboard_listener: Optional[keyboard.Listener] = None
        
        logger.info(f"Event tracker initialized for session: {session_dir.name}")
    
    def start(self):
        """Start tracking events."""
        if self.is_tracking:
            logger.warning("Event tracking already in progress")
            return
        
        self.is_tracking = True
        self.events = []
        self.last_window_title = self._get_active_window_title()
        
        # Record initial window
        if self.config.get("capture_window_changes", True):
            self._record_event("window_change", {
                "window_title": self.last_window_title,
                "app_name": self._get_active_app_name()
            })
        
        # Start mouse listener
        if self.config.get("capture_mouse", True):
            self.mouse_listener = mouse.Listener(
                on_click=self._on_mouse_click,
                on_scroll=self._on_mouse_scroll
            )
            self.mouse_listener.start()
        
        # Start keyboard listener
        if self.config.get("capture_keyboard", True):
            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.keyboard_listener.start()
        
        # Start window monitoring thread
        if self.config.get("capture_window_changes", True):
            threading.Thread(target=self._monitor_windows, daemon=True).start()
        
        logger.info("Event tracking started")
    
    def stop(self):
        """Stop tracking events and save to file."""
        if not self.is_tracking:
            return
        
        self.is_tracking = False
        
        # Stop listeners
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        # Save events to file
        self._save_events()
        
        logger.info(f"Event tracking stopped. Total events: {len(self.events)}")
    
    def _on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events."""
        if not self.is_tracking:
            return
        
        event_type = "mouse_press" if pressed else "mouse_release"
        self._record_event(event_type, {
            "x": x,
            "y": y,
            "button": str(button)
        })
    
    def _on_mouse_scroll(self, x, y, dx, dy):
        """Handle mouse scroll events."""
        if not self.is_tracking:
            return
        
        self._record_event("mouse_scroll", {
            "x": x,
            "y": y,
            "dx": dx,
            "dy": dy
        })
    
    def _on_key_press(self, key):
        """Handle keyboard key press events."""
        if not self.is_tracking:
            return
        
        try:
            # Try to get character representation
            if hasattr(key, 'char') and key.char:
                char = key.char
            else:
                char = str(key).replace("Key.", "")
            
            self._record_event("key_press", {
                "key": char,
                "key_name": str(key)
            })
        except Exception as e:
            logger.debug(f"Error processing key press: {e}")
    
    def _on_key_release(self, key):
        """Handle keyboard key release events."""
        # We mainly care about presses, but can track releases too
        pass
    
    def _monitor_windows(self):
        """Monitor active window changes in background thread."""
        while self.is_tracking:
            try:
                current_title = self._get_active_window_title()
                if current_title != self.last_window_title:
                    self._record_event("window_change", {
                        "window_title": current_title,
                        "app_name": self._get_active_app_name()
                    })
                    self.last_window_title = current_title
                
                time.sleep(0.5)  # Check every 500ms
            except Exception as e:
                logger.error(f"Error monitoring windows: {e}")
                time.sleep(1.0)
    
    def _get_active_window_title(self) -> str:
        """Get the title of the currently active window.
        
        Returns:
            Window title string
        """
        try:
            import pygetwindow as gw
            active_windows = gw.getActiveWindow()
            if active_windows:
                return active_windows.title
        except Exception:
            pass
        
        # Fallback: try to get from process
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name']:
                        # This is a simplified approach
                        return proc.info['name']
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            pass
        
        return "Unknown"
    
    def _get_active_app_name(self) -> str:
        """Get the name of the currently active application.
        
        Returns:
            Application name string
        """
        try:
            import pygetwindow as gw
            active_windows = gw.getActiveWindow()
            if active_windows:
                return active_windows.title.split(" - ")[-1]  # Usually app name is last part
        except Exception:
            pass
        
        return "Unknown"
    
    def _record_event(self, event_type: str, data: Dict[str, Any]):
        """Record an event with timestamp.
        
        Args:
            event_type: Type of event (mouse_click, key_press, etc.)
            data: Event data dictionary
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data
        }
        
        self.events.append(event)
        
        # Callback if provided
        if self.on_event:
            try:
                self.on_event(event)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")
    
    def _save_events(self):
        """Save events to JSON file."""
        try:
            with open(self.events_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "session_id": self.session_dir.name,
                    "total_events": len(self.events),
                    "events": self.events
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(self.events)} events to {self.events_file}")
        except Exception as e:
            logger.error(f"Error saving events: {e}", exc_info=True)
    
    def get_stats(self) -> dict:
        """Get tracking statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            "event_count": len(self.events),
            "is_tracking": self.is_tracking,
            "events_file": str(self.events_file)
        }

