# Create build_exe.bat
cat > build_exe.bat << 'EOF'
@echo off
REM Build script for The AGI Assistant executable
REM Run this after installing all dependencies

echo ========================================
echo Building The AGI Assistant Executable
echo ========================================
echo.

REM Check if virtual environment is activated
python --version
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

echo.
echo Step 1: Installing/Updating PyInstaller...
pip install pyinstaller --upgrade

echo.
echo Step 2: Building executable...
python build_exe.py

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Your executable is in: dist\AGI_Assistant.exe
echo.
echo IMPORTANT: Before distributing, ensure:
echo   1. Tesseract OCR is installed on target machine
echo   2. Ollama is installed and phi3.5:latest model is pulled
echo   3. Playwright browsers are installed
echo.
pause
EOF

# Also update build_exe.py to work on both Windows and Linux
cat > build_exe.py << 'EOF'
"""Build script for creating .exe executable."""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_exe():
    """Build executable using PyInstaller."""
    print("🔨 Building The AGI Assistant executable...")
    
    # Determine OS for correct path separator
    is_windows = sys.platform.startswith('win')
    path_sep = ';' if is_windows else ':'
    
    # Clean previous builds
    if Path('build').exists():
        shutil.rmtree('build')
    if Path('dist').exists():
        shutil.rmtree('dist')
    if Path('AGI_Assistant.spec').exists():
        Path('AGI_Assistant.spec').unlink()
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=AGI_Assistant",
        f"--add-data=src{path_sep}src",  # Correct separator for OS
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
        "--hidden-import=mss",
        "--hidden-import=sounddevice",
        "--hidden-import=faster_whisper",
        "--hidden-import=pytesseract",
        "--hidden-import=ollama",
        "--hidden-import=playwright",
        "--hidden-import=pyautogui",
        "--hidden-import=pygetwindow",
        "--hidden-import=pynput",
        "--collect-all=customtkinter",
        "--collect-all=PIL",
        "main.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build successful!")
        
        if is_windows:
            print(f"📦 Executable location: dist\\AGI_Assistant.exe")
        else:
            print(f"📦 Executable location: dist/AGI_Assistant")
            print("\n⚠️  Note: You built on Linux/Mac, so you got a Linux/Mac executable,")
            print("   not a Windows .exe. To build a Windows .exe, you need to run")
            print("   this script on a Windows machine or use GitHub Actions.")
        
        print("\n⚠️  External dependencies required:")
        print("   1. Install Tesseract OCR on target machine")
        print("   2. Install Ollama and pull phi3.5:latest model")
        print("   3. Install Playwright browsers: playwright install chromium")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found. Install it with: pip install pyinstaller")
        return False

if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)
EOF

# Commit both files
git add build_exe.bat build_exe.py
git commit -m "Add build_exe.bat for Windows and fix build_exe.py"
git push origin main

echo "✅ Created build_exe.bat and updated build_exe.py"