"""
AGI Assistant - Desktop AI that Observes, Learns, and Automates
Enhanced version with better error handling and cross-platform support
"""

import os
import json
import time
import threading
import platform
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import shutil

# Try importing optional dependencies with graceful fallbacks
try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False
    print("⚠️ mss not installed. Screenshot capture disabled.")

try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️ sounddevice/soundfile not installed. Audio capture disabled.")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ Pillow not installed. Image processing disabled.")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    
    # Auto-detect Tesseract installation
    def find_tesseract():
        """Auto-detect Tesseract installation across platforms"""
        # Common paths for different OS
        common_paths = {
            'Windows': [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                Path.home() / 'AppData/Local/Programs/Tesseract-OCR/tesseract.exe',
            ],
            'Darwin': [  # macOS
                '/usr/local/bin/tesseract',
                '/opt/homebrew/bin/tesseract',
            ],
            'Linux': [
                '/usr/bin/tesseract',
                '/usr/local/bin/tesseract',
            ]
        }
        
        system = platform.system()
        paths_to_check = common_paths.get(system, [])
        
        # First try system PATH
        if shutil.which('tesseract'):
            return shutil.which('tesseract')
        
        # Then check common installation paths
        for path in paths_to_check:
            if isinstance(path, str):
                path = Path(path)
            if path.exists():
                return str(path)
        
        return None
    
    tesseract_path = find_tesseract()
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        print(f"✅ Tesseract found at: {tesseract_path}")
    else:
        TESSERACT_AVAILABLE = False
        print("⚠️ Tesseract OCR not found. OCR features disabled.")
        print("   Install from: https://github.com/tesseract-ocr/tesseract")
        
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️ pytesseract not installed. OCR features disabled.")

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️ faster-whisper not installed. Transcription disabled.")


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
    """Captures screenshots at regular intervals with error handling"""
    
    def __init__(self, log_callback=None):
        self.is_recording = False
        self.screenshot_count = 0
        self.log_callback = log_callback
        self.available = MSS_AVAILABLE and PIL_AVAILABLE
        
    def log(self, message):
        """Send log messages to GUI"""
        if self.log_callback:
            self.log_callback(message)
        print(message)
        
    def start(self):
        if not self.available:
            self.log("❌ Screenshot capture not available (missing dependencies)")
            return False
            
        self.is_recording = True
        threading.Thread(target=self._capture_loop, daemon=True).start()
        return True
        
    def stop(self):
        self.is_recording = False
        
    def _capture_loop(self):
        try:
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
                        
                        # Extract text from screenshot using OCR if available
                        if TESSERACT_AVAILABLE:
                            threading.Thread(
                                target=self._extract_ocr, 
                                args=(img, timestamp),
                                daemon=True
                            ).start()
                        
                        time.sleep(Config.SCREENSHOT_INTERVAL)
                        
                    except Exception as e:
                        self.log(f"Screenshot error: {e}")
                        time.sleep(Config.SCREENSHOT_INTERVAL)
                        
        except Exception as e:
            self.log(f"Screenshot system error: {e}")
            self.is_recording = False
            
    def _extract_ocr(self, img, timestamp):
        """Extract text from screenshot (runs in separate thread)"""
        try:
            text = pytesseract.image_to_string(img)
            if text.strip():
                ocr_file = Config.OUTPUT_DIR / f"ocr_{timestamp}.txt"
                with open(ocr_file, 'w', encoding='utf-8') as f:
                    f.write(text)
        except Exception as e:
            self.log(f"OCR error: {e}")


