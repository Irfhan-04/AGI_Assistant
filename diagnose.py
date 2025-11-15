"""Diagnostic script to check system setup."""

import sys
import os
from pathlib import Path

print("=" * 60)
print("AGI Assistant - System Diagnostic")
print("=" * 60)
print()

# Check Python version
print(f"✓ Python version: {sys.version}")
print()

# Check required directories
print("Checking directories...")
base_dir = Path(__file__).parent
data_dir = base_dir / "data"
sessions_dir = data_dir / "sessions"
workflows_dir = data_dir / "workflows"
logs_dir = base_dir / "logs"

for dir_path, name in [(data_dir, "data"), (sessions_dir, "sessions"), 
                        (workflows_dir, "workflows"), (logs_dir, "logs")]:
    if dir_path.exists():
        print(f"✓ {name} directory exists: {dir_path}")
    else:
        print(f"✗ {name} directory missing, creating: {dir_path}")
        dir_path.mkdir(parents=True, exist_ok=True)
print()

# Check required packages
print("Checking Python packages...")
required_packages = [
    "customtkinter",
    "mss",
    "sounddevice",
    "numpy",
    "pynput",
    "psutil",
    "faster_whisper",
    "pytesseract",
    "PIL",
    "cv2",
    "ollama",
    "pyautogui",
    "playwright"
]

missing_packages = []
for package in required_packages:
    try:
        if package == "cv2":
            import cv2
        elif package == "PIL":
            from PIL import Image
        else:
            __import__(package)
        print(f"✓ {package}")
    except ImportError:
        print(f"✗ {package} - NOT INSTALLED")
        missing_packages.append(package)
print()

if missing_packages:
    print("⚠️  Missing packages. Install with:")
    print(f"pip install {' '.join(missing_packages)}")
    print()

# Check Tesseract
print("Checking Tesseract OCR...")
try:
    import pytesseract
    if os.name == 'nt':
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            print(f"✓ Tesseract found at: {tesseract_path}")
        else:
            print(f"✗ Tesseract not found at: {tesseract_path}")
            print("  Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    
    version = pytesseract.get_tesseract_version()
    print(f"✓ Tesseract version: {version}")
except Exception as e:
    print(f"✗ Tesseract error: {e}")
print()

# Check Ollama
print("Checking Ollama...")
try:
    import ollama
    models = ollama.list()
    model_names = [m['name'] for m in models.get('models', [])]
    print(f"✓ Ollama is running")
    print(f"✓ Available models: {', '.join(model_names)}")
    
    if 'phi3.5:latest' in model_names or 'phi3.5:mini' in model_names:
        print("✓ Phi3.5 model found")
    else:
        print("✗ Phi3.5 model not found")
        print("  Run: ollama pull phi3.5:latest")
except Exception as e:
    print(f"✗ Ollama error: {e}")
    print("  Make sure Ollama is installed and running")
    print("  Download from: https://ollama.ai/download")
print()

# Check Playwright
print("Checking Playwright...")
try:
    from playwright.sync_api import sync_playwright
    print("✓ Playwright installed")
    print("  If browsers not installed, run: playwright install chromium")
except Exception as e:
    print(f"✗ Playwright error: {e}")
print()

# Check audio devices
print("Checking audio devices...")
try:
    import sounddevice as sd
    devices = sd.query_devices()
    input_devices = [d for d in devices if d['max_input_channels'] > 0]
    print(f"✓ Found {len(input_devices)} input devices")
    for i, device in enumerate(input_devices):
        print(f"  {i+1}. {device['name']}")
except Exception as e:
    print(f"✗ Audio error: {e}")
print()

# Check imports from src
print("Checking project imports...")
try:
    sys.path.insert(0, str(base_dir))
    
    from src.config import STORAGE_CONFIG
    print("✓ src.config")
    
    from src.logger import get_logger
    print("✓ src.logger")
    
    from src.storage.database import Database
    print("✓ src.storage.database")
    
    from src.observation.session_manager import SessionManager
    print("✓ src.observation.session_manager")
    
    print("✓ All project imports successful")
except Exception as e:
    print(f"✗ Import error: {e}")
    import traceback
    traceback.print_exc()
print()

print("=" * 60)
print("Diagnostic complete!")
print("=" * 60)

if missing_packages:
    print("\n⚠️  Action required: Install missing packages")
    sys.exit(1)
else:
    print("\n✓ System ready to run!")
    sys.exit(0)