# AGI Assistant - Complete Setup Guide

## 🎯 Overview
AGI Assistant is a privacy-first desktop AI that observes your computer usage, learns your workflows, and automates repetitive tasks. Everything runs locally on your machine with no cloud dependencies.

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 20.04+)
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space for dependencies and data
- **Microphone**: Optional (for voice command features)

### Supported Features by Platform
| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| Screenshot Capture | ✅ | ✅ | ✅ |
| OCR Text Extraction | ✅ | ✅ | ✅ |
| Audio Recording | ✅ | ✅ | ✅ |
| Speech Transcription | ✅ | ✅ | ✅ |
| Workflow Automation | ✅ | ✅ | ✅ |

---

## 🚀 Quick Start Installation

### Step 1: Install Python
If you don't have Python installed:

**Windows:**
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer and **check "Add Python to PATH"**
3. Verify: Open Command Prompt and run `python --version`

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python@3.11

# Verify
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
python3 --version
```

### Step 2: Install System Dependencies

#### Tesseract OCR (for text extraction)

**Windows:**
1. Download installer: [GitHub Tesseract Release](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer (default location: `C:\Program Files\Tesseract-OCR`)
3. The application will auto-detect installation

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt install tesseract-ocr
```

#### PortAudio (for audio recording)

**Windows:** Usually included with Python

**macOS:**
```bash
brew install portaudio
```

**Linux:**
```bash
sudo apt install portaudio19-dev
```

### Step 3: Install Python Dependencies

Navigate to the project folder and run:

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### If You Get Errors

**"No module named 'tkinter'":**
- **Linux**: `sudo apt install python3-tk`
- **macOS**: Should be included; reinstall Python from python.org if missing

**sounddevice installation fails:**
- Install PortAudio first (see above)
- Try: `pip install sounddevice --no-cache-dir`

**faster-whisper fails:**
- Make sure you have Python 3.8-3.11 (not 3.12+)
- Update pip: `pip install --upgrade pip setuptools wheel`

---

## 📦 Detailed Dependencies

### Core Dependencies (Required)
```txt
mss==9.0.1              # Screen capture
pillow==10.1.0          # Image processing
numpy==1.26.4           # Numerical operations
pytesseract==0.3.10     # OCR wrapper
pyautogui==0.9.54       # GUI automation
```

### Optional Dependencies (For Enhanced Features)
```txt
sounddevice==0.4.6      # Audio recording
soundfile==0.12.1       # Audio file handling
faster-whisper==0.10.0  # Speech transcription
```

### Minimal Installation (Without Audio)
If you don't need audio features:
```bash
pip install mss pillow numpy pytesseract pyautogui
```

---

## 🎮 Running the Application

### Observer Mode (Data Collection)
```bash
python agi_assistant_main.py
```

**What it does:**
- Captures screenshots every 5 seconds
- Records audio in 10-second chunks (if microphone available)
- Extracts text from screenshots using OCR
- Transcribes voice commands using Whisper AI
- Stores all data locally in `agi_data/` folder

**Controls:**
1. Click **"Start Observing"** to begin
2. Perform your repetitive tasks normally
3. (Optional) Speak commands while working
4. After 30-60 seconds, click **"Analyze Workflows"**
5. Click **"Stop Observing"** when done

### Automator Mode (Workflow Execution)
```bash
python automation_executor.py
```

**What it does:**
- Loads detected workflows from Observer
- Shows workflow details and actions
- Executes automated tasks step-by-step

**Controls:**
1. Select a workflow from the list
2. Review the actions in the details panel
3. Click **"Execute Selected"**
4. Confirm the execution
5. Watch the automation happen!

**Safety Features:**
- ⚠️ **FAILSAFE**: Move mouse to top-left corner to emergency stop
- 3-second countdown before execution
- Pause/Resume during execution
- Stop button to cancel anytime

---

## 🔧 Configuration

### Adjusting Capture Intervals
Edit `agi_assistant_main.py`:
```python
class Config:
    SCREENSHOT_INTERVAL = 5   # Change to 3 or 10 seconds
    AUDIO_CHUNK_DURATION = 10 # Change audio recording length
```

### Data Storage Location
All data is stored in `agi_data/` folder:
```
agi_data/
├── screenshots/     # Screen captures
├── audio/          # Voice recordings
├── workflows/      # Detected patterns
├── ocr_*.txt       # Extracted text
└── transcript_*.txt # Voice transcriptions
```

### Privacy & Data Management
- **All data is local** - nothing leaves your computer
- **No internet required** - runs completely offline
- **Delete anytime** - use "Clear Data" button or delete `agi_data/` folder
- **No tracking** - zero telemetry or analytics

---

## 🐛 Troubleshooting

### "Tesseract not found"
```bash
# Check if installed
tesseract --version

# If not found, install (see Step 2 above)
```

