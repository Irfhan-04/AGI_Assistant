"""Improved build script for creating .exe executable with all dependencies."""

import os
import sys
import subprocess
from pathlib import Path
import shutil

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    missing = []
    
    # Check PyInstaller
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        missing.append("pyinstaller")
    
    # Check other critical packages
    packages = [
        'customtkinter', 'mss', 'sounddevice', 'faster_whisper',
        'pytesseract', 'ollama', 'playwright', 'pyautogui'
    ]
    
    for pkg in packages:
        try:
            __import__(pkg.replace('-', '_'))
            print(f"✓ {pkg} found")
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    print("✓ All dependencies found\n")
    return True

def clean_build_dirs():
    """Clean previous build directories."""
    print("🧹 Cleaning previous build directories...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")
    
    # Remove spec file
    if os.path.exists('AGI_Assistant.spec'):
        os.remove('AGI_Assistant.spec')
        print("  Removed AGI_Assistant.spec")
    
    print()

def create_hooks_dir():
    """Create PyInstaller hooks directory for custom imports."""
    hooks_dir = Path("hooks")
    hooks_dir.mkdir(exist_ok=True)
    
    # Create hook for customtkinter
    hook_ctk = hooks_dir / "hook-customtkinter.py"
    hook_ctk.write_text("""
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('customtkinter')
hiddenimports = collect_submodules('customtkinter')
""")
    
    print("✓ Created PyInstaller hooks\n")
    return str(hooks_dir)

def build_exe():
    """Build executable using PyInstaller."""
    
    print("="*60)
    print("🔨 Building The AGI Assistant Executable")
    print("="*60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Clean previous builds
    clean_build_dirs()
    
    # Create hooks directory
    hooks_path = create_hooks_dir()
    
    print("🔧 Building executable with PyInstaller...")
    print()
    
    # PyInstaller command with all options
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=AGI_Assistant",
        "--icon=NONE",
        
        # Add data files
        "--add-data=src;src",
        
        # Hidden imports (critical packages)
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=mss",
        "--hidden-import=sounddevice",
        "--hidden-import=soundfile",
        "--hidden-import=faster_whisper",
        "--hidden-import=pytesseract",
        "--hidden-import=ollama",
        "--hidden-import=playwright",
        "--hidden-import=pyautogui",
        "--hidden-import=pygetwindow",
        "--hidden-import=pynput",
        "--hidden-import=psutil",
        "--hidden-import=numpy",
        "--hidden-import=cv2",
        "--hidden-import=sqlite3",
        "--hidden-import=wave",
        "--hidden-import=json",
        "--hidden-import=threading",
        "--hidden-import=pathlib",
        
        # Collect all data/submodules for key packages
        "--collect-all=customtkinter",
        "--collect-all=PIL",
        "--collect-all=tkinter",
        
        # Hooks directory
        f"--additional-hooks-dir={hooks_path}",
        
        # PyInstaller options
        "--noconfirm",
        "--clean",
        
        # Main entry point
        "main.py"
    ]
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Build successful!\n")
        print("="*60)
        print("📦 Executable Information")
        print("="*60)
        
        exe_path = Path("dist/AGI_Assistant.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"Location: {exe_path.absolute()}")
            print(f"Size: {size_mb:.2f} MB")
            print()
            
            print("⚠️  IMPORTANT: Before distributing, ensure target machine has:")
            print("   1. Tesseract OCR installed")
            print("      Download: https://github.com/UB-Mannheim/tesseract/wiki")
            print()
            print("   2. Ollama installed with phi3.5:mini model")
            print("      Download: https://ollama.ai/download")
            print("      Then run: ollama pull phi3.5:mini")
            print()
            print("   3. Playwright browsers installed")
            print("      Run: playwright install chromium")
            print()
            
            return True
        else:
            print("❌ Executable not found after build!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed!")
        print(f"\nError output:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found. Install it with: pip install pyinstaller")
        return False

def create_installer_script():
    """Create a simple batch installer helper."""
    installer = Path("install_dependencies.bat")
    installer.write_text("""@echo off
echo ========================================
echo AGI Assistant - Dependency Installer
echo ========================================
echo.

echo Installing Tesseract OCR...
echo Please download from: https://github.com/UB-Mannheim/tesseract/wiki
echo After installation, add to PATH or note the installation directory.
pause

echo.
echo Installing Ollama...
echo Please download from: https://ollama.ai/download
echo After installation, open a new terminal and run: ollama pull phi3.5:mini
pause

echo.
echo Installing Playwright browsers...
playwright install chromium
echo.

echo ========================================
echo Installation complete!
echo ========================================
pause
""")
    print(f"✓ Created dependency installer: {installer}\n")

if __name__ == "__main__":
    success = build_exe()
    
    if success:
        print("\n" + "="*60)
        print("🎉 Build Complete!")
        print("="*60)
        
        # Create installer helper
        create_installer_script()
        
        print("\n📝 Next Steps:")
        print("   1. Test the executable on your machine")
        print("   2. For distribution, include install_dependencies.bat")
        print("   3. Create a README with setup instructions")
        print()
        
    sys.exit(0 if success else 1)