"""Desktop automation actions using PyAutoGUI."""

import time
import pyautogui
import pygetwindow as gw
from typing import Optional, Tuple
from src.config import AUTOMATION_CONFIG
from src.logger import get_logger

logger = get_logger(__name__)

# Enable fail-safe (move mouse to corner to abort)
pyautogui.FAILSAFE = AUTOMATION_CONFIG["safety"]["fail_safe"]
pyautogui.PAUSE = AUTOMATION_CONFIG["safety"]["pause_between_actions"]


class DesktopActions:
    """Desktop automation actions wrapper."""
    
    def __init__(self):
        """Initialize desktop actions."""
        self.config = AUTOMATION_CONFIG["safety"]
        logger.info("Desktop actions initialized")
    
    def click(self, x: int, y: int, button: str = "left") -> bool:
        """Click at coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ("left", "right", "middle")
            
        Returns:
            True if successful
        """
        try:
            pyautogui.click(x, y, button=button)
            logger.debug(f"Clicked at ({x}, {y}) with {button} button")
            return True
        except Exception as e:
            logger.error(f"Error clicking at ({x}, {y}): {e}")
            return False
    
    def double_click(self, x: int, y: int) -> bool:
        """Double-click at coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if successful
        """
        try:
            pyautogui.doubleClick(x, y)
            logger.debug(f"Double-clicked at ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Error double-clicking at ({x}, {y}): {e}")
            return False
    
    def right_click(self, x: int, y: int) -> bool:
        """Right-click at coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if successful
        """
        return self.click(x, y, button="right")
    
    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """Type text.
        
        Args:
            text: Text to type
            interval: Delay between keystrokes
            
        Returns:
            True if successful
        """
        try:
            pyautogui.write(text, interval=interval)
            logger.debug(f"Typed text: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """Press a single key.
        
        Args:
            key: Key name (e.g., "enter", "tab", "esc")
            
        Returns:
            True if successful
        """
        try:
            pyautogui.press(key)
            logger.debug(f"Pressed key: {key}")
            return True
        except Exception as e:
            logger.error(f"Error pressing key {key}: {e}")
            return False
    
    def hotkey(self, *keys: str) -> bool:
        """Press a hotkey combination.
        
        Args:
            *keys: Key names (e.g., "ctrl", "s")
            
        Returns:
            True if successful
        """
        try:
            pyautogui.hotkey(*keys)
            logger.debug(f"Pressed hotkey: {'+'.join(keys)}")
            return True
        except Exception as e:
            logger.error(f"Error pressing hotkey {'+'.join(keys)}: {e}")
            return False
    
    def scroll(self, x: int, y: int, clicks: int = 3) -> bool:
        """Scroll at coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            clicks: Number of scroll clicks (positive = up, negative = down)
            
        Returns:
            True if successful
        """
        try:
            pyautogui.scroll(clicks, x=x, y=y)
            logger.debug(f"Scrolled {clicks} clicks at ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Error scrolling at ({x}, {y}): {e}")
            return False
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> bool:
        """Move mouse to coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Movement duration in seconds
            
        Returns:
            True if successful
        """
        try:
            pyautogui.moveTo(x, y, duration=duration)
            logger.debug(f"Moved mouse to ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Error moving mouse to ({x}, {y}): {e}")
            return False
    
    def launch_application(self, app_name: str) -> bool:
        """Launch an application.
        
        Args:
            app_name: Application name or executable path
            
        Returns:
            True if successful
        """
        try:
            import subprocess
            subprocess.Popen(app_name)
            logger.info(f"Launched application: {app_name}")
            time.sleep(2)  # Wait for app to start
            return True
        except Exception as e:
            logger.error(f"Error launching application {app_name}: {e}")
            return False
    
    def close_application(self, window_title: str) -> bool:
        """Close an application window.
        
        Args:
            window_title: Window title to close
            
        Returns:
            True if successful
        """
        try:
            windows = gw.getWindowsWithTitle(window_title)
            if windows:
                windows[0].close()
                logger.info(f"Closed window: {window_title}")
                return True
            else:
                logger.warning(f"Window not found: {window_title}")
                return False
        except Exception as e:
            logger.error(f"Error closing window {window_title}: {e}")
            return False
    
    def switch_to_window(self, window_title: str) -> bool:
        """Switch to a specific window.
        
        Args:
            window_title: Window title to switch to
            
        Returns:
            True if successful
        """
        try:
            windows = gw.getWindowsWithTitle(window_title)
            if windows:
                windows[0].activate()
                logger.info(f"Switched to window: {window_title}")
                time.sleep(0.5)  # Wait for window to activate
                return True
            else:
                logger.warning(f"Window not found: {window_title}")
                return False
        except Exception as e:
            logger.error(f"Error switching to window {window_title}: {e}")
            return False
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen size.
        
        Returns:
            Tuple of (width, height)
        """
        return pyautogui.size()

