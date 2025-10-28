"""
AGI Assistant - Round 2: Enhanced Automation Executor
Executes learned workflows with better error handling and safety features
"""

import json
import time
import platform
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

# Try importing pyautogui with graceful fallback
try:
    import pyautogui
    # Safety settings
    pyautogui.FAILSAFE = True  # Move mouse to corner to abort
    pyautogui.PAUSE = 0.5  # Pause between actions
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("⚠️ pyautogui not installed. Automation disabled.")


class WorkflowExecutor:
    """Enhanced workflow executor with better error handling and platform support"""
    
    def __init__(self, log_callback=None):
        self.is_running = False
        self.paused = False
        self.log_callback = log_callback
        self.system = platform.system()
        self.available = PYAUTOGUI_AVAILABLE
        
    def log(self, message):
        """Send log messages to GUI"""
        if self.log_callback:
            self.log_callback(message)
        print(message)
        
    def load_workflow(self, workflow_file):
        """Load and validate workflow from JSON file"""
        try:
            with open(workflow_file, 'r') as f:
                workflow = json.load(f)
            
            # Validate workflow structure
            required_fields = ['description', 'actions']
            for field in required_fields:
                if field not in workflow:
                    raise ValueError(f"Missing required field: {field}")
            
            return workflow
        except json.JSONDecodeError as e:
            self.log(f"Invalid JSON in workflow file: {e}")
            return None
        except Exception as e:
            self.log(f"Error loading workflow: {e}")
            return None
    
    def execute_workflow(self, workflow, callback=None):
        """Execute a workflow step by step with safety checks"""
        if not self.available:
            if callback:
                callback("❌ Automation unavailable (pyautogui not installed)")
            return
        
        self.is_running = True
        self.paused = False
        
        try:
            if callback:
                callback(f"🚀 Starting: {workflow.get('description', 'Unknown workflow')}")
                callback("")
            
            actions = workflow.get('actions', [])
            
            if not actions:
                if callback:
                    callback("⚠️ No actions defined in workflow")
                return
            
            for i, action in enumerate(actions):
                # Check if stopped
                if not self.is_running:
                    if callback:
                        callback("⏹ Execution stopped by user")
                    break
                
                # Check if paused
                while self.paused and self.is_running:
                    time.sleep(0.1)
                
                if callback:
                    callback(f"[{i+1}/{len(actions)}] {action}")
                
                # Execute action with error handling
                try:
                    self._execute_action(action)
                    time.sleep(1)  # Pause between steps for stability
                except Exception as e:
                    if callback:
                        callback(f"   ⚠️ Error: {str(e)}")
                    self.log(f"Action failed: {action} - {e}")
                    
            if self.is_running and callback:
                callback("")
                callback("✅ Workflow completed successfully!")
                
        except KeyboardInterrupt:
            if callback:
                callback("⚠️ Execution interrupted")
        except Exception as e:
            if callback:
                callback(f"❌ Critical error: {str(e)}")
            self.log(f"Execution error: {e}")
        finally:
            self.is_running = False
            self.paused = False
    
    def pause(self):
        """Pause execution"""
        self.paused = True
    
    def resume(self):
        """Resume execution"""
        self.paused = False
    
    def stop(self):
        """Stop execution"""
        self.is_running = False
        self.paused = False
    
    def _execute_action(self, action):
        """Execute a single action with platform-specific handling"""
        action_lower = action.lower()
        
        # Application launching
        if "open excel" in action_lower:
            self._open_application("excel")
            
        elif "open web browser" in action_lower or "open browser" in action_lower:
            if "chrome" in action_lower:
                self._open_application("chrome")
            elif "firefox" in action_lower:
                self._open_application("firefox")
            else:
                # Default browser
                if self.system == "Windows":
                    self._open_application("chrome")
                elif self.system == "Darwin":
                    self._open_application("safari")
                else:
                    self._open_application("firefox")
        
        elif "open folder" in action_lower or "open file explorer" in action_lower:
            self._open_file_explorer()
        
        # Data entry
        elif "enter data" in action_lower or "type" in action_lower:
            # Extract text to type if specified
            if ":" in action:
                text = action.split(":", 1)[1].strip()
            else:
                text = "Sample Data"
            pyautogui.write(text, interval=0.1)
            
        elif "click" in action_lower:
            # Simple click at current position
            pyautogui.click()
        
        # Navigation
        elif "navigate" in action_lower:
            if "url" in action_lower or "http" in action:
                # Extract URL if present
                words = action.split()
                url = next((w for w in words if w.startswith("http")), "https://www.google.com")
                self._navigate_to_url(url)
            else:
                self._navigate_to_url("https://www.google.com")
        
        elif "search" in action_lower:
            if ":" in action:
                query = action.split(":", 1)[1].strip()
            else:
                query = "search query"
            self._perform_search(query)
        
        # File operations
        elif "save" in action_lower:
            self._save_file(action)
        
        elif "copy" in action_lower:
            pyautogui.hotkey('ctrl', 'c' if self.system == "Windows" else 'command', 'c')
        
        elif "paste" in action_lower:
            pyautogui.hotkey('ctrl', 'v' if self.system == "Windows" else 'command', 'v')
        
        # Keyboard shortcuts
        elif "tab" in action_lower:
            pyautogui.press('tab')
        
        elif "enter" in action_lower:
            pyautogui.press('enter')
        
        elif "escape" in action_lower or "esc" in action_lower:
            pyautogui.press('escape')
        
        else:
            # Generic action - just log it
            self.log(f"Generic action: {action}")
            time.sleep(0.5)
    
    def _open_application(self, app_name):
        """Open application based on OS"""
        try:
            if self.system == "Windows":
                pyautogui.press('win')
                time.sleep(0.5)
                pyautogui.write(app_name, interval=0.1)
                time.sleep(0.5)
                pyautogui.press('enter')
                time.sleep(2)  # Wait for app to open
                
            elif self.system == "Darwin":  # macOS
                pyautogui.hotkey('command', 'space')
                time.sleep(0.5)
                pyautogui.write(app_name, interval=0.1)
                time.sleep(0.5)
                pyautogui.press('enter')
                time.sleep(2)
                
            else:  # Linux
                # Try Alt+F2 for run dialog
                pyautogui.hotkey('alt', 'F2')
                time.sleep(0.5)
                pyautogui.write(app_name, interval=0.1)
                time.sleep(0.5)
                pyautogui.press('enter')
                time.sleep(2)
                
        except Exception as e:
            self.log(f"Failed to open {app_name}: {e}")
    
    def _open_file_explorer(self):
        """Open file explorer/finder"""
        try:
            if self.system == "Windows":
                pyautogui.hotkey('win', 'e')
            elif self.system == "Darwin":
                pyautogui.hotkey('command', 'space')
                time.sleep(0.3)
                pyautogui.write('finder', interval=0.1)
                pyautogui.press('enter')
            else:
                # Linux - try common file managers
                self._open_application("nautilus")  # GNOME
            time.sleep(1)
        except Exception as e:
            self.log(f"Failed to open file explorer: {e}")
    
    def _navigate_to_url(self, url):
        """Navigate to URL in browser"""
        try:
            if self.system == "Darwin":
                pyautogui.hotkey('command', 'l')
            else:
                pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.3)
            pyautogui.write(url, interval=0.05)
            pyautogui.press('enter')
            time.sleep(1)
        except Exception as e:
            self.log(f"Failed to navigate to {url}: {e}")
    
    def _perform_search(self, query):
        """Perform web search"""
        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            self._navigate_to_url(search_url)
        except Exception as e:
            self.log(f"Failed to search for {query}: {e}")
    
    def _save_file(self, action):
        """Save file with optional filename"""
        try:
            if self.system == "Darwin":
                pyautogui.hotkey('command', 's')
            else:
                pyautogui.hotkey('ctrl', 's')
            time.sleep(0.5)
            
            # Check if filename is specified
            if ":" in action:
                filename = action.split(":", 1)[1].strip()
                pyautogui.write(filename, interval=0.1)
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pyautogui.write(f"automated_file_{timestamp}", interval=0.1)
            
            pyautogui.press('enter')
        except Exception as e:
            self.log(f"Failed to save file: {e}")


