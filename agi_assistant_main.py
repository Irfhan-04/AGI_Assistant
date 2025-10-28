"""
AGI Assistant - Desktop AI that Observes, Learns, and Automates
Round 1: Observe & Understand MVP
"""

import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext
import mss
import sounddevice as sd
import soundfile as sf
import numpy as np
from PIL import Image
import pytesseract  # For OCR
from faster_whisper import WhisperModel
import pyautogui

# Add this after the imports, before the Config class:
import pytesseract

# Windows users - UPDATE THIS PATH to match your Tesseract installation:
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Irfhan Ahamed\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Mac users:
# pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

# Linux users:
# Usually no need to set path, it's in system PATH

# Configuration
class Config:
    OUTPUT_DIR = Path("agi_data")
    SCREENSHOTS_DIR = OUTPUT_DIR / "screenshots"
    AUDIO_DIR = OUTPUT_DIR / "audio"
    WORKFLOWS_DIR = OUTPUT_DIR / "workflows"
    
    SCREENSHOT_INTERVAL = 5  # seconds
    AUDIO_CHUNK_DURATION = 10  # seconds
    SAMPLE_RATE = 16000
    
    # Create directories
    for dir_path in [OUTPUT_DIR, SCREENSHOTS_DIR, AUDIO_DIR, WORKFLOWS_DIR]:
        dir_path.mkdir(exist_ok=True)

class ScreenCapture:
    """Captures screenshots at regular intervals"""
    
    def __init__(self):
        self.is_recording = False
        self.screenshot_count = 0
        
    def start(self):
        self.is_recording = True
        threading.Thread(target=self._capture_loop, daemon=True).start()
        
    def stop(self):
        self.is_recording = False
        
    def _capture_loop(self):
        with mss.mss() as sct:
            while self.is_recording:
                try:
                    # Capture primary monitor
                    screenshot = sct.grab(sct.monitors[1])
                    img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                    
                    # Save with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = Config.SCREENSHOTS_DIR / f"screen_{timestamp}.png"
                    img.save(filename)
                    
                    self.screenshot_count += 1
                    
                    # Extract text from screenshot using OCR
                    text = pytesseract.image_to_string(img)
                    if text.strip():
                        self._save_ocr_data(timestamp, text)
                    
                    time.sleep(Config.SCREENSHOT_INTERVAL)
                except Exception as e:
                    print(f"Screenshot error: {e}")
                    
    def _save_ocr_data(self, timestamp, text):
        """Save OCR extracted text"""
        ocr_file = Config.OUTPUT_DIR / f"ocr_{timestamp}.txt"
        with open(ocr_file, 'w', encoding='utf-8') as f:
            f.write(text)

class AudioRecorder:
    """Records audio and transcribes it locally"""
    
    def __init__(self):
        self.is_recording = False
        self.whisper_model = None
        
    def initialize_whisper(self):
        """Load Whisper model for transcription"""
        print("Loading Whisper model...")
        self.whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        print("Whisper model loaded!")
        
    def start(self):
        self.is_recording = True
        threading.Thread(target=self._record_loop, daemon=True).start()
        
    def stop(self):
        self.is_recording = False
        
    def _record_loop(self):
        while self.is_recording:
            try:
                # Record audio chunk
                duration = Config.AUDIO_CHUNK_DURATION
                audio_data = sd.rec(
                    int(duration * Config.SAMPLE_RATE),
                    samplerate=Config.SAMPLE_RATE,
                    channels=1,
                    dtype='float32'
                )
                sd.wait()
                
                # Save audio file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                audio_file = Config.AUDIO_DIR / f"audio_{timestamp}.wav"
                sf.write(audio_file, audio_data, Config.SAMPLE_RATE)
                
                # Transcribe if Whisper is loaded
                if self.whisper_model and np.max(np.abs(audio_data)) > 0.01:
                    self._transcribe(audio_file, timestamp)
                    
            except Exception as e:
                print(f"Audio recording error: {e}")
                
    def _transcribe(self, audio_file, timestamp):
        """Transcribe audio file"""
        try:
            segments, info = self.whisper_model.transcribe(str(audio_file))
            transcription = " ".join([segment.text for segment in segments])
            
            if transcription.strip():
                # Save transcription
                text_file = Config.OUTPUT_DIR / f"transcript_{timestamp}.txt"
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(transcription)
                print(f"Transcribed: {transcription[:50]}...")
        except Exception as e:
            print(f"Transcription error: {e}")

