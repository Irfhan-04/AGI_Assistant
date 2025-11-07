"""Data fusion module that merges transcript, OCR, and events into unified timeline."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from src.logger import get_logger

logger = get_logger(__name__)


class DataFusion:
    """Merges multiple data sources into a unified timeline."""
    
    def __init__(self):
        """Initialize data fusion engine."""
        logger.info("Data fusion engine initialized")
    
    def create_timeline(self, session_dir: Path) -> Dict[str, Any]:
        """Create unified timeline from all session data.
        
        Args:
            session_dir: Path to session directory
            
        Returns:
            Dictionary with unified timeline
        """
        logger.info(f"Creating timeline for session: {session_dir.name}")
        
        # Load transcript
        transcript = self._load_transcript(session_dir)
        
        # Load OCR results
        ocr_results = self._load_ocr_results(session_dir)
        
        # Load events
        events = self._load_events(session_dir)
        
        # Create unified timeline
        timeline = self._merge_data(transcript, ocr_results, events)
        
        # Save timeline
        timeline_file = session_dir / "timeline.json"
        try:
            with open(timeline_file, 'w', encoding='utf-8') as f:
                json.dump(timeline, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved timeline to: {timeline_file}")
        except Exception as e:
            logger.error(f"Error saving timeline: {e}")
        
        return timeline
    
    def _load_transcript(self, session_dir: Path) -> str:
        """Load transcript from file.
        
        Args:
            session_dir: Session directory path
            
        Returns:
            Transcript text
        """
        transcript_file = session_dir / "transcript.txt"
        if transcript_file.exists():
            try:
                with open(transcript_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error loading transcript: {e}")
        return ""
    
    def _load_ocr_results(self, session_dir: Path) -> Dict[str, Any]:
        """Load OCR results from file.
        
        Args:
            session_dir: Session directory path
            
        Returns:
            OCR results dictionary
        """
        ocr_file = session_dir / "ocr_results.json"
        if ocr_file.exists():
            try:
                with open(ocr_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading OCR results: {e}")
        return {"texts": [], "ui_elements": []}
    
    def _load_events(self, session_dir: Path) -> List[Dict[str, Any]]:
        """Load events from file.
        
        Args:
            session_dir: Session directory path
            
        Returns:
            List of event dictionaries
        """
        events_file = session_dir / "events.json"
        if events_file.exists():
            try:
                with open(events_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("events", [])
            except Exception as e:
                logger.error(f"Error loading events: {e}")
        return []
    
    def _merge_data(self, transcript: str, ocr_results: Dict[str, Any], 
                   events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge all data sources into unified timeline.
        
        Args:
            transcript: Full transcript text
            ocr_results: OCR results dictionary
            events: List of events
            
        Returns:
            Unified timeline dictionary
        """
        # Parse timestamps and create timeline entries
        timeline_entries = []
        
        # Add events to timeline
        for event in events:
            timestamp = event.get("timestamp")
            if timestamp:
                timeline_entries.append({
                    "timestamp": timestamp,
                    "type": "event",
                    "event_type": event.get("type"),
                    "data": event.get("data", {})
                })
        
        # Add OCR text entries (with approximate timestamps from screenshot filenames)
        for ocr_text in ocr_results.get("texts", []):
            filename = ocr_text.get("file", "")
            # Extract timestamp from filename (format: screenshot_YYYYMMDD_HHMMSS_mmm.jpg)
            timestamp = self._extract_timestamp_from_filename(filename)
            if timestamp:
                timeline_entries.append({
                    "timestamp": timestamp,
                    "type": "ocr",
                    "text": ocr_text.get("text", ""),
                    "source_file": filename
                })
        
        # Add transcript segments (if we can split by time)
        # For now, add full transcript as a single entry at session start
        if transcript:
            timeline_entries.append({
                "timestamp": timeline_entries[0]["timestamp"] if timeline_entries else datetime.now().isoformat(),
                "type": "transcript",
                "text": transcript
            })
        
        # Sort by timestamp
        timeline_entries.sort(key=lambda x: x["timestamp"])
        
        # Create unified timeline structure
        timeline = {
            "session_id": "",  # Will be set by caller
            "total_entries": len(timeline_entries),
            "transcript": transcript,
            "timeline": timeline_entries,
            "summary": {
                "total_events": len(events),
                "total_ocr_texts": len(ocr_results.get("texts", [])),
                "has_transcript": bool(transcript)
            }
        }
        
        return timeline
    
    def _extract_timestamp_from_filename(self, filename: str) -> str:
        """Extract ISO timestamp from screenshot filename.
        
        Args:
            filename: Screenshot filename (e.g., screenshot_20250107_123045_123.jpg)
            
        Returns:
            ISO timestamp string or empty string if parsing fails
        """
        try:
            # Format: screenshot_YYYYMMDD_HHMMSS_mmm.jpg
            parts = filename.replace(".jpg", "").split("_")
            if len(parts) >= 3:
                date_part = parts[1]  # YYYYMMDD
                time_part = parts[2]   # HHMMSS
                
                # Convert to ISO format
                year = date_part[:4]
                month = date_part[4:6]
                day = date_part[6:8]
                hour = time_part[:2]
                minute = time_part[2:4]
                second = time_part[4:6]
                
                return f"{year}-{month}-{day}T{hour}:{minute}:{second}"
        except Exception as e:
            logger.debug(f"Error extracting timestamp from filename {filename}: {e}")
        
        return datetime.now().isoformat()  # Fallback to current time

