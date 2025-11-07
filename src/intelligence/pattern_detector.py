"""Pattern detection to find repetitive action sequences across sessions."""

import json
from typing import List, Dict, Any, Tuple
from datetime import datetime
from src.config import INTELLIGENCE_CONFIG
from src.logger import get_logger

logger = get_logger(__name__)


class PatternDetector:
    """Detects repetitive patterns across multiple sessions."""
    
    def __init__(self):
        """Initialize pattern detector."""
        self.config = INTELLIGENCE_CONFIG["pattern_detection"]
        self.min_similarity = self.config["min_similarity"]
        self.min_occurrences = self.config["min_occurrences"]
        logger.info("Pattern detector initialized")
    
    def detect_patterns(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect patterns across multiple sessions.
        
        Args:
            sessions: List of session dictionaries with timeline data
            
        Returns:
            List of detected patterns
        """
        if len(sessions) < 2:
            logger.info("Need at least 2 sessions to detect patterns")
            return []
        
        logger.info(f"Detecting patterns across {len(sessions)} sessions")
        
        # Extract action sequences from each session
        sequences = []
        for session in sessions:
            sequence = self._extract_action_sequence(session)
            if sequence:
                sequences.append({
                    "session_id": session.get("session_id", ""),
                    "sequence": sequence
                })
        
        # Find similar sequences
        patterns = []
        for i, seq1_data in enumerate(sequences):
            for j, seq2_data in enumerate(sequences[i+1:], start=i+1):
                similarity = self._calculate_similarity(
                    seq1_data["sequence"],
                    seq2_data["sequence"]
                )
                
                if similarity >= self.min_similarity:
                    # Found a potential pattern
                    pattern = {
                        "sessions": [seq1_data["session_id"], seq2_data["session_id"]],
                        "similarity": similarity,
                        "sequence": seq1_data["sequence"],  # Use first sequence as template
                        "occurrences": 2
                    }
                    patterns.append(pattern)
        
        # Group patterns and count occurrences
        grouped_patterns = self._group_patterns(patterns)
        
        # Filter by minimum occurrences
        filtered_patterns = [
            p for p in grouped_patterns 
            if p["occurrences"] >= self.min_occurrences
        ]
        
        # Calculate confidence scores
        for pattern in filtered_patterns:
            pattern["confidence"] = self._calculate_confidence(pattern)
        
        # Sort by confidence
        filtered_patterns.sort(key=lambda x: x["confidence"], reverse=True)
        
        logger.info(f"Detected {len(filtered_patterns)} patterns")
        return filtered_patterns
    
    def _extract_action_sequence(self, session: Dict[str, Any]) -> List[str]:
        """Extract action sequence from session timeline.
        
        Args:
            session: Session dictionary with timeline
            
        Returns:
            List of action strings
        """
        timeline = session.get("timeline", {})
        entries = timeline.get("timeline", [])
        
        sequence = []
        for entry in entries:
            if entry.get("type") == "event":
                event_type = entry.get("event_type", "")
                data = entry.get("data", {})
                
                # Create action string
                if event_type == "mouse_press":
                    action = f"click({data.get('x')},{data.get('y')})"
                elif event_type == "key_press":
                    action = f"type({data.get('key', '')})"
                elif event_type == "window_change":
                    action = f"switch_window({data.get('window_title', '')})"
                else:
                    action = f"{event_type}({json.dumps(data)})"
                
                sequence.append(action)
        
        return sequence
    
    def _calculate_similarity(self, seq1: List[str], seq2: List[str]) -> float:
        """Calculate similarity between two sequences using Levenshtein distance.
        
        Args:
            seq1: First sequence
            seq2: Second sequence
            
        Returns:
            Similarity score between 0 and 1
        """
        if not seq1 or not seq2:
            return 0.0
        
        # Use Levenshtein distance
        distance = self._levenshtein_distance(seq1, seq2)
        max_len = max(len(seq1), len(seq2))
        
        if max_len == 0:
            return 1.0
        
        similarity = 1.0 - (distance / max_len)
        return similarity
    
    def _levenshtein_distance(self, seq1: List[str], seq2: List[str]) -> int:
        """Calculate Levenshtein distance between two sequences.
        
        Args:
            seq1: First sequence
            seq2: Second sequence
            
        Returns:
            Edit distance
        """
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = min(
                        dp[i-1][j] + 1,      # deletion
                        dp[i][j-1] + 1,      # insertion
                        dp[i-1][j-1] + 1     # substitution
                    )
        
        return dp[m][n]
    
    def _group_patterns(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group similar patterns together.
        
        Args:
            patterns: List of pattern dictionaries
            
        Returns:
            Grouped patterns with occurrence counts
        """
        grouped = []
        
        for pattern in patterns:
            # Check if similar pattern already exists
            found = False
            for existing in grouped:
                similarity = self._calculate_similarity(
                    pattern["sequence"],
                    existing["sequence"]
                )
                
                if similarity >= self.min_similarity:
                    # Merge into existing pattern
                    existing["sessions"].extend(pattern["sessions"])
                    existing["occurrences"] += 1
                    found = True
                    break
            
            if not found:
                grouped.append(pattern)
        
        return grouped
    
    def _calculate_confidence(self, pattern: Dict[str, Any]) -> float:
        """Calculate confidence score for a pattern.
        
        Args:
            pattern: Pattern dictionary
            
        Returns:
            Confidence score between 0 and 1
        """
        # Base confidence from similarity
        similarity = pattern.get("similarity", 0.0)
        
        # Boost confidence based on occurrences
        occurrences = pattern.get("occurrences", 0)
        occurrence_boost = min(0.3, (occurrences - self.min_occurrences) * 0.1)
        
        # Boost confidence if sequence is longer (more specific)
        sequence_len = len(pattern.get("sequence", []))
        length_boost = min(0.2, sequence_len / 50.0)
        
        confidence = similarity + occurrence_boost + length_boost
        return min(1.0, confidence)

