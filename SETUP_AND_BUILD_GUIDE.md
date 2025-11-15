# 🐧 The AGI Assistant - Linux Setup Guide

## Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+, Debian 11+, Fedora 35+, or compatible Linux distribution
- **Python**: 3.10 or higher
- **RAM**: 8GB minimum
- **Storage**: 2GB free disk space
- **Display**: X11 or Wayland (X11 recommended for window management)

---

## 📦 Installation Steps

### Step 1: System Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y \
    python3 python3-pip python3-venv \
    tesseract-ocr tesseract-ocr-eng \
    xdotool wmctrl \
    portaudio19-dev \
    libgirepository1.0-dev \
    gcc g++ make

# Fedora/RHEL
sudo dnf install -y \
    python3 python3-pip python3-virtualenv \
    tesseract tesseract-langpack-eng \
    xdotool wmctrl \
    portaudio-devel \
    gobject-introspection-devel \
    gcc gcc-c++ make

# Arch Linux
sudo pacman -S \
    python python-pip \
    tesseract tesseract-data-eng \
    xdotool wmctrl \
    portaudio \
    gobject-introspection \
    base-devel
```

### Step 2: Install Ollama

```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation
ollama --version

# Pull the Phi-3.5 Mini model
ollama pull phi3.5:mini

# Verify model is downloaded
ollama list
```

### Step 3: Clone/Download Project

```bash
cd ~
# Assuming you have the AGI folder
cd AGI
```

### Step 4: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 5: Install Python Dependencies

```bash
# Install from requirements file
pip install -r requirements-linux.txt

# OR install from original requirements
pip install -r requirements.txt
```

### Step 6: Install Playwright Browsers

```bash
# Install Chromium for Playwright
playwright install chromium

# Install system dependencies for Playwright
playwright install-deps chromium
```

### Step 7: Verify Installation

```bash
# Run verification script
python3 verify_setup.py
```

Expected output: All checks should show ✅ PASS

---

## 🚀 Running the Application

### Development Mode

```bash
# Activate virtual environment if not already activated
source venv/bin/activate

# Run application
python3 main.py
```

### First Run

The application will:
1. Create necessary directories (`data/`, `logs/`)
2. Check for Tesseract OCR
3. Check for Ollama connection
4. Display the main window

---

## 🔨 Building Executable

### Build for Linux

```bash
# Make build script executable
chmod +x build_linux.sh

# Run build script
./build_linux.sh
```

Output: `dist/AGI_Assistant`

### Test the Executable

```bash
# Make executable (if not already)
chmod +x dist/AGI_Assistant

# Run
./dist/AGI_Assistant
```

---

## 🐛 Troubleshooting

### Issue: "xdotool: command not found"

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install xdotool wmctrl

# Fedora
sudo dnf install xdotool wmctrl

# Arch
sudo pacman -S xdotool wmctrl
```

### Issue: "Tesseract not found"

**Solution:**
```bash
# Check if installed
which tesseract

# If not found, install
sudo apt install tesseract-ocr tesseract-ocr-eng

# Verify
tesseract --version
```

### Issue: "Ollama connection failed"

**Solution:**
```bash
# Check if Ollama is running
systemctl status ollama

# Start Ollama service
sudo systemctl start ollama

# Enable on boot
sudo systemctl enable ollama

# Or run manually
ollama serve
```

### Issue: "Audio recording not working"

**Solution:**
```bash
# Install PortAudio
sudo apt install portaudio19-dev python3-pyaudio

# Check audio devices
python3 -c "import sounddevice; print(sounddevice.query_devices())"

# Test microphone
arecord -l
```

### Issue: "Window tracking not working"

**Solution:**
```bash
# Install X11 tools
sudo apt install xdotool wmctrl x11-utils

# Test xdotool
xdotool getactivewindow getwindowname

# If using Wayland, switch to X11 for better compatibility
# Log out and select "Ubuntu on Xorg" at login
```

### Issue: "CustomTkinter not displaying correctly"

**Solution:**
```bash
# Install tkinter system package
sudo apt install python3-tk

# Reinstall CustomTkinter
pip install --upgrade --force-reinstall customtkinter
```

### Issue: "Permission denied" when running executable

