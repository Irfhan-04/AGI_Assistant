"""Verification script for Linux - Check dependencies."""

import sys
import os
import platform
import subprocess

def check_platform():
    """Check if running on Linux."""
    print("="*60)
    print("Checking Platform...")
    print("="*60)
    
    system = platform.system()
    print(f"Operating System: {system}")
    print(f"Distribution: {platform.platform()}")
    
    if system != 'Linux':
        print(f"⚠️  Warning: This script is optimized for Linux")
        print(f"   Current platform: {system}")
    else:
        print("✅ Linux platform detected")
    
    print()
    return True

def check_python_version():   # ← add this block here
    """Check Python version."""
    print("="*60)
    print("Checking Python Version...")
    print("="*60)
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print(f"Python version: {version_str}")
    
    if version.major == 3 and version.minor >= 10:
        print("✅ Python version OK\n")
        return True
    else:
        print("❌ Python 3.10+ required\n")
        return False

def check_packages():
    """Check if all required packages are installed."""
    print("="*60)
    print("Checking Python Packages...")
    print("="*60)

    required_packages = [
        ('customtkinter', 'CustomTkinter'),
        ('mss', 'MSS'),
        ('sounddevice', 'SoundDevice'),
        ('numpy', 'NumPy'),
        ('PIL', 'Pillow'),
        ('pynput', 'pynput'),
        ('psutil', 'psutil'),
        ('faster_whisper', 'Faster-Whisper'),
        ('pytesseract', 'Pytesseract'),
        ('ollama', 'Ollama'),
        ('playwright', 'Playwright'),
        ('pyautogui', 'PyAutoGUI'),
    ]

    all_ok = True
    headless = "DISPLAY" not in os.environ

    if headless:
        print("⚠️  No DISPLAY detected — running in headless mode.")
        print("   Skipping GUI-related packages (PyAutoGUI, mouseinfo).\n")
        # Remove GUI packages from checks
        required_packages = [
            (m, n) for m, n in required_packages
            if m not in ("pyautogui", "mouseinfo")
        ]

    for module_name, display_name in required_packages:
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
        except ImportError:
            print(f"❌ {display_name} NOT FOUND")
            print(f"   Install with: pip install {display_name.lower()}")
            all_ok = False
        except KeyError as e:
            # This specifically catches DISPLAY errors from mouseinfo
            if "DISPLAY" in str(e):
                print(f"⚠️  Skipped {display_name} (no GUI display found).")
            else:
                raise

    print()
    return all_ok

def check_tesseract():
    """Check if Tesseract OCR is installed."""
    print("="*60)
    print("Checking Tesseract OCR...")
    print("="*60)
    
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ {version_line}")
            print()
            return True
    except FileNotFoundError:
        print("❌ Tesseract OCR NOT FOUND")
        print("   Install with: sudo apt install tesseract-ocr tesseract-ocr-eng")
        print()
        return False
    except Exception as e:
        print(f"❌ Error checking Tesseract: {e}")
        print()
        return False

