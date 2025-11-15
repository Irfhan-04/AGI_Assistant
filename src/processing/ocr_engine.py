"""OCR engine using pytesseract to extract text from screenshots."""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image
import pytesseract
from src.config import PROCESSING_CONFIG
from src.logger import get_logger

logger = get_logger(__name__)

# Set Tesseract path for Windows if not in PATH
if os.name == 'nt':  # Windows
    tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path


class OCREngine:
    """Extracts text and UI elements from screenshots using OCR."""
    
    def __init__(self):
        """Initialize OCR engine."""
        self.config = PROCESSING_CONFIG["ocr"]
        self.language = self.config["language"]
        self.tesseract_config = self.config["config"]
        
        # Test if Tesseract is available
        try:
            pytesseract.get_tesseract_version()
            logger.info("OCR engine initialized successfully")
        except Exception as e:
            logger.error(f"Tesseract not found. Please install it: {e}")
    
    def extract_text(self, image_path: Path) -> str:
        """Extract text from a single screenshot."""
        if not image_path.exists():
            logger.error(f"Image file not found: {image_path}")
            return ""
        
        try:
            image = Image.open(image_path)
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
        """Extract UI elements with bounding boxes from screenshot."""
        if not image_path.exists():
            return []
        
        try:
            image = Image.open(image_path)
            data = pytesseract.image_to_data(
                image,
                lang=self.language,
                output_type=pytesseract.Output.DICT
            )
            
            ui_elements = []
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                text = data['text'][i].strip()
                if text:
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
            logger.error(f"Error extracting UI elements: {e}", exc_info=True)
            return []
    
    def process_session(self, session_dir: Path, sample_rate: int = 5) -> Dict[str, Any]:
        """Process all screenshots in a session directory."""
        screenshots_dir = session_dir / "screenshots"
        if not screenshots_dir.exists():
            logger.warning(f"Screenshots directory not found: {screenshots_dir}")
            return {"texts": [], "ui_elements": []}
        
        screenshot_files = sorted(screenshots_dir.glob("*.jpg"))
        
        if not screenshot_files:
            logger.info("No screenshots found in session")
            return {"texts": [], "ui_elements": []}
        
        logger.info(f"Processing {len(screenshot_files)} screenshots (sample rate: {sample_rate})")
        
        texts = []
        ui_elements_list = []
        
        for i, screenshot_file in enumerate(screenshot_files):
            if i % sample_rate == 0:
                text = self.extract_text(screenshot_file)
                if text:
                    texts.append({
                        "file": screenshot_file.name,
                        "text": text
                    })
                
                elements = self.extract_ui_elements(screenshot_file)
                if elements:
                    ui_elements_list.append({
                        "file": screenshot_file.name,
                        "elements": elements
                    })
        
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
        """Find specific text in a screenshot and return its location."""
        elements = self.extract_ui_elements(image_path)
        search_text_lower = search_text.lower()
        
        for element in elements:
            if search_text_lower in element["text"].lower():
                return element
        
        return None