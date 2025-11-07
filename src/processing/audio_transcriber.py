"""Audio transcription using faster-whisper for offline speech-to-text."""

from pathlib import Path
from typing import List, Optional
from faster_whisper import WhisperModel
from src.config import PROCESSING_CONFIG
from src.logger import get_logger

logger = get_logger(__name__)


class AudioTranscriber:
    """Transcribes audio files to text using faster-whisper."""
    
    def __init__(self):
        """Initialize audio transcriber."""
        self.config = PROCESSING_CONFIG["whisper"]
        self.model_size = self.config["model_size"]
        self.device = self.config["device"]
        self.compute_type = self.config["compute_type"]
        
        # Initialize model (lazy loading)
        self.model: Optional[WhisperModel] = None
        logger.info("Audio transcriber initialized")
    
    def _get_model(self) -> WhisperModel:
        """Get or initialize Whisper model.
        
        Returns:
            WhisperModel instance
        """
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_size}")
            try:
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type
                )
                logger.info("Whisper model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading Whisper model: {e}", exc_info=True)
                raise
        
        return self.model
    
    def transcribe_file(self, audio_file: Path) -> str:
        """Transcribe a single audio file.
        
        Args:
            audio_file: Path to audio file (WAV format)
            
        Returns:
            Transcribed text string
        """
        if not audio_file.exists():
            logger.error(f"Audio file not found: {audio_file}")
            return ""
        
        try:
            model = self._get_model()
            logger.info(f"Transcribing: {audio_file.name}")
            
            # Transcribe audio
            segments, info = model.transcribe(
                str(audio_file),
                beam_size=5,
                language="en"
            )
            
            # Combine all segments
            transcript_parts = []
            for segment in segments:
                transcript_parts.append(segment.text.strip())
            
            transcript = " ".join(transcript_parts)
            logger.info(f"Transcription complete: {len(transcript)} characters")
            
            return transcript
            
        except Exception as e:
            logger.error(f"Error transcribing audio file {audio_file}: {e}", exc_info=True)
            return ""
    
    def transcribe_session(self, session_dir: Path) -> str:
        """Transcribe all audio files in a session directory.
        
        Args:
            session_dir: Path to session directory
            
        Returns:
            Combined transcript text
        """
        audio_dir = session_dir / "audio"
        if not audio_dir.exists():
            logger.warning(f"Audio directory not found: {audio_dir}")
            return ""
        
        # Find all audio files
        audio_files = sorted(audio_dir.glob("*.wav"))
        
        if not audio_files:
            logger.info("No audio files found in session")
            return ""
        
        logger.info(f"Transcribing {len(audio_files)} audio files")
        
        # Transcribe each file
        transcripts = []
        for audio_file in audio_files:
            transcript = self.transcribe_file(audio_file)
            if transcript:
                transcripts.append(transcript)
        
        # Combine all transcripts
        full_transcript = " ".join(transcripts)
        
        # Save transcript to file
        transcript_file = session_dir / "transcript.txt"
        try:
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(full_transcript)
            logger.info(f"Saved transcript to: {transcript_file}")
        except Exception as e:
            logger.error(f"Error saving transcript: {e}")
        
        return full_transcript
    
    def transcribe_batch(self, audio_files: List[Path]) -> List[str]:
        """Transcribe multiple audio files.
        
        Args:
            audio_files: List of audio file paths
            
        Returns:
            List of transcript strings
        """
        transcripts = []
        for audio_file in audio_files:
            transcript = self.transcribe_file(audio_file)
            transcripts.append(transcript)
        
        return transcripts