class AudioRecorder:
    """Records audio and transcribes it locally with error handling"""
    
    def __init__(self, log_callback=None):
        self.is_recording = False
        self.whisper_model = None
        self.log_callback = log_callback
        self.available = AUDIO_AVAILABLE
        self.whisper_loaded = False
        
    def log(self, message):
        """Send log messages to GUI"""
        if self.log_callback:
            self.log_callback(message)
        print(message)
        
    def initialize_whisper(self):
        """Load Whisper model for transcription"""
        if not WHISPER_AVAILABLE:
            self.log("⚠️ Whisper not available - transcription disabled")
            return False
            
        try:
            self.log("Loading Whisper model...")
            self.whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
            self.whisper_loaded = True
            self.log("✅ Whisper model loaded!")
            return True
        except Exception as e:
            self.log(f"❌ Failed to load Whisper: {e}")
            return False
        
    def start(self):
        if not self.available:
            self.log("❌ Audio recording not available (missing dependencies)")
            return False
            
        self.is_recording = True
        threading.Thread(target=self._record_loop, daemon=True).start()
        return True
        
    def stop(self):
        self.is_recording = False
        
    def _record_loop(self):
        while self.is_recording:
            try:
                # Check if audio device is available
                devices = sd.query_devices()
                if not devices:
                    self.log("❌ No audio devices found")
                    break
                
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
                
                # Transcribe if Whisper is loaded and there's actual audio
                if self.whisper_loaded and np.max(np.abs(audio_data)) > 0.01:
                    threading.Thread(
                        target=self._transcribe,
                        args=(audio_file, timestamp),
                        daemon=True
                    ).start()
                    
            except Exception as e:
                self.log(f"Audio recording error: {e}")
                time.sleep(Config.AUDIO_CHUNK_DURATION)
                
    def _transcribe(self, audio_file, timestamp):
        """Transcribe audio file"""
        try:
            segments, info = self.whisper_model.transcribe(str(audio_file))
            transcription = " ".join([segment.text for segment in segments])
            
            if transcription.strip():
                text_file = Config.OUTPUT_DIR / f"transcript_{timestamp}.txt"
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(transcription)
                self.log(f"Transcribed: {transcription[:50]}...")
        except Exception as e:
            self.log(f"Transcription error: {e}")


