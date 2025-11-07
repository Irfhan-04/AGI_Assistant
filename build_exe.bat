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
echo   2. Ollama is installed and phi3.5:mini model is pulled
echo   3. Playwright browsers are installed
echo.
pause