**Solution:**
```bash
# Make executable
chmod +x dist/AGI_Assistant

# Check SELinux (Fedora/RHEL)
sestatus
# If enabled, you may need to adjust SELinux policies
```

---

## 🔧 Optional: Create Desktop Entry

Create `~/.local/share/applications/agi-assistant.desktop`:

```desktop
[Desktop Entry]
Name=AGI Assistant
Comment=Local AI Workflow Automation
Exec=/path/to/AGI/dist/AGI_Assistant
Icon=/path/to/AGI/icon.png
Terminal=false
Type=Application
Categories=Utility;Development;
```

Make it executable:
```bash
chmod +x ~/.local/share/applications/agi-assistant.desktop
```

---

## 📝 Linux-Specific Notes

### Window Management
- **X11**: Fully supported with xdotool/wmctrl
- **Wayland**: Limited support, some window operations may not work
- **Recommendation**: Use X11 session for best compatibility

### Permissions
The application needs:
- ✅ Screen capture (automatic)
- ✅ Microphone access (check `pavucontrol`)
- ✅ Keyboard/mouse monitoring (automatic with pynput)
- ✅ Window management (xdotool/wmctrl)

### Audio Issues
If audio recording doesn't work:
```bash
# Check PulseAudio
pulseaudio --check
pulseaudio --start

# Check ALSA
arecord -l

# Test recording
arecord -d 5 test.wav
```

---

## 🚀 Performance Tips

### 1. Reduce Resource Usage
Edit `src/config.py`:
```python
OBSERVATION_CONFIG = {
    "screenshot": {
        "interval_ms": 3000,  # Increase to 3 seconds
        "quality": 60,         # Reduce quality
    }
}
```

### 2. Disable Compositor (for better performance)
```bash
# GNOME
gsettings set org.gnome.desktop.interface enable-animations false

# KDE
kwriteconfig5 --file kwinrc --group Compositing --key Enabled false
```

### 3. Use Lightweight Desktop Environment
Consider using:
- XFCE
- LXDE
- i3wm

---

## 🔒 Privacy on Linux

### Data Location
```bash
# Session data
~/.local/share/AGI/data/sessions/

# Workflows
~/.local/share/AGI/data/workflows.db

# Logs
~/.local/share/AGI/logs/
```

### Clear All Data
```bash
rm -rf ~/.local/share/AGI/data/
```

---

## 📋 Command Reference

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-linux.txt
playwright install chromium

# Run
python3 main.py

# Build
./build_linux.sh

# Test executable
./dist/AGI_Assistant

# Install system dependencies
./install_linux_dependencies.sh

# Clean build
rm -rf build dist *.spec
```

---

## 🆘 Getting Help

### Check Logs
```bash
# Application logs
tail -f logs/agi_assistant_$(date +%Y%m%d).log

# System logs
journalctl -xe
```

### Test Components

**Test OCR:**
```bash
python3 -c "
from src.processing.ocr_engine import OCREngine
ocr = OCREngine()
print('OCR OK' if ocr.test_ocr() else 'OCR FAILED')
"
```

**Test Ollama:**
```bash
python3 -c "
from src.intelligence.llm_interface import LLMInterface
llm = LLMInterface()
print('Ollama OK' if llm.test_connection() else 'Ollama FAILED')
"
```

**Test Audio:**
```bash
python3 -c "
import sounddevice as sd
print('Audio devices:', sd.query_devices())
"
```

---

## ✅ Verification Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] All Python packages installed
- [ ] Tesseract OCR installed and working
- [ ] Ollama installed and phi3.5:mini model downloaded
- [ ] Playwright browsers installed
- [ ] xdotool and wmctrl installed (X11)
- [ ] Application runs: `python3 main.py`
- [ ] Can record a session
- [ ] No errors in logs
- [ ] Executable builds successfully
- [ ] Executable runs without errors

---

## 🎉 Success!

If all checks pass, you're ready to use The AGI Assistant on Linux!

For issues specific to your distribution, check:
- **Ubuntu**: https://help.ubuntu.com
- **Fedora**: https://docs.fedoraproject.org
- **Arch**: https://wiki.archlinux.org

Happy automating! 🚀