class WorkflowAnalyzer:
    """Analyzes captured data to identify workflows"""
    
    def __init__(self, log_callback=None):
        self.detected_workflows = []
        self.log_callback = log_callback
        
    def log(self, message):
        """Send log messages to GUI"""
        if self.log_callback:
            self.log_callback(message)
        
    def analyze(self):
        """Analyze recent screenshots and transcriptions"""
        workflows = []
        
        try:
            # Get recent OCR texts
            ocr_files = sorted(Config.OUTPUT_DIR.glob("ocr_*.txt"))[-10:]
            ocr_texts = []
            for file in ocr_files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        text = f.read()
                        if text.strip():
                            ocr_texts.append(text)
                except Exception as e:
                    self.log(f"Error reading {file}: {e}")
            
            # Get recent transcriptions
            transcript_files = sorted(Config.OUTPUT_DIR.glob("transcript_*.txt"))[-10:]
            transcripts = []
            for file in transcript_files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        text = f.read()
                        if text.strip():
                            transcripts.append(text)
                except Exception as e:
                    self.log(f"Error reading {file}: {e}")
            
            if not ocr_texts and not transcripts:
                self.log("ℹ️ No data collected yet. Continue observing...")
                return []
            
            # Pattern detection
            workflow = self._detect_patterns(ocr_texts, transcripts)
            
            if workflow:
                workflows.append(workflow)
                self._save_workflow(workflow)
                
        except Exception as e:
            self.log(f"Analysis error: {e}")
            
        return workflows
    
    def _detect_patterns(self, ocr_texts, transcripts):
        """Enhanced pattern detection"""
        combined_text = " ".join(ocr_texts + transcripts).lower()
        
        # Enhanced patterns with more keywords
        patterns = {
            "excel": {
                "keywords": ["excel", "spreadsheet", "cells", "formula", "workbook", "xlsx"],
                "min_matches": 2
            },
            "browser": {
                "keywords": ["chrome", "firefox", "safari", "edge", "browser", "search", "google", "url", "website"],
                "min_matches": 2
            },
            "file_management": {
                "keywords": ["folder", "file", "rename", "move", "copy", "delete", "explorer", "finder"],
                "min_matches": 2
            },
            "email": {
                "keywords": ["email", "outlook", "gmail", "compose", "send", "inbox", "mail"],
                "min_matches": 2
            },
            "document_editing": {
                "keywords": ["word", "document", "edit", "text", "paragraph", "typing"],
                "min_matches": 2
            }
        }
        
        detected = []
        confidence_scores = {}
        
        for category, config in patterns.items():
            matches = sum(1 for keyword in config["keywords"] if keyword in combined_text)
            if matches >= config["min_matches"]:
                detected.append(category)
                confidence_scores[category] = min(matches / len(config["keywords"]), 1.0)
        
        if detected:
            # Calculate overall confidence
            avg_confidence = sum(confidence_scores.values()) / len(confidence_scores)
            confidence = "high" if avg_confidence > 0.6 else "medium" if avg_confidence > 0.3 else "low"
            
            return {
                "timestamp": datetime.now().isoformat(),
                "categories": detected,
                "description": f"Detected workflow: {', '.join(detected)}",
                "actions": self._generate_actions(detected),
                "confidence": confidence,
                "data_points": len(ocr_texts) + len(transcripts)
            }
        return None
    
    def _generate_actions(self, categories):
        """Generate automation actions based on detected patterns"""
        actions = []
        
        action_mapping = {
            "excel": [
                "Open Excel application",
                "Navigate to specific cell",
                "Enter data in cells",
                "Apply formula",
                "Save workbook"
            ],
            "browser": [
                "Open web browser",
                "Navigate to URL",
                "Perform search",
                "Click element",
                "Fill form"
            ],
            "file_management": [
                "Open file explorer",
                "Navigate to folder",
                "Create/rename file",
                "Move/copy files"
            ],
            "email": [
                "Open email client",
                "Compose new email",
                "Add recipients",
                "Send email"
            ],
            "document_editing": [
                "Open document editor",
                "Type content",
                "Format text",
                "Save document"
            ]
        }
        
        for category in categories:
            if category in action_mapping:
                actions.extend(action_mapping[category])
        
        return list(dict.fromkeys(actions))  # Remove duplicates while preserving order
    
    def _save_workflow(self, workflow):
        """Save detected workflow to JSON"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            workflow_file = Config.WORKFLOWS_DIR / f"workflow_{timestamp}.json"
            with open(workflow_file, 'w') as f:
                json.dump(workflow, f, indent=2)
            self.log(f"💾 Workflow saved: {workflow_file.name}")
        except Exception as e:
            self.log(f"Error saving workflow: {e}")


class AGIAssistantGUI:
    """Enhanced GUI with better status indicators and error handling"""
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("AGI Assistant - Desktop AI Observer")
        self.window.geometry("900x700")
        self.window.resizable(True, True)
        
        self.screen_capture = ScreenCapture(log_callback=self.log)
        self.audio_recorder = AudioRecorder(log_callback=self.log)
        self.workflow_analyzer = WorkflowAnalyzer(log_callback=self.log)
        
        self.is_observing = False
        self.setup_ui()
        self.check_dependencies()
        
    def check_dependencies(self):
        """Check and report on available features"""
        self.log("🔍 Checking system capabilities...")
        
        features = []
        if MSS_AVAILABLE and PIL_AVAILABLE:
            features.append("✅ Screenshot capture")
        else:
            features.append("❌ Screenshot capture (missing dependencies)")
            
        if TESSERACT_AVAILABLE:
            features.append("✅ OCR text extraction")
        else:
            features.append("❌ OCR text extraction (install Tesseract)")
            
        if AUDIO_AVAILABLE:
            features.append("✅ Audio recording")
        else:
            features.append("❌ Audio recording (missing sounddevice)")
            
        if WHISPER_AVAILABLE:
            features.append("✅ Speech transcription")
        else:
            features.append("❌ Speech transcription (install faster-whisper)")
        
        self.log("\n".join(features))
        self.log("")
        
    def setup_ui(self):
        # Title
        title = tk.Label(
            self.window,
            text="🤖 AGI Assistant",
            font=("Arial", 24, "bold"),
            fg="#2c3e50"
        )
        title.pack(pady=15)
        
        subtitle = tk.Label(
            self.window,
            text="Privacy-First Desktop AI Observer & Automator",
            font=("Arial", 10),
            fg="#7f8c8d"
        )
        subtitle.pack()
        
        # Status frame with better styling
        status_frame = ttk.LabelFrame(self.window, text="System Status", padding=10)
        status_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.status_label = tk.Label(
            status_frame,
            text="● Ready",
            font=("Arial", 12, "bold"),
            fg="#27ae60"
        )
        self.status_label.pack()
        
        # Feature status
        self.feature_status = tk.Label(
            status_frame,
            text="All systems nominal",
            font=("Arial", 9),
            fg="#7f8c8d"
        )
        self.feature_status.pack()
        
        # Control buttons with improved layout
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(pady=15)
        
        self.start_btn = tk.Button(
            btn_frame,
            text="▶ Start Observing",
            command=self.start_observing,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=25,
            pady=10,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = tk.Button(
            btn_frame,
            text="⏸ Stop Observing",
            command=self.stop_observing,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=25,
            pady=10,
            state=tk.DISABLED,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        self.analyze_btn = tk.Button(
            btn_frame,
            text="🔍 Analyze Workflows",
            command=self.analyze_workflows,
            bg="#3498db",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=25,
            pady=10,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        self.analyze_btn.grid(row=0, column=2, padx=5)
        
        # Clear data button
        self.clear_btn = tk.Button(
            btn_frame,
            text="🗑️ Clear Data",
            command=self.clear_data,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=25,
            pady=10,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        self.clear_btn.grid(row=0, column=3, padx=5)
        
        # Log display with better styling
        log_frame = ttk.LabelFrame(self.window, text="Activity Log", padding=5)
        log_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        self.log_display = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            width=100,
            font=("Consolas", 9),
            bg="#f8f9fa",
            fg="#2c3e50",
            wrap=tk.WORD
        )
        self.log_display.pack(fill=tk.BOTH, expand=True)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(self.window, text="Statistics", padding=10)
        stats_frame.pack(padx=20, pady=10, fill=tk.X)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="Screenshots: 0 | Audio Clips: 0 | Workflows: 0",
            font=("Arial", 10),
            fg="#2c3e50"
        )
        self.stats_label.pack()
        
        # Info label
        info = tk.Label(
            self.window,
            text="ℹ️ All data is stored locally in the 'agi_data' folder | Privacy-First Design",
            font=("Arial", 8),
            fg="#7f8c8d"
        )
        info.pack(pady=5)
        
    def log(self, message):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_display.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_display.see(tk.END)
        self.window.update_idletasks()
        
    def start_observing(self):
        """Start observation with proper error handling"""
        self.is_observing = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="● Observing", fg="#f39c12")
        
        self.log("=" * 80)
        self.log("🚀 Starting observation mode...")
        
        # Start screen capture
        if self.screen_capture.start():
            self.log("📸 Screen capture active")
        else:
            self.log("⚠️ Screen capture unavailable")
        
        # Initialize and start audio
        if self.audio_recorder.available:
            self.log("🎤 Audio recording initiated")
            if WHISPER_AVAILABLE:
                self.log("⚙️ Loading Whisper model (may take a moment)...")
                threading.Thread(
                    target=self.audio_recorder.initialize_whisper,
                    daemon=True
                ).start()
            self.audio_recorder.start()
        else:
            self.log("⚠️ Audio recording unavailable")
        
        self.log("✨ System is now observing your workflows")
        self.log("=" * 80)
        
        # Update stats periodically
        self.update_stats()
        
    def stop_observing(self):
        """Stop observation with cleanup"""
        self.is_observing = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="● Stopped", fg="#e74c3c")
        
        self.log("=" * 80)
        self.log("⏸ Stopping observation mode...")
        self.screen_capture.stop()
        self.audio_recorder.stop()
        self.log("💾 All data saved locally in 'agi_data' folder")
        self.log("✅ Observation stopped successfully")
        self.log("=" * 80)
        
    def analyze_workflows(self):
        """Analyze workflows with progress indication"""
        self.log("=" * 80)
        self.log("🔍 Analyzing captured data for workflow patterns...")
        self.analyze_btn.config(state=tk.DISABLED)
        
        def analyze_thread():
            try:
                workflows = self.workflow_analyzer.analyze()
                
                if workflows:
                    self.log(f"\n✨ Found {len(workflows)} workflow(s):\n")
                    for wf in workflows:
                        self.log(f"📋 {wf['description']}")
                        self.log(f"   Confidence: {wf['confidence'].upper()}")
                        self.log(f"   Data points: {wf.get('data_points', 0)}")
                        self.log(f"   Categories: {', '.join(wf['categories'])}")
                        self.log(f"\n   Suggested Actions:")
                        for action in wf['actions'][:5]:  # Show first 5
                            self.log(f"     • {action}")
                        if len(wf['actions']) > 5:
                            self.log(f"     ... and {len(wf['actions']) - 5} more")
                        self.log("")
                else:
                    self.log("ℹ️ No clear workflows detected yet.")
                    self.log("   💡 Tip: Continue observing and perform repetitive tasks")
                    
            except Exception as e:
                self.log(f"❌ Analysis error: {e}")
            finally:
                self.analyze_btn.config(state=tk.NORMAL)
                self.log("=" * 80)
        
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    def clear_data(self):
        """Clear all collected data"""
        response = messagebox.askyesno(
            "Clear Data",
            "This will delete all screenshots, audio files, and detected workflows.\n\n"
            "Are you sure you want to continue?"
        )
        
        if response:
            try:
                # Clear directories
                for dir_path in [Config.SCREENSHOTS_DIR, Config.AUDIO_DIR, Config.WORKFLOWS_DIR]:
                    for file in dir_path.glob("*"):
                        file.unlink()
                
                # Clear OCR and transcript files
                for file in Config.OUTPUT_DIR.glob("ocr_*.txt"):
                    file.unlink()
                for file in Config.OUTPUT_DIR.glob("transcript_*.txt"):
                    file.unlink()
                
                self.log("🗑️ All data cleared successfully")
                self.update_stats()
                messagebox.showinfo("Success", "All data has been cleared")
                
            except Exception as e:
                self.log(f"❌ Error clearing data: {e}")
                messagebox.showerror("Error", f"Failed to clear data: {e}")
            
    def update_stats(self):
        """Update statistics display"""
        if self.is_observing or True:  # Always update
            try:
                screenshots = len(list(Config.SCREENSHOTS_DIR.glob("*.png")))
                audio_files = len(list(Config.AUDIO_DIR.glob("*.wav")))
                workflows = len(list(Config.WORKFLOWS_DIR.glob("*.json")))
                
                self.stats_label.config(
                    text=f"Screenshots: {screenshots} | Audio Clips: {audio_files} | Workflows: {workflows}"
                )
            except Exception as e:
                self.log(f"Stats update error: {e}")
            
            if self.is_observing:
                self.window.after(2000, self.update_stats)
            
    def run(self):
        """Run the application"""
        self.log("🤖 AGI Assistant initialized and ready")
        self.log("📁 Data will be saved to: " + str(Config.OUTPUT_DIR.absolute()))
        self.log("")
        self.window.mainloop()


if __name__ == "__main__":
    print("=" * 80)
    print("🤖 AGI Assistant - Desktop AI Observer & Automator")
    print("=" * 80)
    app = AGIAssistantGUI()
    app.run()
