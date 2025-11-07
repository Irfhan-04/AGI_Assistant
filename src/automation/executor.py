"""Workflow execution engine."""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.automation.desktop_actions import DesktopActions
from src.automation.browser_actions import BrowserActions
from src.automation.file_actions import FileActions
from src.automation.verifier import Verifier
from src.logger import get_logger

logger = get_logger(__name__)


class WorkflowExecutor:
    """Executes learned workflows step by step."""
    
    def __init__(self):
        """Initialize workflow executor."""
        self.desktop = DesktopActions()
        self.browser = BrowserActions()
        self.file = FileActions()
        self.verifier = Verifier()
        
        # Action handlers mapping
        self.action_handlers = {
            # Desktop actions
            "click": self._handle_click,
            "double_click": self._handle_double_click,
            "right_click": self._handle_right_click,
            "type": self._handle_type,
            "press_key": self._handle_press_key,
            "hotkey": self._handle_hotkey,
            "scroll": self._handle_scroll,
            "move_mouse": self._handle_move_mouse,
            
            # Application actions
            "launch_app": self._handle_launch_app,
            "close_app": self._handle_close_app,
            "switch_window": self._handle_switch_window,
            
            # Browser actions
            "navigate": self._handle_navigate,
            "click_element": self._handle_click_element,
            "fill_form": self._handle_fill_form,
            "select_dropdown": self._handle_select_dropdown,
            
            # File actions
            "open_file": self._handle_open_file,
            "save_file": self._handle_save_file,
            "move_file": self._handle_move_file,
            "rename_file": self._handle_rename_file,
        }
        
        logger.info("Workflow executor initialized")
    
    def execute(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow.
        
        Args:
            workflow: Workflow dictionary
            
        Returns:
            Execution result dictionary
        """
        workflow_name = workflow.get("workflow_name", "Unknown")
        steps = workflow.get("steps", [])
        
        logger.info(f"Executing workflow: {workflow_name} ({len(steps)} steps)")
        
        start_time = datetime.now()
        results = []
        
        for i, step in enumerate(steps, 1):
            step_number = step.get("step_number", i)
            action_type = step.get("action_type", "")
            target = step.get("target", "")
            value = step.get("value", "")
            wait_after = step.get("wait_after", 500)
            verification = step.get("verification", "")
            
            logger.info(f"Step {step_number}/{len(steps)}: {action_type} - {target}")
            
            # Capture screenshot before action
            before_screenshot = self.verifier.capture_screenshot()
            
            # Execute action
            success = False
            error = None
            
            try:
                handler = self.action_handlers.get(action_type)
                if handler:
                    success = handler(target, value)
                else:
                    error = f"Unknown action type: {action_type}"
                    logger.error(error)
            except Exception as e:
                error = str(e)
                logger.error(f"Error executing step {step_number}: {e}", exc_info=True)
            
            # Wait after action
            time.sleep(wait_after / 1000.0)
            
            # Capture screenshot after action
            after_screenshot = self.verifier.capture_screenshot()
            
            # Verify success if verification specified
            if success and verification:
                verification_result = self.verifier.verify(
                    verification,
                    before_screenshot,
                    after_screenshot
                )
                if not verification_result:
                    logger.warning(f"Verification failed for step {step_number}")
                    success = False
            
            # Record step result
            step_result = {
                "step_number": step_number,
                "action_type": action_type,
                "target": target,
                "value": value,
                "success": success,
                "error": error,
                "timestamp": datetime.now().isoformat()
            }
            results.append(step_result)
            
            # Stop if step failed
            if not success:
                logger.error(f"Workflow execution stopped at step {step_number}")
                break
        
        end_time = datetime.now()
        execution_time = int((end_time - start_time).total_seconds() * 1000)
        
        overall_success = all(r["success"] for r in results)
        steps_completed = sum(1 for r in results if r["success"])
        
        execution_result = {
            "workflow_name": workflow_name,
            "workflow_id": workflow.get("id"),
            "started_at": start_time.isoformat(),
            "completed_at": end_time.isoformat(),
            "success": overall_success,
            "steps_completed": steps_completed,
            "steps_total": len(steps),
            "execution_time": execution_time,
            "steps": results,
            "error_message": results[-1]["error"] if results and not overall_success else None
        }
        
        logger.info(f"Workflow execution {'completed successfully' if overall_success else 'failed'}")
        return execution_result
    
    def _handle_click(self, target: str, value: str) -> bool:
        """Handle click action."""
        try:
            x, y = map(int, target.split(","))
            return self.desktop.click(x, y)
        except:
            return False
    
    def _handle_double_click(self, target: str, value: str) -> bool:
        """Handle double-click action."""
        try:
            x, y = map(int, target.split(","))
            return self.desktop.double_click(x, y)
        except:
            return False
    
    def _handle_right_click(self, target: str, value: str) -> bool:
        """Handle right-click action."""
        try:
            x, y = map(int, target.split(","))
            return self.desktop.right_click(x, y)
        except:
            return False
    
    def _handle_type(self, target: str, value: str) -> bool:
        """Handle type action."""
        return self.desktop.type_text(value or target)
    
    def _handle_press_key(self, target: str, value: str) -> bool:
        """Handle press key action."""
        return self.desktop.press_key(target or value)
    
    def _handle_hotkey(self, target: str, value: str) -> bool:
        """Handle hotkey action."""
        keys = (target or value).split("+")
        return self.desktop.hotkey(*keys)
    
    def _handle_scroll(self, target: str, value: str) -> bool:
        """Handle scroll action."""
        try:
            x, y = map(int, target.split(","))
            clicks = int(value) if value else 3
            return self.desktop.scroll(x, y, clicks)
        except:
            return False
    
    def _handle_move_mouse(self, target: str, value: str) -> bool:
        """Handle move mouse action."""
        try:
            x, y = map(int, target.split(","))
            return self.desktop.move_mouse(x, y)
        except:
            return False
    
    def _handle_launch_app(self, target: str, value: str) -> bool:
        """Handle launch app action."""
        return self.desktop.launch_application(target or value)
    
    def _handle_close_app(self, target: str, value: str) -> bool:
        """Handle close app action."""
        return self.desktop.close_application(target or value)
    
    def _handle_switch_window(self, target: str, value: str) -> bool:
        """Handle switch window action."""
        return self.desktop.switch_to_window(target or value)
    
    def _handle_navigate(self, target: str, value: str) -> bool:
        """Handle navigate action."""
        return self.browser.navigate(target or value)
    
    def _handle_click_element(self, target: str, value: str) -> bool:
        """Handle click element action."""
        return self.browser.click_element(target or value)
    
    def _handle_fill_form(self, target: str, value: str) -> bool:
        """Handle fill form action."""
        return self.browser.fill_input(target, value)
    
    def _handle_select_dropdown(self, target: str, value: str) -> bool:
        """Handle select dropdown action."""
        return self.browser.select_option(target, value)
    
    def _handle_open_file(self, target: str, value: str) -> bool:
        """Handle open file action."""
        return self.file.open_file(target or value)
    
    def _handle_save_file(self, target: str, value: str) -> bool:
        """Handle save file action."""
        return self.file.save_file(value or "", target)
    
    def _handle_move_file(self, target: str, value: str) -> bool:
        """Handle move file action."""
        return self.file.move_file(target, value)
    
    def _handle_rename_file(self, target: str, value: str) -> bool:
        """Handle rename file action."""
        return self.file.rename_file(target, value)

