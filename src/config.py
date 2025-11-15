"""Configuration settings for The AGI Assistant."""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
SESSIONS_DIR = DATA_DIR / "sessions"
WORKFLOWS_DIR = DATA_DIR / "workflows"
DB_PATH = DATA_DIR / "workflows.db"

# Storage configuration
STORAGE_CONFIG = {
    "max_total_size": 2 * 1024 * 1024 * 1024,  # 2GB
    "sessions": {
        "retention_days": 7,
        "delete_after_learning": True,
        "compress_screenshots": True,
        "jpeg_quality": 75,
    },
    "workflows": {
        "retention": "permanent",
        "backup_frequency": "daily",
        "max_count": 100,
    },
    "cleanup_triggers": {
        "storage_threshold": 0.9,  # 90% full
        "check_frequency": "hourly",
    }
}

# Observation settings
OBSERVATION_CONFIG = {
    "screenshot": {
        "interval_ms": 2000,  # 2 seconds between screenshots
        "format": "JPEG",
        "quality": 75,
        "only_on_activity": True,  # Skip idle periods
    },
    "audio": {
        "sample_rate": 16000,
        "channels": 1,
        "chunk_duration": 10,  # 10 second clips
        "silence_threshold": 0.01,  # Skip silent periods
    },
    "events": {
        "capture_mouse": True,
        "capture_keyboard": True,
        "capture_window_changes": True,
    }
}

# Processing settings
PROCESSING_CONFIG = {
    "whisper": {
        "model_size": "base",  # base, small, medium, large
        "device": "cpu",
        "compute_type": "int8",
    },
    "ocr": {
        "language": "eng",
        "config": "--psm 6",  # Assume uniform block of text
    }
}

# Intelligence settings
INTELLIGENCE_CONFIG = {
    "ollama": {
        "base_url": "http://localhost:11434",
        "model": "phi3.5:latest",  # Changed from phi3.5:mini
        "timeout": 60,
        "max_retries": 3,
    },
    "pattern_detection": {
        "min_similarity": 0.80,
        "min_occurrences": 3,
    },
    "workflow_generation": {
        "max_timeline_length": 1000,
        "confidence_threshold": 0.7,
    }
}

# Automation settings
AUTOMATION_CONFIG = {
    "safety": {
        "fail_safe": True,  # Move mouse to corner to abort
        "pause_between_actions": 0.5,  # seconds
        "action_timeout": 10,  # seconds per action
    },
    "verification": {
        "screenshot_comparison": True,
        "similarity_threshold": 0.95,  # 95% similarity for success
    }
}

# UI settings
UI_CONFIG = {
    "theme": "dark",
    "window_size": "900x700",
    "colors": {
        "primary": "#3498db",
        "success": "#27ae60",
        "danger": "#e74c3c",
        "warning": "#f39c12",
        "background": "#1a1a1a",
        "surface": "#2d2d2d",
    }
}

# Create directories if they don't exist
os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(WORKFLOWS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

