"""Workflow card component for displaying workflows."""

import customtkinter as ctk
from typing import Dict, Any, Callable
from src.config import UI_CONFIG
from src.logger import get_logger

logger = get_logger(__name__)


class WorkflowCard(ctk.CTkFrame):
    """Card component for displaying a workflow."""
    
    def __init__(self, parent, workflow: Dict[str, Any], 
                 on_run: Callable, on_delete: Callable):
        """Initialize workflow card.
        
        Args:
            parent: Parent widget
            workflow: Workflow dictionary
            on_run: Callback for run button
            on_delete: Callback for delete button
        """
        super().__init__(parent)
        
        self.workflow = workflow
        self.on_run = on_run
        self.on_delete = on_delete
        
        self.configure(
            fg_color=UI_CONFIG["colors"]["surface"],
            corner_radius=10,
            border_width=2,
            border_color=UI_CONFIG["colors"]["primary"]
        )
        
        self._create_card()
    
    def _create_card(self):
        """Create card content."""
        # Header frame
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=10)
        
        # Status icon
        confidence = self.workflow.get("confidence", 0.0)
        icon = "✅" if confidence > 0.8 else "⏳" if confidence > 0.5 else "⚠️"
        icon_label = ctk.CTkLabel(
            header_frame,
            text=icon,
            font=("Segoe UI", 24)
        )
        icon_label.pack(side="left", padx=10)
        
        # Workflow name and description
        info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=self.workflow.get("workflow_name", "Unnamed Workflow"),
            font=("Segoe UI", 16, "bold")
        )
        name_label.pack(anchor="w")
        
        description = self.workflow.get("description", "")
        if description:
            desc_label = ctk.CTkLabel(
                info_frame,
                text=description[:100] + "..." if len(description) > 100 else description,
                font=("Segoe UI", 11),
                text_color="#95a5a6"
            )
            desc_label.pack(anchor="w")
        
        # Stats frame
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=15, pady=5)
        
        # Calculate success rate
        times_run = self.workflow.get("times_run", 0)
        times_succeeded = self.workflow.get("times_succeeded", 0)
        success_rate = (times_succeeded / times_run * 100) if times_run > 0 else 0
        
        stats_text = (
            f"Confidence: {confidence*100:.0f}% | "
            f"Runs: {times_run} | "
            f"Success: {success_rate:.0f}% | "
            f"Category: {self.workflow.get('category', 'general')}"
        )
        stats_label = ctk.CTkLabel(
            stats_frame,
            text=stats_text,
            font=("Segoe UI", 10),
            text_color="#95a5a6"
        )
        stats_label.pack(side="left")
        
        # Action buttons frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=10)
        
        run_btn = ctk.CTkButton(
            btn_frame,
            text="▶️ Run Now",
            command=lambda: self.on_run(self.workflow),
            fg_color=UI_CONFIG["colors"]["success"],
            hover_color="#229954",
            width=120,
            height=35
        )
        run_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Delete",
            command=lambda: self.on_delete(self.workflow),
            fg_color=UI_CONFIG["colors"]["danger"],
            hover_color="#c0392b",
            width=100,
            height=35
        )
        delete_btn.pack(side="left", padx=5)
        
        # Steps preview
        steps = self.workflow.get("steps", [])
        if steps:
            steps_text = f"{len(steps)} steps"
            if steps:
                first_step = steps[0]
                steps_text += f": {first_step.get('action_type', '')} - {first_step.get('target', '')[:30]}"
            
            steps_label = ctk.CTkLabel(
                btn_frame,
                text=steps_text,
                font=("Segoe UI", 9),
                text_color="#7f8c8d"
            )
            steps_label.pack(side="right", padx=10)

