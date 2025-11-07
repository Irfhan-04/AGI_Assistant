"""Settings window for configuration and information."""

import customtkinter as ctk
from src.config import UI_CONFIG
from src.storage.storage_manager import StorageManager
from src.storage.database import Database
from src.logger import get_logger

logger = get_logger(__name__)


class SettingsWindow(ctk.CTk):
    """Settings and information window."""
    
    def __init__(self, parent=None, database: Database = None):
        """Initialize settings window.
        
        Args:
            parent: Parent window
            database: Database instance
        """
        super().__init__()
        
        self.parent = parent
        self.database = database or Database()
        self.storage_manager = StorageManager(self.database)
        
        self.title("⚙️ Settings - The AGI Assistant")
        self.geometry("600x500")
        self.configure(fg_color=UI_CONFIG["colors"]["background"])
        
        self._create_tabs()
        
        logger.info("Settings window initialized")
    
    def _create_tabs(self):
        """Create tabbed interface."""
        # Create tabview
        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Storage tab
        storage_tab = tabview.add("💾 Storage")
        self._create_storage_tab(storage_tab)
        
        # Privacy tab
        privacy_tab = tabview.add("🔒 Privacy")
        self._create_privacy_tab(privacy_tab)
        
        # About tab
        about_tab = tabview.add("ℹ️ About")
        self._create_about_tab(about_tab)
    
    def _create_storage_tab(self, parent):
        """Create storage management tab."""
        # Storage usage
        usage_frame = ctk.CTkFrame(parent)
        usage_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            usage_frame,
            text="Storage Usage",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=10)
        
        usage = self.storage_manager.get_storage_usage()
        
        usage_text = (
            f"Total: {usage['total_size_gb']:.2f} GB / {usage['max_size_gb']:.2f} GB\n"
            f"Usage: {usage['usage_percentage']:.1f}%\n"
            f"Sessions: {usage['session_count']}"
        )
        
        ctk.CTkLabel(
            usage_frame,
            text=usage_text,
            font=("Segoe UI", 12)
        ).pack(pady=10)
        
        # Cleanup button
        cleanup_btn = ctk.CTkButton(
            parent,
            text="🧹 Cleanup Old Sessions",
            command=self._cleanup_sessions,
            fg_color=UI_CONFIG["colors"]["warning"]
        )
        cleanup_btn.pack(pady=10)
    
    def _create_privacy_tab(self, parent):
        """Create privacy information tab."""
        privacy_text = """
🔒 PRIVACY GUARANTEE

The AGI Assistant runs 100% locally on your machine.

✓ No cloud uploads
✓ No data sharing
✓ No external network requests
✓ All processing happens on your computer
✓ Your workflows stay yours

All data is stored locally in:
- Session recordings: data/sessions/
- Workflows: data/workflows.db
- Logs: logs/

You can delete all data at any time by deleting the 'data' folder.
        """
        
        text_label = ctk.CTkLabel(
            parent,
            text=privacy_text,
            font=("Segoe UI", 12),
            justify="left",
            anchor="w"
        )
        text_label.pack(padx=20, pady=20, fill="both", expand=True)
    
    def _create_about_tab(self, parent):
        """Create about tab."""
        about_text = """
🤖 The AGI Assistant v1.0.0

A local AI desktop assistant that observes, learns, and automates.

Built for the Humanity Founders Hackathon.

Features:
• Screen and audio recording
• Automatic workflow learning
• Pattern detection across sessions
• Desktop and browser automation
• 100% local processing

Technologies:
• Python 3.10+
• Ollama + Phi-3.5 Mini
• CustomTkinter
• PyAutoGUI + Playwright
• Faster-Whisper
• Tesseract OCR

© 2025 The AGI Assistant
        """
        
        text_label = ctk.CTkLabel(
            parent,
            text=about_text,
            font=("Segoe UI", 11),
            justify="left",
            anchor="w"
        )
        text_label.pack(padx=20, pady=20, fill="both", expand=True)
    
    def _cleanup_sessions(self):
        """Clean up old sessions."""
        cleaned = self.storage_manager.cleanup_old_sessions()
        
        # Show message
        msg = ctk.CTkLabel(
            self,
            text=f"Cleaned up {cleaned} old sessions",
            font=("Segoe UI", 12),
            fg_color=UI_CONFIG["colors"]["success"]
        )
        msg.pack(pady=10)
        self.after(3000, msg.destroy)

