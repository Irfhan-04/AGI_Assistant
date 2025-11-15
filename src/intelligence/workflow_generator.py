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
            Generated workflow dictionary with proper structure
        """
        logger.info("Generating workflow from timeline")
        
        # Prepare prompt
        prompt = self._create_workflow_prompt(timeline)
        system_prompt = self._get_system_prompt()
        
        # Generate workflow JSON
        try:
            workflow_json = self.llm.generate_json(prompt, system_prompt)
        except Exception as e:
            logger.error(f"Error generating workflow with LLM: {e}")
            # Fallback to basic workflow
            workflow_json = self._generate_fallback_workflow(timeline)
        
        # Validate and enhance workflow
        workflow = self._validate_workflow(workflow_json, timeline)
        
        logger.info(f"Generated workflow: {workflow.get('workflow_name', 'Unknown')}")
        return workflow
    
    def _create_workflow_prompt(self, timeline: Dict[str, Any]) -> str:
        """Create prompt for workflow generation."""
        entries = timeline.get("timeline", [])[:self.config["max_timeline_length"]]
        transcript = timeline.get("transcript", "")
        
        # Format timeline entries
        timeline_text = ""
        for entry in entries[:20]:  # Limit to first 20 for prompt size
            timestamp = entry.get("timestamp", "")
            entry_type = entry.get("type", "")
            
            if entry_type == "event":
                event_type = entry.get("event_type", "")
                data = entry.get("data", {})
                timeline_text += f"{timestamp} - {event_type}: {json.dumps(data)}\n"
        
        prompt = f"""Analyze this desktop activity and create an automatable workflow.

TIMELINE (first 20 events):
{timeline_text}

AUDIO TRANSCRIPT:
{transcript[:300] if transcript else 'None'}

Create a JSON workflow with this structure:
{{
  "workflow_name": "Descriptive name (e.g. 'Create Excel Sales Report')",
  "description": "What this workflow does",
  "confidence": 0.75,
  "category": "excel",
  "estimated_time_manual": "60 seconds",
  "estimated_time_auto": "10 seconds",
  "steps": [
    {{
      "step_number": 1,
      "action_type": "launch_app",
      "target": "excel.exe",
      "value": "",
      "wait_after": 2000,
      "verification": "window_visible"
    }}
  ],
  "variables": [],
  "triggers": ["manual"]
}}

Output ONLY valid JSON."""
        
        return prompt
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for LLM."""
        return """You are an expert at analyzing user interactions and creating automatable workflows.
Create precise, executable workflows. Always output valid JSON."""
    
    def _generate_fallback_workflow(self, timeline: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a basic fallback workflow if LLM fails."""
        entries = timeline.get("timeline", [])
        
        # Extract basic actions
        steps = []
        step_num = 1
        
        for entry in entries[:10]:  # First 10 events
            if entry.get("type") == "event":
                event_type = entry.get("event_type", "")
                data = entry.get("data", {})
                
                if event_type == "mouse_press":
                    steps.append({
                        "step_number": step_num,
                        "action_type": "click",
                        "target": f"{data.get('x', 0)},{data.get('y', 0)}",
                        "value": "",
                        "wait_after": 500,
                        "verification": ""
                    })
                    step_num += 1
                elif event_type == "key_press":
                    key = data.get("key", "")
                    if len(key) == 1:  # Single character
                        steps.append({
                            "step_number": step_num,
                            "action_type": "type",
                            "target": key,
                            "value": key,
                            "wait_after": 100,
                            "verification": ""
                        })
                        step_num += 1
        
        return {
            "workflow_name": "Recorded Workflow",
            "description": "Automatically captured workflow",
            "confidence": 0.5,
            "category": "general",
            "estimated_time_manual": "60 seconds",
            "estimated_time_auto": "30 seconds",
            "steps": steps,
            "variables": [],
            "triggers": ["manual"]
        }
    
    def _validate_workflow(self, workflow_json: Dict[str, Any], timeline: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance workflow JSON."""
        # Ensure required fields exist with proper names
        workflow = {
            "workflow_name": workflow_json.get("workflow_name", workflow_json.get("name", "Unnamed Workflow")),
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
                "target": str(step.get("target", "")),
                "value": str(step.get("value", "")),
                "wait_after": int(step.get("wait_after", 500)),
                "verification": str(step.get("verification", ""))
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
        """Parse time string to seconds."""
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