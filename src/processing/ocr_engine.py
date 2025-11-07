"""OCR engine using pytesseract to extract text from screenshots."""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image
import pytesseract
from src.config import PROCESSING_CONFIG
from src.logger import get_logger

logger = get_logger(__name__)


class OCREngine:
    """Extracts text and UI elements from screenshots using OCR."""
    
    def __init__(self):
        """Initialize OCR engine."""
        self.config = PROCESSING_CONFIG["ocr"]
        self.language = self.config["language"]
        self.tesseract_config = self.config["config"]
        
        logger.info("OCR engine initialized")
    
    def extract_text(self, image_path: Path) -> str:
        """Extract text from a single screenshot.
        
        Args:
            image_path: Path to screenshot image
            
        Returns:
            Extracted text string
        """
        if not image_path.exists():
            logger.error(f"Image file not found: {image_path}")
            return ""
        
        try:
            # Load image
            image = Image.open(image_path)
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(
                image,
                lang=self.language,
                config=self.tesseract_config
            )
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from {image_path}: {e}", exc_info=True)
            return ""
    
    def extract_ui_elements(self, image_path: Path) -> List[Dict[str, Any]]:
        """Extract UI elements with bounding boxes from screenshot.
        
        Args:
            image_path: Path to screenshot image
            
        Returns:
            List of UI element dictionaries with text and coordinates
        """
        if not image_path.exists():
            return []
        
        try:
            # Load image
            image = Image.open(image_path)
            
            # Get detailed data with bounding boxes
            data = pytesseract.image_to_data(
                image,
                lang=self.language,
                output_type=pytesseract.Output.DICT
            )
            
            # Extract UI elements
            ui_elements = []
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                text = data['text'][i].strip()
                if text:  # Only include non-empty text
                    ui_elements.append({
                        "text": text,
                        "x": data['left'][i],
                        "y": data['top'][i],
                        "width": data['width'][i],
                        "height": data['height'][i],
                        "confidence": data['conf'][i] if data['conf'][i] != -1 else None
                    })
            
            return ui_elements
            
        except Exception as e:
            logger.error(f"Error extracting UI elements from {image_path}: {e}", exc_info=True)
            return []
    
    def process_session(self, session_dir: Path, sample_rate: int = 5) -> Dict[str, Any]:
        """Process all screenshots in a session directory.
        
        Args:
            session_dir: Path to session directory
            sample_rate: Process every Nth screenshot (1 = all, 5 = every 5th)
            
        Returns:
            Dictionary with OCR results
        """
        screenshots_dir = session_dir / "screenshots"
        if not screenshots_dir.exists():
            logger.warning(f"Screenshots directory not found: {screenshots_dir}")
            return {"texts": [], "ui_elements": []}
        
        # Find all screenshot files
        screenshot_files = sorted(screenshots_dir.glob("*.jpg"))
        
        if not screenshot_files:
            logger.info("No screenshots found in session")
            return {"texts": [], "ui_elements": []}
        
        logger.info(f"Processing {len(screenshot_files)} screenshots (sample rate: {sample_rate})")
        
        # Process screenshots (with sampling)
        texts = []
        ui_elements_list = []
        
        for i, screenshot_file in enumerate(screenshot_files):
            if i % sample_rate == 0:  # Sample every Nth screenshot
                # Extract text
                text = self.extract_text(screenshot_file)
                if text:
                    texts.append({
                        "file": screenshot_file.name,
                        "text": text
                    })
                
                # Extract UI elements
                elements = self.extract_ui_elements(screenshot_file)
                if elements:
                    ui_elements_list.append({
                        "file": screenshot_file.name,
                        "elements": elements
                    })
        
        # Save results to JSON
        ocr_results = {
            "texts": texts,
            "ui_elements": ui_elements_list
        }
        
        ocr_file = session_dir / "ocr_results.json"
        try:
            with open(ocr_file, 'w', encoding='utf-8') as f:
                json.dump(ocr_results, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved OCR results to: {ocr_file}")
        except Exception as e:
            logger.error(f"Error saving OCR results: {e}")
        
        return ocr_results
    
    def find_text_in_screenshot(self, image_path: Path, search_text: str) -> Optional[Dict[str, Any]]:
        """Find specific text in a screenshot and return its location.
        
        Args:
            image_path: Path to screenshot image
            search_text: Text to search for
            
        Returns:
            Dictionary with location info or None if not found
        """
        elements = self.extract_ui_elements(image_path)
        
        search_text_lower = search_text.lower()
        for element in elements:
            if search_text_lower in element["text"].lower():
                return element
        
        return None

