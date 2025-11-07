"""Learning engine that aggregates patterns and generates workflow suggestions."""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.intelligence.pattern_detector import PatternDetector
from src.intelligence.workflow_generator import WorkflowGenerator
from src.storage.database import Database
from src.config import INTELLIGENCE_CONFIG, SESSIONS_DIR
from src.logger import get_logger

logger = get_logger(__name__)


class LearningEngine:
    """Multi-session learning engine that aggregates patterns and generates workflows."""
    
    def __init__(self, database: Database):
        """Initialize learning engine.
        
        Args:
            database: Database instance for storing workflows
        """
        self.database = database
        self.pattern_detector = PatternDetector()
        self.workflow_generator = WorkflowGenerator()
        self.config = INTELLIGENCE_CONFIG
        logger.info("Learning engine initialized")
    
    def learn_from_session(self, session_dir: Path) -> Optional[Dict[str, Any]]:
        """Learn from a single session and generate workflow if pattern detected.
        
        Args:
            session_dir: Path to session directory
            
        Returns:
            Generated workflow dictionary or None
        """
        logger.info(f"Learning from session: {session_dir.name}")
        
        # Load timeline
        timeline_file = session_dir / "timeline.json"
        if not timeline_file.exists():
            logger.warning(f"Timeline not found for session: {session_dir.name}")
            return None
        
        try:
            with open(timeline_file, 'r', encoding='utf-8') as f:
                timeline = json.load(f)
        except Exception as e:
            logger.error(f"Error loading timeline: {e}")
            return None
        
        # Check for similar sessions
        similar_sessions = self._find_similar_sessions(timeline)
        
        if len(similar_sessions) >= self.config["pattern_detection"]["min_occurrences"] - 1:
            # Pattern detected - generate workflow
            logger.info(f"Pattern detected across {len(similar_sessions) + 1} sessions")
            
            # Combine all similar sessions
            all_sessions = similar_sessions + [timeline]
            
            # Generate workflow
            workflow = self.workflow_generator.generate_workflow(timeline)
            
            # Enhance workflow with pattern information
            workflow["pattern_confidence"] = self._calculate_pattern_confidence(all_sessions)
            workflow["sessions_used"] = [s.get("session_id", "") for s in all_sessions]
            
            # Save to database
            workflow_id = self.database.add_workflow(workflow)
            workflow["id"] = workflow_id
            
            logger.info(f"Generated workflow: {workflow.get('workflow_name')} (ID: {workflow_id})")
            return workflow
        
        logger.info("No pattern detected yet - need more similar sessions")
        return None
    
    def learn_from_multiple_sessions(self, session_dirs: List[Path]) -> List[Dict[str, Any]]:
        """Learn from multiple sessions and detect patterns.
        
        Args:
            session_dirs: List of session directory paths
            
        Returns:
            List of generated workflows
        """
        logger.info(f"Learning from {len(session_dirs)} sessions")
        
        # Load all timelines
        timelines = []
        for session_dir in session_dirs:
            timeline_file = session_dir / "timeline.json"
            if timeline_file.exists():
                try:
                    with open(timeline_file, 'r', encoding='utf-8') as f:
                        timeline = json.load(f)
                        timeline["session_id"] = session_dir.name
                        timelines.append(timeline)
                except Exception as e:
                    logger.error(f"Error loading timeline from {session_dir}: {e}")
        
        if len(timelines) < 2:
            logger.info("Need at least 2 sessions to detect patterns")
            return []
        
        # Detect patterns
        patterns = self.pattern_detector.detect_patterns(timelines)
        
        # Generate workflows for each pattern
        workflows = []
        for pattern in patterns:
            # Find representative timeline
            representative_timeline = self._find_representative_timeline(timelines, pattern)
            
            if representative_timeline:
                # Generate workflow
                workflow = self.workflow_generator.generate_workflow(representative_timeline)
                
                # Enhance with pattern info
                workflow["pattern_confidence"] = pattern.get("confidence", 0.0)
                workflow["sessions_used"] = pattern.get("sessions", [])
                
                # Save to database
                workflow_id = self.database.add_workflow(workflow)
                workflow["id"] = workflow_id
                
                workflows.append(workflow)
                logger.info(f"Generated workflow from pattern: {workflow.get('workflow_name')}")
        
        return workflows
    
    def _find_similar_sessions(self, timeline: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find sessions similar to the given timeline.
        
        Args:
            timeline: Timeline dictionary
            
        Returns:
            List of similar timeline dictionaries
        """
        # Get all sessions from database
        all_sessions = self.database.get_all_sessions()
        
        # Load timelines for sessions that have learned workflows
        similar_sessions = []
        for session in all_sessions:
            if session.get("learned_workflow_id"):
                session_id = session.get("session_id")
                session_dir = SESSIONS_DIR / session_id if session_id else None
                
                if session_dir and session_dir.exists():
                    timeline_file = session_dir / "timeline.json"
                    if timeline_file.exists():
                        try:
                            with open(timeline_file, 'r', encoding='utf-8') as f:
                                session_timeline = json.load(f)
                            
                            # Check similarity (simplified)
                            similarity = self._calculate_timeline_similarity(timeline, session_timeline)
                            if similarity >= self.config["pattern_detection"]["min_similarity"]:
                                similar_sessions.append(session_timeline)
                        except Exception as e:
                            logger.debug(f"Error loading timeline for session {session_id}: {e}")
        
        return similar_sessions
    
    def _calculate_timeline_similarity(self, timeline1: Dict[str, Any], 
                                       timeline2: Dict[str, Any]) -> float:
        """Calculate similarity between two timelines.
        
        Args:
            timeline1: First timeline
            timeline2: Second timeline
            
        Returns:
            Similarity score between 0 and 1
        """
        entries1 = timeline1.get("timeline", [])
        entries2 = timeline2.get("timeline", [])
        
        # Extract action sequences
        seq1 = [e.get("event_type", "") for e in entries1 if e.get("type") == "event"]
        seq2 = [e.get("event_type", "") for e in entries2 if e.get("type") == "event"]
        
        # Use pattern detector's similarity calculation
        return self.pattern_detector._calculate_similarity(seq1, seq2)
    
    def _find_representative_timeline(self, timelines: List[Dict[str, Any]], 
                                      pattern: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find the most representative timeline for a pattern.
        
        Args:
            timelines: List of timeline dictionaries
            pattern: Pattern dictionary
            
        Returns:
            Most representative timeline or None
        """
        pattern_sessions = pattern.get("sessions", [])
        
        for timeline in timelines:
            if timeline.get("session_id") in pattern_sessions:
                return timeline
        
        return timelines[0] if timelines else None
    
    def _calculate_pattern_confidence(self, sessions: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on number of similar sessions.
        
        Args:
            sessions: List of session timelines
            
        Returns:
            Confidence score between 0 and 1
        """
        num_sessions = len(sessions)
        min_occurrences = self.config["pattern_detection"]["min_occurrences"]
        
        # Base confidence increases with more occurrences
        base_confidence = min(0.8, 0.5 + (num_sessions - min_occurrences) * 0.1)
        
        return base_confidence

