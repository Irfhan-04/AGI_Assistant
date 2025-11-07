"""Build script for creating .exe executable."""

import os
import sys
import subprocess
from pathlib import Path

def build_exe():
    """Build executable using PyInstaller."""
    print("🔨 Building The AGI Assistant executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=AGI_Assistant",
        "--icon=NONE",  # Add icon file path if you have one
        "--add-data=src;src",  # Include src directory
        "--hidden-import=customtkinter",
        "--hidden-import=pil",
        "--hidden-import=mss",
        "--hidden-import=sounddevice",
        "--hidden-import=faster_whisper",
        "--hidden-import=pytesseract",
        "--hidden-import=ollama",
        "--hidden-import=playwright",
        "--hidden-import=pyautogui",
        "--hidden-import=pygetwindow",
        "--collect-all=customtkinter",
        "--collect-all=PIL",
        "main.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build successful!")
        print(f"📦 Executable location: dist/AGI_Assistant.exe")
        print("\n⚠️  Note: Make sure to:")
        print("   1. Install Tesseract OCR on target machine")
        print("   2. Install Ollama and pull phi3.5:mini model")
        print("   3. Install Playwright browsers: playwright install chromium")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found. Install it with: pip install pyinstaller")
        return False

if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)

