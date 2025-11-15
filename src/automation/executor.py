"""Workflow execution engine."""

import time
from typing import Dict, Any
from datetime import datetime
from src.automation.desktop_actions import DesktopActions
from src.automation.browser_actions import BrowserActions
from src.automation.file_actions import FileActions
# from src.automation.verifier import Verifier   # Disabled for Codespaces (no GUI)
from src.logger import get_logger

logger = get_logger(__name__)


# --- Add a dummy verifier for headless environments ---
class DummyVerifier:
    """Fallback verifier for headless environments (no GUI/screenshot checks)."""

    def capture_screenshot(self):
        return None

    def verify(self, verification, before, after):
        logger.debug("Skipping verification (headless mode).")
        return True


class WorkflowExecutor:
    """Executes learned workflows step by step."""

    def __init__(self):
        """Initialize workflow executor."""
        self.desktop = DesktopActions()
        self.browser = BrowserActions()
        self.file = FileActions()

        # Use real Verifier if available, otherwise fallback to DummyVerifier
        try:
            from src.automation.verifier import Verifier
            self.verifier = Verifier()
        except Exception as e:
            self.verifier = DummyVerifier()
            logger.warning(f"Using DummyVerifier (no GUI). Reason: {e}")

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

if __name__ == "__main__":
    import sys, json, os

    logger.info("Starting Workflow Executor in CLI mode...")

    # Check for workflow path argument
    if len(sys.argv) < 2:
        print("Usage: python -m src.automation.executor <workflow.json>")
        sys.exit(1)

    workflow_path = sys.argv[1]

    if not os.path.exists(workflow_path):
        print(f"❌ Workflow file not found: {workflow_path}")
        sys.exit(1)

    # Load workflow JSON
    try:
        with open(workflow_path, "r") as f:
            workflow = json.load(f)
    except Exception as e:
        print(f"❌ Error loading workflow file: {e}")
        sys.exit(1)

    # Execute workflow
    executor = WorkflowExecutor()
    result = executor.execute(workflow)

    # Print results summary
    print("\n============================================================")
    print(f"Workflow '{result['workflow_name']}' completed")
    print(f"✅ Success: {result['success']}")
    print(f"🧩 Steps completed: {result['steps_completed']}/{result['steps_total']}")
    print(f"🕒 Execution time: {result['execution_time']} ms")
    print("============================================================\n")

    for step in result["steps"]:
        status = "✅" if step["success"] else "❌"
        print(f"{status} Step {step['step_number']}: {step['action_type']} → {step['target'] or step['value']}")