class AutomationGUI:
    """Enhanced GUI for workflow automation with better UX"""
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("AGI Assistant - Workflow Automation")
        self.window.geometry("850x650")
        self.window.resizable(True, True)
        
        self.executor = WorkflowExecutor(log_callback=self.log)
        self.workflows = []
        self.execution_thread = None
        
        self.setup_ui()
        self.load_workflows()
        
        # Check if pyautogui is available
        if not PYAUTOGUI_AVAILABLE:
            messagebox.showwarning(
                "Missing Dependency",
                "PyAutoGUI is not installed. Automation features will be disabled.\n\n"
                "Install it with: pip install pyautogui"
            )
        
    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.window, bg="#2c3e50")
        title_frame.pack(fill=tk.X)
        
        title = tk.Label(
            title_frame,
            text="🤖 Workflow Automation",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title.pack(pady=15)
        
        subtitle = tk.Label(
            title_frame,
            text="Execute AI-Detected Workflows Automatically",
            font=("Arial", 10),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        subtitle.pack(pady=(0, 10))
        
        # Main content frame
        content_frame = ttk.Frame(self.window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Left panel - Workflow list
        left_panel = ttk.LabelFrame(content_frame, text="Detected Workflows", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Workflow listbox with scrollbar
        list_frame = ttk.Frame(left_panel)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.workflow_listbox = tk.Listbox(
            list_frame,
            height=12,
            font=("Arial", 10),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE
        )
        self.workflow_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.workflow_listbox.yview)
        
        self.workflow_listbox.bind('<<ListboxSelect>>', self.on_workflow_select)
        
        # Workflow details
        details_frame = ttk.LabelFrame(left_panel, text="Workflow Details", padding=5)
        details_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.details_text = tk.Text(
            details_frame,
            height=8,
            font=("Consolas", 9),
            wrap=tk.WORD,
            bg="#f8f9fa",
            state=tk.DISABLED
        )
        self.details_text.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Controls and logs
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Control buttons
        control_frame = ttk.LabelFrame(right_panel, text="Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        btn_grid = ttk.Frame(control_frame)
        btn_grid.pack()
        
        self.execute_btn = tk.Button(
            btn_grid,
            text="▶ Execute Selected",
            command=self.execute_selected,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=8,
            cursor="hand2",
            width=18
        )
        self.execute_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.pause_btn = tk.Button(
            btn_grid,
            text="⏸ Pause",
            command=self.pause_execution,
            bg="#f39c12",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=8,
            state=tk.DISABLED,
            cursor="hand2",
            width=18
        )
        self.pause_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.stop_btn = tk.Button(
            btn_grid,
            text="⏹ Stop",
            command=self.stop_execution,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=8,
            state=tk.DISABLED,
            cursor="hand2",
            width=18
        )
        self.stop_btn.grid(row=1, column=0, padx=5, pady=5)
        
        self.refresh_btn = tk.Button(
            btn_grid,
            text="🔄 Refresh List",
            command=self.load_workflows,
            bg="#3498db",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=8,
            cursor="hand2",
            width=18
        )
        self.refresh_btn.grid(row=1, column=1, padx=5, pady=5)
        
        # Status
        status_frame = ttk.LabelFrame(right_panel, text="Status", padding=5)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = tk.Label(
            status_frame,
            text="● Ready to automate",
            font=("Arial", 11, "bold"),
            fg="#27ae60"
        )
        self.status_label.pack()
        
        # Execution log
        log_frame = ttk.LabelFrame(right_panel, text="Execution Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_display = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            font=("Consolas", 9),
            bg="#f8f9fa",
            wrap=tk.WORD
        )
        self.log_display.pack(fill=tk.BOTH, expand=True)
        
        # Bottom info bar
        info_frame = tk.Frame(self.window, bg="#ecf0f1", height=40)
        info_frame.pack(fill=tk.X, side=tk.BOTTOM)
        info_frame.pack_propagate(False)
        
        warning = tk.Label(
            info_frame,
            text="⚠️ FAILSAFE: Move mouse to top-left corner to emergency stop | "
                 "💡 Position windows before executing",
            font=("Arial", 9),
            bg="#ecf0f1",
            fg="#e67e22"
        )
        warning.pack(pady=10)
        
    def load_workflows(self):
        """Load all detected workflows"""
        self.log("🔄 Loading workflows...")
        workflow_dir = Path("agi_data/workflows")
        
        if not workflow_dir.exists():
            self.log("⚠️ No workflows directory found")
            return
        
        workflow_files = sorted(workflow_dir.glob("*.json"), reverse=True)  # Most recent first
        
        self.workflows = []
        self.workflow_listbox.delete(0, tk.END)
        
        if not workflow_files:
            self.log("ℹ️ No workflows found. Run the Observer first to detect workflows.")
            self.workflow_listbox.insert(tk.END, "No workflows detected yet")
            return
        
        for wf_file in workflow_files:
            wf = self.executor.load_workflow(wf_file)
            if wf:
                self.workflows.append((wf_file, wf))
                
                # Format display text
                timestamp = wf.get('timestamp', '')[:19]
                desc = wf.get('description', 'Unknown')
                confidence = wf.get('confidence', 'unknown')
                
                display_text = f"[{confidence.upper()}] {desc} ({timestamp})"
                self.workflow_listbox.insert(tk.END, display_text)
        
        self.log(f"✅ Loaded {len(self.workflows)} workflow(s)")
    
    def on_workflow_select(self, event):
        """Handle workflow selection"""
        selection = self.workflow_listbox.curselection()
        if not selection or not self.workflows:
            return
        
        idx = selection[0]
        if idx >= len(self.workflows):
            return
        
        _, workflow = self.workflows[idx]
        
        # Display workflow details
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        details = f"Description: {workflow.get('description', 'N/A')}\n\n"
        details += f"Confidence: {workflow.get('confidence', 'unknown').upper()}\n"
        details += f"Categories: {', '.join(workflow.get('categories', []))}\n"
        details += f"Actions ({len(workflow.get('actions', []))}):\n"
        
        for i, action in enumerate(workflow.get('actions', []), 1):
            details += f"  {i}. {action}\n"
        
        self.details_text.insert(1.0, details)
        self.details_text.config(state=tk.DISABLED)
    
    def execute_selected(self):
        """Execute the selected workflow with confirmation"""
        selection = self.workflow_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a workflow to execute")
            return
        
        if not self.workflows:
            messagebox.showwarning("No Workflows", "No workflows available")
            return
        
        idx = selection[0]
        if idx >= len(self.workflows):
            return
        
        _, workflow = self.workflows[idx]
        
        # Confirm execution
        actions_preview = "\n".join(f"  • {a}" for a in workflow.get('actions', [])[:5])
        if len(workflow.get('actions', [])) > 5:
            actions_preview += f"\n  ... and {len(workflow.get('actions', [])) - 5} more"
        
        response = messagebox.askyesno(
            "Confirm Execution",
            f"Execute workflow?\n\n"
            f"{workflow.get('description')}\n\n"
            f"Actions:\n{actions_preview}\n\n"
            f"⚠️ Make sure target applications and windows are ready!"
        )
        
        if not response:
            return
        
        # Prepare UI
        self.execute_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        self.log_display.delete(1.0, tk.END)
        
        # Countdown
        for i in range(3, 0, -1):
            self.status_label.config(text=f"⏱ Starting in {i}...", fg="#f39c12")
            self.log(f"Starting in {i}...")
            self.window.update()
            time.sleep(1)
        
        self.status_label.config(text="● Executing...", fg="#e67e22")
        
        # Execute in thread
        import threading
        self.execution_thread = threading.Thread(
            target=self._execute_workflow_thread,
            args=(workflow,),
            daemon=True
        )
        self.execution_thread.start()
    
    def _execute_workflow_thread(self, workflow):
        """Execute workflow in separate thread"""
        try:
            self.executor.execute_workflow(workflow, self.update_status)
        finally:
            self.window.after(0, self._execution_complete)
    
    def _execution_complete(self):
        """Handle execution completion"""
        self.execute_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="● Ready", fg="#27ae60")
    
    def pause_execution(self):
        """Pause/resume execution"""
        if self.executor.paused:
            self.executor.resume()
            self.pause_btn.config(text="⏸ Pause")
            self.status_label.config(text="● Executing...", fg="#e67e22")
            self.log("▶ Resumed")
        else:
            self.executor.pause()
            self.pause_btn.config(text="▶ Resume")
            self.status_label.config(text="● Paused", fg="#f39c12")
            self.log("⏸ Paused")
    
    def stop_execution(self):
        """Stop workflow execution"""
        self.executor.stop()
        self.log("⏹ Stopping...")
        self._execution_complete()
    
    def update_status(self, message):
        """Update status and log (called from executor)"""
        self.log(message)
    
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_display.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_display.see(tk.END)
        self.window.update_idletasks()
    
    def run(self):
        """Run the application"""
        self.window.mainloop()


if __name__ == "__main__":
    print("=" * 80)
    print("🤖 AGI Assistant - Workflow Automation")
    print("=" * 80)
    app = AutomationGUI()
    app.run()
