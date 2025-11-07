"""Workflow generator that uses LLM to create workflows from timeline data."""

import json
from typing import Dict, Any, List
from src.intelligence.llm_interface import LLMInterface
from src.config import INTELLIGENCE_CONFIG
from src.logger import get_logger

logger = get_logger(__name__)


class WorkflowGenerator:
    """Generates automatable workflows from timeline data using LLM."""
    
    def __init__(self):
        """Initialize workflow generator."""
        self.llm = LLMInterface()
        self.config = INTELLIGENCE_CONFIG["workflow_generation"]
        logger.info("Workflow generator initialized")
    
    def generate_workflow(self, timeline: Dict[str, Any]) -> Dict[str, Any]:
        """Generate workflow from timeline data.
        
        Args:
            timeline: Unified timeline dictionary
            
        Returns:
            Generated workflow dictionary
        """
        logger.info("Generating workflow from timeline")
        
        # Prepare prompt
        prompt = self._create_workflow_prompt(timeline)
        system_prompt = self._get_system_prompt()
        
        # Generate workflow JSON
        workflow_json = self.llm.generate_json(prompt, system_prompt)
        
        # Validate and enhance workflow
        workflow = self._validate_workflow(workflow_json, timeline)
        
        logger.info(f"Generated workflow: {workflow.get('workflow_name', 'Unknown')}")
        return workflow
    
    def _create_workflow_prompt(self, timeline: Dict[str, Any]) -> str:
        """Create prompt for workflow generation.
        
        Args:
            timeline: Timeline dictionary
            
        Returns:
            Prompt string
        """
        # Extract key information from timeline
        entries = timeline.get("timeline", [])[:self.config["max_timeline_length"]]
        transcript = timeline.get("transcript", "")
        
        # Format timeline entries
        timeline_text = ""
        for entry in entries:
            timestamp = entry.get("timestamp", "")
            entry_type = entry.get("type", "")
            
            if entry_type == "event":
                event_type = entry.get("event_type", "")
                data = entry.get("data", {})
                timeline_text += f"{timestamp} - {event_type}: {json.dumps(data)}\n"
            elif entry_type == "ocr":
                text = entry.get("text", "")[:100]  # Limit text length
                timeline_text += f"{timestamp} - OCR Text: {text}\n"
            elif entry_type == "transcript":
                text = entry.get("text", "")[:500]  # Limit text length
                timeline_text += f"{timestamp} - Audio: {text}\n"
        
        prompt = f"""You are analyzing desktop activity to build automatable workflows.

CONTEXT:
Session: {timeline.get('session_id', 'Unknown')}
Duration: {len(entries)} events recorded
Transcript: {transcript[:500] if transcript else 'None'}

TIMELINE:
{timeline_text}

TASK:
Generate a JSON workflow that captures this as an automatable task.

OUTPUT FORMAT:
{{
  "workflow_name": "Descriptive name",
  "description": "What this workflow does",
  "confidence": 0.0-1.0,
  "category": "excel|browser|file_ops|general",
  "estimated_time_manual": "X seconds",
  "estimated_time_auto": "Y seconds",
  "steps": [
    {{
      "step_number": 1,
      "action_type": "launch_app|click|type|save|hotkey|etc",
      "target": "What to interact with",
      "value": "What to input (if applicable)",
      "wait_after": milliseconds,
      "verification": "How to confirm success"
    }}
  ],
  "variables": [
    {{
      "name": "variable_name",
      "type": "auto|user_input",
      "default": "default_value"
    }}
  ],
  "triggers": ["manual", "scheduled", "event-based"]
}}

RULES:
1. Be specific about click locations (use cell references, button names, coordinates)
2. Identify variables (things that change each time)
3. Add verification steps for critical actions
4. Estimate realistic time savings
5. Only output valid JSON, no markdown"""
        
        return prompt
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for LLM.
        
        Returns:
            System prompt string
        """
        return """You are an expert at analyzing user interactions and creating automatable workflows.
You understand desktop applications, web browsers, and file operations.
You create precise, executable workflows that can be automated.
Always output valid JSON."""
    
    def _validate_workflow(self, workflow_json: Dict[str, Any], timeline: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance workflow JSON.
        
        Args:
            workflow_json: Raw workflow JSON from LLM
            timeline: Original timeline data
            
        Returns:
            Validated workflow dictionary
        """
        # Ensure required fields exist
        workflow = {
            "workflow_name": workflow_json.get("workflow_name", "Unnamed Workflow"),
            "description": workflow_json.get("description", ""),
            "confidence": float(workflow_json.get("confidence", 0.5)),
            "category": workflow_json.get("category", "general"),
            "estimated_time_manual": workflow_json.get("estimated_time_manual", "0 seconds"),
            "estimated_time_auto": workflow_json.get("estimated_time_auto", "0 seconds"),
            "steps": workflow_json.get("steps", []),
            "variables": workflow_json.get("variables", []),
            "triggers": workflow_json.get("triggers", ["manual"])
        }
        
        # Validate steps
        validated_steps = []
        for step in workflow["steps"]:
            validated_step = {
                "step_number": step.get("step_number", len(validated_steps) + 1),
                "action_type": step.get("action_type", "unknown"),
                "target": step.get("target", ""),
                "value": step.get("value", ""),
                "wait_after": int(step.get("wait_after", 500)),
                "verification": step.get("verification", "")
            }
            validated_steps.append(validated_step)
        
        workflow["steps"] = validated_steps
        
        # Calculate estimated savings
        try:
            manual_time = self._parse_time(workflow["estimated_time_manual"])
            auto_time = self._parse_time(workflow["estimated_time_auto"])
            workflow["estimated_savings"] = max(0, manual_time - auto_time)
        except:
            workflow["estimated_savings"] = 0
        
        return workflow
    
    def _parse_time(self, time_str: str) -> int:
        """Parse time string to seconds.
        
        Args:
            time_str: Time string like "2 minutes" or "30 seconds"
            
        Returns:
            Time in seconds
        """
        time_str = time_str.lower().strip()
        
        if "minute" in time_str or "min" in time_str:
            try:
                num = float(time_str.split()[0])
                return int(num * 60)
            except:
                pass
        elif "second" in time_str or "sec" in time_str:
            try:
                num = float(time_str.split()[0])
                return int(num)
            except:
                pass
        
        return 0

