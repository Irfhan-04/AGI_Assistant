"""Main window UI using CustomTkinter."""

import threading
import time
import sys
import customtkinter as ctk
from pathlib import Path
from typing import Optional
from src.observation.session_manager import SessionManager
from src.storage.database import Database
from src.automation.executor import WorkflowExecutor
from src.config import UI_CONFIG
from src.logger import get_logger

logger = get_logger(__name__)

# Set appearance mode and color theme
ctk.set_appearance_mode(UI_CONFIG["theme"])
ctk.set_default_color_theme("blue")


class MainWindow(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        
        self.title("🤖 The AGI Assistant")
        self.geometry(UI_CONFIG["window_size"])
        self.configure(fg_color=UI_CONFIG["colors"]["background"])
        
        # Initialize components
        try:
            self.session_manager = SessionManager()
            self.database = Database()
            self.executor = WorkflowExecutor()
            
            self.is_recording = False
            self.recording_start_time: Optional[float] = None
            
            # Create UI
            self._create_header()
            self._create_control_panel()
            self._create_workflows_section()
            self._create_status_bar()
            
            # Start update loop
            self._update_loop()
            
            logger.info("Main window initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing main window: {e}", exc_info=True)
            self._show_error_dialog(f"Initialization Error: {str(e)}")
    
    def _show_error_dialog(self, message: str):
        """Show error dialog."""
        error_window = ctk.CTkToplevel(self)
        error_window.title("Error")
        error_window.geometry("400x200")
        
        label = ctk.CTkLabel(
            error_window,
            text=message,
            wraplength=350,
            font=("Segoe UI", 12)
        )
        label.pack(pady=20, padx=20)
        
        close_btn = ctk.CTkButton(
            error_window,
            text="Close",
            command=error_window.destroy
        )
        close_btn.pack(pady=10)
    
    def _create_header(self):
        """Create header section."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=20, padx=20, fill="x")
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🤖 The AGI Assistant",
            font=("Segoe UI", 28, "bold"),
            text_color=UI_CONFIG["colors"]["primary"]
        )
        title_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Watch, Learn, Automate - 100% Local",
            font=("Segoe UI", 12),
            text_color="#95a5a6"
        )
        subtitle_label.pack()
    
    def _create_control_panel(self):
        """Create control panel with recording buttons."""
        control_frame = ctk.CTkFrame(self, fg_color=UI_CONFIG["colors"]["surface"])
        control_frame.pack(pady=10, padx=20, fill="x")
        
        buttons_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        buttons_frame.pack(pady=10)
        
        self.record_btn = ctk.CTkButton(
            buttons_frame,
            text="🔴 Start Watching",
            command=self._start_recording,
            fg_color=UI_CONFIG["colors"]["danger"],
            hover_color="#c0392b",
            height=50,
            width=200,
            font=("Segoe UI", 16, "bold")
        )
        self.record_btn.pack(side="left", padx=10)
        
        self.stop_btn = ctk.CTkButton(
            buttons_frame,
            text="⏹️ Stop Watching",
            command=self._stop_recording,
            state="disabled",
            height=50,
            width=200,
            font=("Segoe UI", 16, "bold")
        )
        self.stop_btn.pack(side="left", padx=10)
        
        self.status_label = ctk.CTkLabel(
            control_frame,
            text="Status: Ready to observe",
            font=("Segoe UI", 14)
        )
        self.status_label.pack(pady=10)
        
        stats_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        stats_frame.pack(pady=10)
        
        self.duration_label = ctk.CTkLabel(
            stats_frame,
            text="Duration: 00:00:00",
            font=("Segoe UI", 12)
        )
        self.duration_label.pack(side="left", padx=20)
        
        self.screenshots_label = ctk.CTkLabel(
            stats_frame,
            text="Screenshots: 0",
            font=("Segoe UI", 12)
        )
        self.screenshots_label.pack(side="left", padx=20)
        
        self.audio_label = ctk.CTkLabel(
            stats_frame,
            text="Audio clips: 0",
            font=("Segoe UI", 12)
        )
        self.audio_label.pack(side="left", padx=20)
        
        self.events_label = ctk.CTkLabel(
            stats_frame,
            text="Events: 0",
            font=("Segoe UI", 12)
        )
        self.events_label.pack(side="left", padx=20)
    
    def _create_workflows_section(self):
        """Create workflows display section."""
        workflows_frame = ctk.CTkFrame(self, fg_color=UI_CONFIG["colors"]["surface"])
        workflows_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        label = ctk.CTkLabel(
            workflows_frame,
            text="📚 Learned Workflows",
            font=("Segoe UI", 18, "bold")
        )
        label.pack(pady=10)
        
        self.workflows_scroll = ctk.CTkScrollableFrame(
            workflows_frame,
            fg_color="transparent"
        )
        self.workflows_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._load_workflows()
    
    def _create_status_bar(self):
        """Create status bar."""
        status_frame = ctk.CTkFrame(self, fg_color=UI_CONFIG["colors"]["surface"], height=30)
        status_frame.pack(side="bottom", fill="x", padx=20, pady=5)
        status_frame.pack_propagate(False)
        
        self.status_text = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=("Segoe UI", 10),
            text_color="#95a5a6"
        )
        self.status_text.pack(side="left", padx=10)
    
    def _start_recording(self):
        """Start recording session."""
        if self.is_recording:
            return
        
        try:
            self.is_recording = True
            self.recording_start_time = time.time()
            
            session_id = self.session_manager.start_session()
            
            self.record_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.status_label.configure(text=f"Status: Recording session {session_id}")
            self.status_text.configure(text=f"Recording: {session_id}")
            
            logger.info(f"Started recording session: {session_id}")
        except Exception as e:
            logger.error(f"Error starting recording: {e}", exc_info=True)
            self._show_error_dialog(f"Failed to start recording: {str(e)}")
            self.is_recording = False
    
    def _stop_recording(self):
        """Stop recording session."""
        if not self.is_recording:
            return
        
        try:
            self.is_recording = False
            
            session_summary = self.session_manager.stop_session()
            
            self.record_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.status_label.configure(text="Status: Processing session...")
            self.status_text.configure(text="Processing session data...")
            
            threading.Thread(target=self._process_session, args=(session_summary,), daemon=True).start()
            
            logger.info("Stopped recording session")
        except Exception as e:
            logger.error(f"Error stopping recording: {e}", exc_info=True)
            self._show_error_dialog(f"Failed to stop recording: {str(e)}")
    
    def _process_session(self, session_summary: dict):
        """Process session data in background."""
        try:
            session_dir = Path(session_summary.get("session_dir", ""))
            if not session_dir.exists():
                logger.error(f"Session directory not found: {session_dir}")
                return
            
            from src.processing.audio_transcriber import AudioTranscriber
            from src.processing.ocr_engine import OCREngine
            from src.processing.data_fusion import DataFusion
            from src.intelligence.learning_engine import LearningEngine
            
            transcriber = AudioTranscriber()
            transcriber.transcribe_session(session_dir)
            
            ocr = OCREngine()
            ocr.process_session(session_dir)
            
            fusion = DataFusion()
            timeline = fusion.create_timeline(session_dir)
            timeline["session_id"] = session_dir.name
            
            learning_engine = LearningEngine(self.database)
            workflow = learning_engine.learn_from_session(session_dir)
            
            session_summary["learned_workflow_id"] = workflow.get("id") if workflow else None
            self.database.add_session(session_summary)
            
            self.after(0, self._on_session_processed, workflow is not None)
            
        except Exception as e:
            logger.error(f"Error processing session: {e}", exc_info=True)
            self.after(0, lambda: self.status_text.configure(text=f"Error: {str(e)[:50]}"))
    
    def _on_session_processed(self, workflow_learned: bool):
        """Called when session processing is complete."""
        if workflow_learned:
            self.status_label.configure(text="Status: Workflow learned! Check workflows below.")
            self.status_text.configure(text="Workflow learned successfully")
        else:
            self.status_label.configure(text="Status: Session processed. Need more similar sessions.")
            self.status_text.configure(text="Session processed")
        
        self._load_workflows()
    
    def _load_workflows(self):
        """Load and display workflows."""
        for widget in self.workflows_scroll.winfo_children():
            widget.destroy()
        
        try:
            workflows = self.database.get_all_workflows()
            
            if not workflows:
                no_workflows_label = ctk.CTkLabel(
                    self.workflows_scroll,
                    text="No workflows learned yet. Start recording to learn workflows!",
                    font=("Segoe UI", 12),
                    text_color="#95a5a6"
                )
                no_workflows_label.pack(pady=20)
                return
            
            from src.ui.workflow_card import WorkflowCard
            
            for workflow in workflows:
                card = WorkflowCard(
                    self.workflows_scroll,
                    workflow=workflow,
                    on_run=self._run_workflow,
                    on_delete=self._delete_workflow
                )
                card.pack(pady=5, padx=10, fill="x")
        except Exception as e:
            logger.error(f"Error loading workflows: {e}", exc_info=True)
    
    def _run_workflow(self, workflow: dict):
        """Run a workflow."""
        self.status_text.configure(text=f"Executing: {workflow.get('workflow_name')}")
        threading.Thread(target=self._execute_workflow, args=(workflow,), daemon=True).start()
    
    def _execute_workflow(self, workflow: dict):
        """Execute workflow in background."""
        try:
            result = self.executor.execute(workflow)
            
            self.database.log_execution({
                "workflow_id": workflow.get("id"),
                "started_at": result.get("started_at"),
                "completed_at": result.get("completed_at"),
                "success": result.get("success"),
                "steps_completed": result.get("steps_completed"),
                "steps_total": result.get("steps_total"),
                "error_message": result.get("error_message"),
                "execution_time": result.get("execution_time")
            })
            
            if result.get("success"):
                self.after(0, lambda: self.status_text.configure(
                    text=f"✓ '{workflow.get('workflow_name')}' completed"
                ))
            else:
                self.after(0, lambda: self.status_text.configure(
                    text=f"✗ '{workflow.get('workflow_name')}' failed"
                ))
            
        except Exception as e:
            logger.error(f"Error executing workflow: {e}", exc_info=True)
            self.after(0, lambda: self.status_text.configure(text=f"Error: {str(e)[:50]}"))
    
    def _delete_workflow(self, workflow: dict):
        """Delete a workflow."""
        workflow_id = workflow.get("id")
        if workflow_id:
            self.database.delete_workflow(workflow_id)
            self._load_workflows()
            self.status_text.configure(text=f"Deleted: {workflow.get('workflow_name')}")
    
    def _update_loop(self):
        """Update loop for UI refresh."""
        try:
            if self.is_recording:
                stats = self.session_manager.get_session_stats()
                
                elapsed = stats.get("elapsed_seconds", 0)
                hours = elapsed // 3600
                minutes = (elapsed % 3600) // 60
                seconds = elapsed % 60
                self.duration_label.configure(text=f"Duration: {hours:02d}:{minutes:02d}:{seconds:02d}")
                
                self.screenshots_label.configure(text=f"Screenshots: {stats.get('screenshots', 0)}")
                self.audio_label.configure(text=f"Audio clips: {stats.get('audio_clips', 0)}")
                self.events_label.configure(text=f"Events: {stats.get('events', 0)}")
        except Exception as e:
            logger.error(f"Error in update loop: {e}")
        finally:
            self.after(1000, self._update_loop)
    
    def on_closing(self):
        """Handle window closing."""
        try:
            if self.is_recording:
                self._stop_recording()
            self.database.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        finally:
            self.destroy()