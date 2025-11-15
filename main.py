"""Main window UI using CustomTkinter."""

import threading
import time
import customtkinter as ctk
from pathlib import Path
from typing import Optional
from src.observation.session_manager import SessionManager
from src.storage.database import Database
from src.storage.storage_manager import StorageManager
from src.automation.executor import WorkflowExecutor
from src.ui.workflow_card import WorkflowCard
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
        self.session_manager = SessionManager()
        self.database = Database()
        self.storage_manager = StorageManager(self.database)
        self.executor = WorkflowExecutor()
        
        self.is_recording = False
        self.recording_start_time: Optional[float] = None
        
        # Create UI
        self._create_header()
        self._create_control_panel()
        self._create_workflows_section()
        self._create_status_bar()
        
        # Check Ollama connection on startup
        self._check_dependencies()
        
        # Start update loop
        self._update_loop()
        
        logger.info("Main window initialized")
    
    def _check_dependencies(self):
        """Check if required dependencies are available."""
        errors = []
        
        # Check Ollama
        try:
            from src.intelligence.llm_interface import LLMInterface
            llm = LLMInterface()
            if not llm.test_connection():
                errors.append("⚠️ Ollama not connected. Make sure Ollama is running and phi3.5:mini model is pulled.")
        except Exception as e:
            errors.append(f"⚠️ Ollama error: {str(e)}")
        
        # Check Tesseract
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
        except Exception as e:
            errors.append("⚠️ Tesseract OCR not found. Please install Tesseract OCR.")
        
        # Show warnings if any
        if errors:
            self.after(1000, lambda: self._show_dependency_warning("\n".join(errors)))
    
    def _show_dependency_warning(self, message: str):
        """Show dependency warning dialog."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("⚠️ Dependency Warning")
        dialog.geometry("500x300")
        
        text = ctk.CTkTextbox(dialog, wrap="word")
        text.pack(fill="both", expand=True, padx=20, pady=20)
        text.insert("1.0", message + "\n\nThe application will continue, but some features may not work.")
        text.configure(state="disabled")
        
        ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy
        ).pack(pady=10)
    
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
        
        # Buttons frame
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
        
        # Settings button
        settings_btn = ctk.CTkButton(
            buttons_frame,
            text="⚙️ Settings",
            command=self._open_settings,
            height=50,
            width=120,
            font=("Segoe UI", 14)
        )
        settings_btn.pack(side="left", padx=10)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            control_frame,
            text="Status: Ready to observe",
            font=("Segoe UI", 14)
        )
        self.status_label.pack(pady=10)
        
        # Stats frame
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
        
        # Header with label and refresh button
        header_frame = ctk.CTkFrame(workflows_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=10, padx=10)
        
        label = ctk.CTkLabel(
            header_frame,
            text="📚 Learned Workflows",
            font=("Segoe UI", 18, "bold")
        )
        label.pack(side="left", padx=10)
        
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            command=self._load_workflows,
            width=100,
            height=30
        )
        refresh_btn.pack(side="right", padx=10)
        
        # Scrollable frame for workflow cards
        self.workflows_scroll = ctk.CTkScrollableFrame(
            workflows_frame,
            fg_color="transparent"
        )
        self.workflows_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Load workflows
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
            
            # Start session
            session_id = self.session_manager.start_session()
            
            # Update UI
            self.record_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.status_label.configure(text=f"Status: Recording session {session_id}")
            self.status_text.configure(text=f"Recording: {session_id}")
            
            logger.info(f"Started recording session: {session_id}")
        except Exception as e:
            logger.error(f"Error starting recording: {e}", exc_info=True)
            self.is_recording = False
            self.status_text.configure(text=f"Error: {str(e)}")
    
    def _stop_recording(self):
        """Stop recording session."""
        if not self.is_recording:
            return
        
        try:
            self.is_recording = False
            
            # Stop session
            session_summary = self.session_manager.stop_session()
            
            # Update UI
            self.record_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.status_label.configure(text="Status: Processing session...")
            self.status_text.configure(text="Processing session data...")
            
            # Process session in background
            threading.Thread(target=self._process_session, args=(session_summary,), daemon=True).start()
            
            logger.info("Stopped recording session")
        except Exception as e:
            logger.error(f"Error stopping recording: {e}", exc_info=True)
            self.status_text.configure(text=f"Error: {str(e)}")
    
    def _process_session(self, session_summary: dict):
        """Process session data in background."""
        try:
            session_dir = Path(session_summary.get("session_dir", ""))
            if not session_dir.exists():
                logger.error(f"Session directory not found: {session_dir}")
                self.after(0, lambda: self.status_text.configure(text="Error: Session directory not found"))
                return
            
            # Process audio transcription
            try:
                from src.processing.audio_transcriber import AudioTranscriber
                transcriber = AudioTranscriber()
                transcriber.transcribe_session(session_dir)
            except Exception as e:
                logger.warning(f"Audio transcription failed: {e}")
            
            # Process OCR
            try:
                from src.processing.ocr_engine import OCREngine
                ocr = OCREngine()
                ocr.process_session(session_dir)
            except Exception as e:
                logger.warning(f"OCR processing failed: {e}")
            
            # Create timeline
            try:
                from src.processing.data_fusion import DataFusion
                fusion = DataFusion()
                timeline = fusion.create_timeline(session_dir)
                timeline["session_id"] = session_dir.name
            except Exception as e:
                logger.error(f"Timeline creation failed: {e}")
                self.after(0, lambda: self.status_text.configure(text="Error creating timeline"))
                return
            
            # Try to learn workflow
            workflow = None
            try:
                from src.intelligence.learning_engine import LearningEngine
                learning_engine = LearningEngine(self.database)
                workflow = learning_engine.learn_from_session(session_dir)
            except Exception as e:
                logger.warning(f"Workflow learning failed: {e}")
            
            # Save session to database
            try:
                session_summary["learned_workflow_id"] = workflow.get("id") if workflow else None
                self.database.add_session(session_summary)
            except Exception as e:
                logger.error(f"Failed to save session to database: {e}")
            
            # Update UI
            self.after(0, self._on_session_processed, workflow is not None)
            
        except Exception as e:
            logger.error(f"Error processing session: {e}", exc_info=True)
            self.after(0, lambda: self.status_text.configure(text="Error processing session"))
    
    def _on_session_processed(self, workflow_learned: bool):
        """Called when session processing is complete."""
        if workflow_learned:
            self.status_label.configure(text="Status: Workflow learned! Check workflows below.")
            self.status_text.configure(text="Workflow learned successfully")
        else:
            self.status_label.configure(text="Status: Session processed. Need more similar sessions to learn workflow.")
            self.status_text.configure(text="Session processed")
        
        # Reload workflows
        self._load_workflows()
    
    def _load_workflows(self):
        """Load and display workflows."""
        try:
            # Clear existing cards
            for widget in self.workflows_scroll.winfo_children():
                widget.destroy()
            
            # Get workflows from database
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
            
            # Create workflow cards
            for workflow in workflows:
                try:
                    card = WorkflowCard(
                        self.workflows_scroll,
                        workflow=workflow,
                        on_run=self._run_workflow,
                        on_delete=self._delete_workflow
                    )
                    card.pack(pady=5, padx=10, fill="x")
                except Exception as e:
                    logger.error(f"Error creating workflow card: {e}")
                    
        except Exception as e:
            logger.error(f"Error loading workflows: {e}", exc_info=True)
    
    def _run_workflow(self, workflow: dict):
        """Run a workflow."""
        try:
            self.status_text.configure(text=f"Executing workflow: {workflow.get('workflow_name')}")
            
            # Execute in background thread
            threading.Thread(target=self._execute_workflow, args=(workflow,), daemon=True).start()
        except Exception as e:
            logger.error(f"Error running workflow: {e}", exc_info=True)
            self.status_text.configure(text=f"Error: {str(e)}")
    
    def _execute_workflow(self, workflow: dict):
        """Execute workflow in background."""
        try:
            result = self.executor.execute(workflow)
            
            # Log execution
            try:
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
            except Exception as e:
                logger.error(f"Failed to log execution: {e}")
            
            # Update UI
            if result.get("success"):
                self.after(0, lambda: self.status_text.configure(
                    text=f"✅ Workflow '{workflow.get('workflow_name')}' completed successfully"
                ))
            else:
                error_msg = result.get("error_message", "Unknown error")
                self.after(0, lambda: self.status_text.configure(
                    text=f"❌ Workflow failed: {error_msg}"
                ))
            
        except Exception as e:
            logger.error(f"Error executing workflow: {e}", exc_info=True)
            self.after(0, lambda: self.status_text.configure(text=f"Error: {str(e)}"))
    
    def _delete_workflow(self, workflow: dict):
        """Delete a workflow."""
        try:
            workflow_id = workflow.get("id")
            if workflow_id:
                self.database.delete_workflow(workflow_id)
                self._load_workflows()
                self.status_text.configure(text=f"Deleted workflow: {workflow.get('workflow_name')}")
        except Exception as e:
            logger.error(f"Error deleting workflow: {e}", exc_info=True)
            self.status_text.configure(text=f"Error: {str(e)}")
    
    def _open_settings(self):
        """Open settings window."""
        try:
            from src.ui.settings_window import SettingsWindow
            settings = SettingsWindow(parent=self, database=self.database)
            settings.focus()
        except Exception as e:
            logger.error(f"Error opening settings: {e}", exc_info=True)
    
    def _update_loop(self):
        """Update loop for UI refresh."""
        try:
            if self.is_recording:
                stats = self.session_manager.get_session_stats()
                
                # Update duration
                elapsed = stats.get("elapsed_seconds", 0)
                hours = elapsed // 3600
                minutes = (elapsed % 3600) // 60
                seconds = elapsed % 60
                self.duration_label.configure(text=f"Duration: {hours:02d}:{minutes:02d}:{seconds:02d}")
                
                # Update stats
                self.screenshots_label.configure(text=f"Screenshots: {stats.get('screenshots', 0)}")
                self.audio_label.configure(text=f"Audio clips: {stats.get('audio_clips', 0)}")
                self.events_label.configure(text=f"Events: {stats.get('events', 0)}")
        except Exception as e:
            logger.debug(f"Error in update loop: {e}")
        
        # Schedule next update
        self.after(1000, self._update_loop)
    
    def on_closing(self):
        """Handle window closing."""
        try:
            if self.is_recording:
                self._stop_recording()
                time.sleep(1)  # Give time to stop gracefully
            self.database.close()
        except Exception as e:
            logger.error(f"Error during closing: {e}")
        finally:
            self.destroy()