class WorkflowAnalyzer:
    """Analyzes captured data to identify workflows"""
    
    def __init__(self):
        self.detected_workflows = []
        
    def analyze(self):
        """Analyze recent screenshots and transcriptions"""
        workflows = []
        
        # Get recent OCR texts
        ocr_files = sorted(Config.OUTPUT_DIR.glob("ocr_*.txt"))[-10:]
        ocr_texts = []
        for file in ocr_files:
            with open(file, 'r', encoding='utf-8') as f:
                ocr_texts.append(f.read())
        
        # Get recent transcriptions
        transcript_files = sorted(Config.OUTPUT_DIR.glob("transcript_*.txt"))[-10:]
        transcripts = []
        for file in transcript_files:
            with open(file, 'r', encoding='utf-8') as f:
                transcripts.append(f.read())
        
        # Simple pattern detection (this is where you'd use an LLM in production)
        workflow = self._detect_patterns(ocr_texts, transcripts)
        
        if workflow:
            workflows.append(workflow)
            self._save_workflow(workflow)
            
        return workflows
    
    def _detect_patterns(self, ocr_texts, transcripts):
        """Simple pattern detection - enhance with LLM"""
        combined_text = " ".join(ocr_texts + transcripts).lower()
        
        # Example patterns
        patterns = {
            "excel": ["excel", "spreadsheet", "cells", "formula"],
            "browser": ["chrome", "firefox", "search", "google"],
            "file_management": ["folder", "file", "rename", "move", "copy"],
            "form_filling": ["form", "input", "submit", "field"]
        }
        
        detected = []
        for category, keywords in patterns.items():
            if sum(keyword in combined_text for keyword in keywords) >= 2:
                detected.append(category)
        
        if detected:
            return {
                "timestamp": datetime.now().isoformat(),
                "categories": detected,
                "description": f"Detected workflow: {', '.join(detected)}",
                "actions": self._generate_actions(detected)
            }
        return None
    
    def _generate_actions(self, categories):
        """Generate automation actions based on detected patterns"""
        actions = []
        if "excel" in categories:
            actions.append("Open Excel application")
            actions.append("Enter data in cells")
            actions.append("Save file")
        if "browser" in categories:
            actions.append("Open web browser")
            actions.append("Navigate to URL")
            actions.append("Perform search")
        return actions
    
    def _save_workflow(self, workflow):
        """Save detected workflow to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        workflow_file = Config.WORKFLOWS_DIR / f"workflow_{timestamp}.json"
        with open(workflow_file, 'w') as f:
            json.dump(workflow, f, indent=2)

class AGIAssistantGUI:
    """Main GUI for the AGI Assistant"""
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("AGI Assistant - Desktop AI Observer")
        self.window.geometry("800x600")
        
        self.screen_capture = ScreenCapture()
        self.audio_recorder = AudioRecorder()
        self.workflow_analyzer = WorkflowAnalyzer()
        
        self.is_observing = False
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = tk.Label(
            self.window,
            text="🤖 AGI Assistant",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)
        
        # Status frame
        status_frame = ttk.Frame(self.window)
        status_frame.pack(pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="Status: Ready",
            font=("Arial", 12),
            fg="green"
        )
        self.status_label.pack()
        
        # Control buttons
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(pady=20)
        
        self.start_btn = tk.Button(
            btn_frame,
            text="▶ Start Observing",
            command=self.start_observing,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 14),
            padx=20,
            pady=10
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = tk.Button(
            btn_frame,
            text="⏸ Stop Observing",
            command=self.stop_observing,
            bg="#f44336",
            fg="white",
            font=("Arial", 14),
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        self.analyze_btn = tk.Button(
            btn_frame,
            text="🔍 Analyze Workflows",
            command=self.analyze_workflows,
            bg="#2196F3",
            fg="white",
            font=("Arial", 14),
            padx=20,
            pady=10
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=10)
        
        # Log display
        log_label = tk.Label(self.window, text="Activity Log:", font=("Arial", 12))
        log_label.pack(pady=(20, 5))
        
        self.log_display = scrolledtext.ScrolledText(
            self.window,
            height=15,
            width=90,
            font=("Consolas", 10)
        )
        self.log_display.pack(padx=20, pady=10)
        
        # Stats
        self.stats_label = tk.Label(
            self.window,
            text="Screenshots: 0 | Audio Clips: 0 | Workflows: 0",
            font=("Arial", 10)
        )
        self.stats_label.pack(pady=10)
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_display.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_display.see(tk.END)
        
    def start_observing(self):
        self.is_observing = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Observing...", fg="orange")
        
        self.log("🚀 Starting observation mode...")
        self.log("📸 Screen capture initiated")
        self.screen_capture.start()
        
        self.log("🎤 Audio recording initiated")
        self.log("⚙️ Loading Whisper model (this may take a moment)...")
        threading.Thread(target=self.audio_recorder.initialize_whisper, daemon=True).start()
        self.audio_recorder.start()
        
        # Update stats periodically
        self.update_stats()
        
    def stop_observing(self):
        self.is_observing = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Stopped", fg="red")
        
        self.log("⏸ Stopping observation mode...")
        self.screen_capture.stop()
        self.audio_recorder.stop()
        self.log("✅ Observation stopped. Data saved locally.")
        
    def analyze_workflows(self):
        self.log("🔍 Analyzing captured data for workflows...")
        workflows = self.workflow_analyzer.analyze()
        
        if workflows:
            for wf in workflows:
                self.log(f"✨ {wf['description']}")
                self.log(f"   Actions: {', '.join(wf['actions'])}")
        else:
            self.log("ℹ️ No clear workflows detected yet. Keep observing!")
            
    def update_stats(self):
        if self.is_observing:
            screenshots = len(list(Config.SCREENSHOTS_DIR.glob("*.png")))
            audio_files = len(list(Config.AUDIO_DIR.glob("*.wav")))
            workflows = len(list(Config.WORKFLOWS_DIR.glob("*.json")))
            
            self.stats_label.config(
                text=f"Screenshots: {screenshots} | Audio Clips: {audio_files} | Workflows: {workflows}"
            )
            
            self.window.after(2000, self.update_stats)
            
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    print("🤖 Initializing AGI Assistant...")
    app = AGIAssistantGUI()
    app.run()