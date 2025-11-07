"""Verification module for workflow execution."""

import time
from typing import Optional
from PIL import Image
import mss
import numpy as np
from src.logger import get_logger

logger = get_logger(__name__)


class Verifier:
    """Verifies workflow execution success."""
    
    def __init__(self):
        """Initialize verifier."""
        self.sct = mss.mss()
        logger.info("Verifier initialized")
    
    def capture_screenshot(self) -> Optional[Image.Image]:
        """Capture current screen.
        
        Returns:
            Screenshot image or None
        """
        try:
            screenshot = self.sct.grab(self.sct.monitors[1])
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            return img
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return None
    
    def verify(self, verification_type: str, before: Optional[Image.Image], 
               after: Optional[Image.Image]) -> bool:
        """Verify action success.
        
        Args:
            verification_type: Type of verification to perform
            before: Screenshot before action
            after: Screenshot after action
            
        Returns:
            True if verification passes
        """
        if not before or not after:
            return False
        
        try:
            if "screenshot_comparison" in verification_type.lower() or "visual_change" in verification_type.lower():
                return self._compare_screenshots(before, after)
            elif "no_change" in verification_type.lower():
                return self._compare_screenshots(before, after, expect_change=False)
            else:
                # Default: expect some change
                return self._compare_screenshots(before, after)
        except Exception as e:
            logger.error(f"Error in verification: {e}")
            return False
    
    def _compare_screenshots(self, img1: Image.Image, img2: Image.Image, 
                            expect_change: bool = True) -> bool:
        """Compare two screenshots.
        
        Args:
            img1: First screenshot
            img2: Second screenshot
            expect_change: Whether to expect changes (True) or no changes (False)
            
        Returns:
            True if comparison matches expectation
        """
        try:
            # Convert to grayscale
            gray1 = img1.convert("L")
            gray2 = img2.convert("L")
            
            # Resize if dimensions differ
            if gray1.size != gray2.size:
                gray2 = gray2.resize(gray1.size)
            
            # Calculate difference
            arr1 = np.array(gray1)
            arr2 = np.array(gray2)
            
            diff = np.abs(arr1.astype(int) - arr2.astype(int))
            change_percentage = np.sum(diff > 10) / diff.size  # Threshold of 10
            
            if expect_change:
                # Expect at least 1% change
                return change_percentage > 0.01
            else:
                # Expect less than 1% change
                return change_percentage < 0.01
                
        except Exception as e:
            logger.error(f"Error comparing screenshots: {e}")
            return False
    
    def find_text_in_screenshot(self, screenshot: Image.Image, text: str) -> bool:
        """Find text in screenshot using OCR.
        
        Args:
            screenshot: Screenshot image
            text: Text to find
            
        Returns:
            True if text found
        """
        try:
            from src.processing.ocr_engine import OCREngine
            ocr = OCREngine()
            
            # Save screenshot temporarily
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                screenshot.save(tmp.name)
                found = ocr.find_text_in_screenshot(Path(tmp.name), text)
                Path(tmp.name).unlink()
            
            return found is not None
        except Exception as e:
            logger.error(f"Error finding text in screenshot: {e}")
            return False

