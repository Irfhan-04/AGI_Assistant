"""
AGI Assistant - Round 2: Automation Executor
Executes learned workflows using pyautogui
"""

import json
import time
import pyautogui
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# Safety settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.5  # Pause between actions

class WorkflowExecutor:
    """Executes automated workflows based on JSON definitions"""
    
    def __init__(self):
        self.is_running = False
        
    def load_workflow(self, workflow_file):
        """Load workflow from JSON file"""
        with open(workflow_file, 'r') as f:
            return json.load(f)
    
    def execute_workflow(self, workflow, callback=None):
        """Execute a workflow step by step"""
        self.is_running = True
        
        try:
            if callback:
                callback(f"Starting workflow: {workflow.get('description', 'Unknown')}")
            
            actions = workflow.get('actions', [])
            
            for i, action in enumerate(actions):
                if not self.is_running:
                    break
                    
                if callback:
                    callback(f"Step {i+1}/{len(actions)}: {action}")
                
                # Execute action based on type
                self._execute_action(action)
                time.sleep(1)  # Pause between steps
                
            if callback:
                callback("✅ Workflow completed successfully!")
                
        except Exception as e:
            if callback:
                callback(f"❌ Error: {str(e)}")
        finally:
            self.is_running = False
    
    def stop(self):
        """Stop execution"""
        self.is_running = False
    
    def _execute_action(self, action):
        """Execute a single action"""
        action_lower = action.lower()
        
        # Example: Excel workflow
        if "open excel" in action_lower:
            # Windows
            pyautogui.press('win')
            time.sleep(0.5)
            pyautogui.write('excel', interval=0.1)
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(2)  # Wait for app to open
            
        elif "enter data" in action_lower:
            # Type some sample data
            pyautogui.write('Sample Data', interval=0.1)
            pyautogui.press('tab')
            pyautogui.write('123', interval=0.1)
            
        elif "save file" in action_lower:
            pyautogui.hotkey('ctrl', 's')
            time.sleep(0.5)
            pyautogui.write('automated_report', interval=0.1)
            pyautogui.press('enter')
            
        # Browser workflow
        elif "open web browser" in action_lower or "open browser" in action_lower:
            pyautogui.press('win')
            time.sleep(0.5)
            pyautogui.write('chrome', interval=0.1)
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(2)
            
        elif "navigate" in action_lower or "search" in action_lower:
            pyautogui.hotkey('ctrl', 'l')  # Focus address bar
            time.sleep(0.3)
            pyautogui.write('https://www.google.com', interval=0.05)
            pyautogui.press('enter')
            
        # File management
        elif "open folder" in action_lower:
            pyautogui.press('win')
            time.sleep(0.5)
            pyautogui.write('explorer', interval=0.1)
            time.sleep(0.5)
            pyautogui.press('enter')
            
        else:
            # Generic action - just log it
            print(f"Action: {action}")

class AutomationGUI:
    """GUI for workflow automation"""
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("AGI Assistant - Workflow Automation")
        self.window.geometry("700x500")
        
        self.executor = WorkflowExecutor()
        self.workflows = []
        
        self.setup_ui()
        self.load_workflows()
        
    def setup_ui(self):
        # Title
        title = tk.Label(
            self.window,
            text="🤖 Workflow Automation",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=20)
        
        # Workflow list
        list_frame = ttk.Frame(self.window)
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        tk.Label(list_frame, text="Detected Workflows:", font=("Arial", 12)).pack(anchor=tk.W)
        
        self.workflow_listbox = tk.Listbox(list_frame, height=10, font=("Arial", 10))
        self.workflow_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(pady=10)
        
        self.execute_btn = tk.Button(
            btn_frame,
            text="▶ Execute Selected",
            command=self.execute_selected,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12),
            padx=20,
            pady=5
        )
        self.execute_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(
            btn_frame,
            text="⏹ Stop",
            command=self.stop_execution,
            bg="#f44336",
            fg="white",
            font=("Arial", 12),
            padx=20,
            pady=5,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = tk.Label(
            self.window,
            text="Ready to automate",
            font=("Arial", 10),
            fg="green"
        )
        self.status_label.pack(pady=10)
        
        # Warning
        warning = tk.Label(
            self.window,
            text="⚠️ Move mouse to top-left corner to emergency stop",
            font=("Arial", 9),
            fg="orange"
        )
        warning.pack(pady=5)
        
    def load_workflows(self):
        """Load all detected workflows"""
        workflow_dir = Path("agi_data/workflows")
        workflow_files = sorted(workflow_dir.glob("*.json"))
        
        self.workflows = []
        self.workflow_listbox.delete(0, tk.END)
        
        for wf_file in workflow_files:
            with open(wf_file, 'r') as f:
                wf = json.load(f)
                self.workflows.append((wf_file, wf))
                self.workflow_listbox.insert(
                    tk.END,
                    f"{wf.get('description', 'Unknown')} - {wf.get('timestamp', '')[:10]}"
                )
    
    def execute_selected(self):
        """Execute the selected workflow"""
        selection = self.workflow_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a workflow to execute")
            return
        
        idx = selection[0]
        _, workflow = self.workflows[idx]
        
        # Confirm
        response = messagebox.askyesno(
            "Confirm Execution",
            f"Execute workflow: {workflow.get('description')}?\n\n"
            f"Actions:\n" + "\n".join(f"• {a}" for a in workflow.get('actions', []))
        )
        
        if response:
            self.execute_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            # Give user time to position windows
            for i in range(3, 0, -1):
                self.status_label.config(text=f"Starting in {i}...")
                self.window.update()
                time.sleep(1)
            
            # Execute in thread
            import threading
            threading.Thread(
                target=self.executor.execute_workflow,
                args=(workflow, self.update_status),
                daemon=True
            ).start()
    
    def stop_execution(self):
        """Stop workflow execution"""
        self.executor.stop()
        self.execute_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped")
    
    def update_status(self, message):
        """Update status label (called from executor)"""
        self.status_label.config(text=message)
        if "completed" in message.lower() or "error" in message.lower():
            self.execute_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = AutomationGUI()
    app.run()