The enhanced application will auto-detect Tesseract in common locations:
- Windows: `C:\Program Files\Tesseract-OCR\`, user AppData
- macOS: `/usr/local/bin/`, `/opt/homebrew/bin/`
- Linux: `/usr/bin/`, `/usr/local/bin/`

### "No audio devices found"
- Check microphone permissions in OS settings
- **macOS**: System Preferences → Security & Privacy → Microphone
- **Windows**: Settings → Privacy → Microphone
- Connect a microphone or headset

### "Screenshot capture failed"
- On Linux, may need: `sudo apt install python3-xlib`
- Check screen recording permissions on macOS

### "PyAutoGUI click not working"
- Some applications may block automation (security feature)
- Try running the application as administrator (Windows) or with elevated privileges

### Performance Issues
- **High CPU usage**: Increase `SCREENSHOT_INTERVAL` to 10+ seconds
- **Memory issues**: Clear old data regularly with "Clear Data" button
- **Whisper slow**: Use `tiny` model instead of `base`:
  ```python
  WhisperModel("tiny", device="cpu", compute_type="int8")
  ```

---

## 🎓 Usage Tips

### Getting Better Workflow Detection
1. **Be deliberate**: Perform tasks step-by-step
2. **Use voice**: Speak what you're doing ("Opening Excel", "Entering data")
3. **Repetition**: Do the same task 2-3 times during observation
4. **Duration**: Observe for at least 1-2 minutes
5. **Focus**: Work on one workflow at a time

### Creating Effective Automations
1. **Consistent windows**: Position applications the same way
2. **Clear actions**: Workflows with clear, repeatable steps work best
3. **Test first**: Review detected actions before executing
4. **Start simple**: Begin with basic tasks (opening apps, typing text)

### Automation Best Practices
1. **Save work first**: Automation can't undo mistakes
2. **Close unneeded apps**: Reduces interference
3. **Don't move mouse**: Let automation control the cursor
4. **Watch first run**: Monitor to ensure it works correctly
5. **Use pause**: Pause if something unexpected happens

---

## 🔒 Security & Privacy

### What Data is Collected?
- **Screenshots**: Visual captures of your screen
- **Audio**: Voice recordings from microphone (if enabled)
- **OCR Text**: Text extracted from screenshots
- **Transcripts**: Text from voice recordings
- **Workflows**: JSON files of detected patterns

### Where is Data Stored?
- **Local only**: All data stays in `agi_data/` folder
- **No cloud**: Nothing uploaded to internet
- **No tracking**: No analytics or telemetry
- **Full control**: Delete `agi_data/` anytime

### Privacy Recommendations
1. **Review data**: Check `agi_data/` folder periodically
2. **Clear sensitive**: Delete screenshots with passwords/personal info
3. **Disable audio**: If you don't need voice commands
4. **Use for work**: Focus on work tasks, not personal browsing
5. **Test safely**: Use test data when learning the system

---

## 🚧 Known Limitations

### Current Limitations
- **Pattern detection**: Simple keyword-based (not AI-powered by default)
- **No multi-monitor**: Captures primary monitor only
- **Limited actions**: Basic keyboard/mouse automation
- **No clipboard**: Can't access or paste clipboard content
- **Application-specific**: Some apps block automation

### Coming Soon (Future Enhancements)
- [ ] Multi-modal LLM integration (Llama 3.2 Vision)
- [ ] Browser automation via Playwright
- [ ] Custom workflow editor GUI
- [ ] Continuous learning from corrections
- [ ] Cross-platform installers
- [ ] Voice-activated execution
- [ ] Multiple monitor support

---

## 📚 Additional Resources

### Python Packages Documentation
- [mss - Screen Capture](https://python-mss.readthedocs.io/)
- [pytesseract - OCR](https://github.com/madmaze/pytesseract)
- [PyAutoGUI - Automation](https://pyautogui.readthedocs.io/)
- [faster-whisper - Transcription](https://github.com/guillaumekln/faster-whisper)

### External Tools
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Python Download](https://www.python.org/downloads/)

### Getting Help
1. Check `ARCHITECTURE.md` for technical details
2. Review error messages in the application log
3. Enable verbose logging for debugging
4. Test with minimal features first (disable audio/OCR)

---

## 🎉 Success Checklist

Before using AGI Assistant, verify:
- [ ] Python 3.8+ installed and in PATH
- [ ] All pip dependencies installed successfully
- [ ] Tesseract OCR installed and detected
- [ ] PortAudio installed (for audio features)
- [ ] Observer application launches without errors
- [ ] Can capture at least one screenshot
- [ ] Data appears in `agi_data/` folder
- [ ] Automator application can load workflows
- [ ] Understanding of safety features (failsafe, pause, stop)

## 🏁 Ready to Go!

You're all set! Start with the Observer to collect workflow data, then use the Automator to execute your automated tasks.

**Remember:**
- Move mouse to top-left corner for emergency stop
- Start with simple workflows
- Review detected actions before executing
- All data is local and private

Happy automating! 🚀
