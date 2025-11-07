"""Audio recording module using sounddevice for microphone capture."""

import time
import threading
import wave
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable
import sounddevice as sd
from src.config import OBSERVATION_CONFIG
from src.logger import get_logger

logger = get_logger(__name__)


class AudioRecorder:
    """Records audio from microphone in chunks."""
    
    def __init__(self, session_dir: Path, on_audio_clip: Optional[Callable] = None):
        """Initialize audio recorder.
        
        Args:
            session_dir: Directory to save audio clips
            on_audio_clip: Optional callback when audio clip is saved
        """
        self.session_dir = session_dir
        self.audio_dir = session_dir / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        self.on_audio_clip = on_audio_clip
        self.is_recording = False
        self.recording_thread: Optional[threading.Thread] = None
        
        self.config = OBSERVATION_CONFIG["audio"]
        self.sample_rate = self.config["sample_rate"]
        self.channels = self.config["channels"]
        self.chunk_duration = self.config["chunk_duration"]
        self.silence_threshold = self.config["silence_threshold"]
        
        self.audio_clip_count = 0
        self.current_chunk: list = []
        self.chunk_start_time: Optional[float] = None
        
        logger.info(f"Audio recorder initialized for session: {session_dir.name}")
    
    def start(self):
        """Start recording audio."""
        if self.is_recording:
            logger.warning("Audio recording already in progress")
            return
        
        self.is_recording = True
        self.audio_clip_count = 0
        self.current_chunk = []
        self.chunk_start_time = time.time()
        
        self.recording_thread = threading.Thread(target=self._recording_loop, daemon=True)
        self.recording_thread.start()
        logger.info("Audio recording started")
    
    def stop(self):
        """Stop recording audio."""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        # Save final chunk if exists
        if self.current_chunk:
            self._save_chunk()
        
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)
        logger.info(f"Audio recording stopped. Total clips: {self.audio_clip_count}")
    
    def _recording_loop(self):
        """Main recording loop running in separate thread."""
        try:
            def audio_callback(indata, frames, time_info, status):
                """Callback function for audio stream."""
                if status:
                    logger.warning(f"Audio stream status: {status}")
                
                if self.is_recording:
                    # Convert to numpy array and append
                    audio_data = indata.copy()
                    self.current_chunk.append(audio_data)
                    
                    # Check if chunk duration reached
                    elapsed = time.time() - self.chunk_start_time
                    if elapsed >= self.chunk_duration:
                        self._save_chunk()
                        self.current_chunk = []
                        self.chunk_start_time = time.time()
            
            # Start audio stream
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=audio_callback,
                dtype=np.float32
            ):
                while self.is_recording:
                    time.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"Error in audio recording loop: {e}", exc_info=True)
    
    def _save_chunk(self):
        """Save current audio chunk to file."""
        if not self.current_chunk:
            return
        
        try:
            # Concatenate all chunks
            audio_array = np.concatenate(self.current_chunk, axis=0)
            
            # Check for silence
            if self._is_silent(audio_array):
                logger.debug("Skipping silent audio chunk")
                return
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audio_{timestamp}.wav"
            filepath = self.audio_dir / filename
            
            # Convert to int16 for WAV format
            audio_int16 = (audio_array * 32767).astype(np.int16)
            
            # Save as WAV file
            with wave.open(str(filepath), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit = 2 bytes
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_int16.tobytes())
            
            self.audio_clip_count += 1
            
            # Callback if provided
            if self.on_audio_clip:
                try:
                    self.on_audio_clip(filepath, timestamp)
                except Exception as e:
                    logger.error(f"Error in audio clip callback: {e}")
            
            logger.debug(f"Saved audio clip: {filename}")
            
        except Exception as e:
            logger.error(f"Error saving audio chunk: {e}", exc_info=True)
    
    def _is_silent(self, audio_array: np.ndarray) -> bool:
        """Check if audio chunk is silent.
        
        Args:
            audio_array: Audio data array
            
        Returns:
            True if silent, False otherwise
        """
        try:
            # Calculate RMS (Root Mean Square) volume
            rms = np.sqrt(np.mean(audio_array**2))
            return rms < self.silence_threshold
        except Exception as e:
            logger.error(f"Error checking silence: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get recording statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            "audio_clip_count": self.audio_clip_count,
            "is_recording": self.is_recording,
            "audio_dir": str(self.audio_dir)
        }

