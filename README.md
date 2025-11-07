# The AGI Assistant

A local AI desktop assistant that observes, learns, and automates repetitive workflows - running 100% locally with no cloud dependencies.

## Overview

The AGI Assistant implements a complete **Observe → Understand → Automate** pipeline:

1. **Observe**: Captures screen activity, audio, and input events
2. **Understand**: Uses LLM (Ollama + Phi-3.5) to analyze patterns and generate workflows
3. **Automate**: Executes learned workflows using PyAutoGUI and Playwright

## Features

- 🎥 **Screen Recording**: Fast screenshot capture with activity detection
- 🎤 **Audio Recording**: Microphone capture with silence detection
- ⌨️ **Event Tracking**: Mouse clicks, keyboard input, and window changes
- 🧠 **AI Learning**: Automatic pattern detection across multiple sessions
- 🤖 **Workflow Generation**: LLM-powered workflow creation from user activity
- 🚀 **Automation**: Desktop and browser automation execution
- 🔒 **100% Local**: All processing happens on your machine, no cloud uploads
- 💾 **Storage Management**: Automatic cleanup of old session data

## Requirements

- **OS**: Windows 10/11
- **Python**: 3.10 or higher
- **RAM**: 8GB minimum (for Phi-3.5 Mini model)
- **Storage**: ~2GB for sessions and models

## Installation

### 1. Clone or Download

```bash
cd AGI
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install External Tools

#### Tesseract OCR
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
- Default installation path: `C:\Program Files\Tesseract-OCR`
- Add to PATH or configure in code if installed elsewhere

#### Ollama
Download and install from: https://ollama.ai/download

After installation, pull the Phi-3.5 Mini model:
```bash
ollama pull phi3.5:mini
```

#### Playwright Browsers
```bash
playwright install chromium
```

## Usage

### Starting the Application

```bash
python main.py
```

### Basic Workflow

1. **Start Recording**: Click "🔴 Start Watching" button
2. **Perform Your Task**: Do your repetitive task normally (e.g., create Excel report)
3. **Stop Recording**: Click "⏹️ Stop Watching" button
4. **Repeat**: Do the same task 2-3 more times
5. **Learn**: The AI will detect the pattern and generate a workflow
6. **Automate**: Click "▶️ Run Now" on the learned workflow card

### Example: Excel Report Automation

1. Start recording
2. Open Excel
3. Create a report with date, sales data, etc.
4. Save the file
5. Stop recording
6. Repeat steps 2-5 two more times
7. The AI will learn the pattern and create a workflow
8. Click "Run Now" to automate the task

## Project Structure

```
AGI/
├── src/
│   ├── observation/      # Screen, audio, event recording
│   ├── processing/        # Transcription, OCR, data fusion
│   ├── intelligence/     # LLM interface, workflow generation, pattern detection
│   ├── automation/       # Desktop, browser, file automation
│   ├── storage/          # Database and storage management
│   └── ui/               # CustomTkinter GUI
├── data/
│   ├── sessions/         # Recorded session data
│   └── workflows/        # Learned workflows database
├── logs/                 # Application logs
├── main.py               # Application entry point
└── requirements.txt      # Python dependencies
```

## Configuration

Edit `src/config.py` to customize:

- Storage limits and retention
- Screenshot intervals and quality
- Audio recording settings
- LLM model and settings
- Automation safety settings
- UI theme and colors

## Privacy

**Everything runs locally on your machine:**

- No cloud uploads
- No external network requests
- No data sharing
- All processing happens on your computer
- Your workflows stay yours

Session data is stored in `data/sessions/` and can be deleted at any time.

## Troubleshooting

### Ollama Connection Error
- Ensure Ollama is running: `ollama serve`
- Check if model is installed: `ollama list`
- Pull model if missing: `ollama pull phi3.5:mini`

### Tesseract OCR Error
- Verify Tesseract is installed and in PATH
- Check installation path in `src/config.py` if needed

### Audio Recording Issues
- Check microphone permissions
- Verify audio device is available
- Check `sounddevice` can access microphone

### Memory Issues
- Close other applications to free RAM
- Reduce screenshot frequency in config
- Use smaller Whisper model (base instead of small)

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Building Executable

```bash
pyinstaller --onefile --windowed --name "AGI_Assistant" main.py
```

## License

Built for the Humanity Founders Hackathon.

## Support

For issues or questions, check the logs in `logs/` directory.

---