def check_x11_tools():
    """Check if X11 tools are installed (Linux-specific)."""
    print("="*60)
    print("Checking X11 Tools (Linux)...")
    print("="*60)
    
    tools = ['xdotool', 'wmctrl']
    all_ok = True
    
    for tool in tools:
        try:
            result = subprocess.run([tool, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 or 'xdotool' in result.stderr:
                print(f"✅ {tool} found")
            else:
                print(f"⚠️  {tool} may not be working correctly")
        except FileNotFoundError:
            print(f"❌ {tool} NOT FOUND")
            print(f"   Install with: sudo apt install {tool}")
            all_ok = False
        except Exception as e:
            print(f"⚠️  Error checking {tool}: {e}")
    
    print()
    return all_ok

def check_ollama():
    """Check if Ollama is installed and model is available."""
    print("="*60)
    print("Checking Ollama...")
    print("="*60)
    
    # Check if Ollama is installed
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Ollama found: {result.stdout.strip()}")
        else:
            print("❌ Ollama NOT FOUND")
            print("   Download from: https://ollama.ai/download")
            print()
            return False
    except FileNotFoundError:
        print("❌ Ollama NOT FOUND")
        print("   Download from: https://ollama.ai/download")
        print()
        return False
    
    # Check if model is installed
    try:
        import ollama
        response = ollama.list()
        models = [model["name"] for model in response.get("models", [])]
        
        if "phi3.5:mini" in models or any("phi3.5" in m for m in models):
            print("✅ phi3.5:mini model found")
            print()
            return True
        else:
            print("⚠️  Ollama found but phi3.5:mini model not installed")
            print("   Run: ollama pull phi3.5:mini")
            print(f"   Available models: {', '.join(models) if models else 'None'}")
            print()
            return False
    except Exception as e:
        print(f"⚠️  Could not check Ollama models: {e}")
        print("   Make sure Ollama service is running")
        print()
        return False

def check_playwright():
    """Check if Playwright browsers are installed."""
    print("="*60)
    print("Checking Playwright Browsers...")
    print("="*60)
    
    try:
        from playwright.sync_api import sync_playwright
        print("✅ Playwright package found")
        print("   If browser automation doesn't work, run: playwright install chromium")
        print()
        return True
    except Exception as e:
        print("❌ Playwright NOT FOUND")
        print("   Install with: pip install playwright")
        print("   Then run: playwright install chromium")
        print()
        return False

def check_audio():
    """Check audio system."""
    print("="*60)
    print("Checking Audio System...")
    print("="*60)
    
    # Skip audio checks in headless environments like Codespaces/Docker
    if os.environ.get("CODESPACES") or not os.path.exists("/dev/snd"):
        print("⚠️  Headless environment detected — skipping audio input check.")
        print()
        return True

    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        
        if input_devices:
            print(f"✅ Found {len(input_devices)} input device(s)")
            print(f"   Default input: {sd.query_devices(kind='input')['name']}")
            print()
            return True
        else:
            print("⚠️  No audio input devices found")
            print("   Check your microphone connection")
            print()
            return False
    except Exception as e:
        print(f"❌ Error checking audio: {e}")
        print("   Install with: sudo apt install portaudio19-dev")
        print()
        return False

def check_directories():
    """Check if required directories exist or can be created."""
    print("="*60)
    print("Checking Directories...")
    print("="*60)
    
    required_dirs = ['data', 'data/sessions', 'data/workflows', 'logs']
    all_ok = True
    
    for dir_path in required_dirs:
        try:
            os.makedirs(dir_path, exist_ok=True)
            print(f"✅ {dir_path}/ ready")
        except Exception as e:
            print(f"❌ Cannot create {dir_path}/: {e}")
            all_ok = False
    
    print()
    return all_ok

def main():
    """Run all checks."""
    print("\n")
    print("🐧 THE AGI ASSISTANT - LINUX SETUP VERIFICATION")
    print("\n")
    
    results = {
        "Platform": check_platform(),
        "Python Version": check_python_version(),
        "Python Packages": check_packages(),
        "Tesseract OCR": check_tesseract(),
        "X11 Tools": check_x11_tools(),
        "Ollama": check_ollama(),
        "Playwright": check_playwright(),
        "Audio System": check_audio(),
        "Directories": check_directories(),
    }
    
    print("="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check:20} {status}")
    
    print()
    
    all_passed = all(results.values())
    
    if all_passed:
        print("🎉 All checks passed! You're ready to run the application.")
        print("   Start with: python3 main.py")
    else:
        print("⚠️  Some checks failed. Please install missing dependencies.")
        print("   See messages above for installation instructions.")
        print()
        print("Quick fix (Ubuntu/Debian):")
        print("   sudo apt install tesseract-ocr xdotool wmctrl portaudio19-dev")
        print("   ollama pull phi3.5:mini")
    
    print("\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())