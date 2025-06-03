#!/usr/bin/env python3
"""
Local STT Handler using faster-whisper
Provides offline speech-to-text without API calls
"""
import io
import os
import tempfile
import logging
from typing import Optional
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

class LocalSTTHandler:
    """Local Speech-to-Text using faster-whisper"""
    
    def __init__(self, model_size: str = "tiny"):
        """
        Initialize local STT
        
        Args:
            model_size: tiny, base, small, medium, large-v3
                       tiny = 39MB, fastest
                       base = 74MB, good balance  
                       small = 244MB, better accuracy
        """
        self.model_size = model_size
        self.model = None
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize the Whisper model"""
        try:
            if self.is_initialized and self.model is not None:
                return True
                
            logger.info(f"Loading Whisper {self.model_size} model...")
            
            # Check if model files exist
            import os
            model_path = os.path.expanduser(f"~/.cache/huggingface/hub/models--Systran--faster-whisper-{self.model_size}")
            if not os.path.exists(model_path):
                logger.info(f"Model will be downloaded on first use: {self.model_size}")
            
            self.model = WhisperModel(
                self.model_size, 
                device="cpu", 
                compute_type="int8"
            )
            
            # Test the model with a simple check
            if self.model is None:
                raise Exception("Model failed to load")
            
            self.is_initialized = True
            logger.info("✅ Local STT initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize local STT: {e}")
            self.is_initialized = False
            self.model = None
            return False
    
    def transcribe_audio(self, audio_data: bytes, language: str = "en") -> Optional[str]:
        """
        Transcribe audio bytes to text
        
        Args:
            audio_data: Audio file bytes (wav, mp3, m4a, etc.)
            language: Language code (en, es, fr, etc.)
            
        Returns:
            Transcribed text or None if failed
        """
        if not self.is_initialized:
            if not self.initialize():
                return None
                
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            try:
                # Transcribe
                segments, info = self.model.transcribe(
                    temp_path, 
                    language=language,
                    vad_filter=True,  # Voice activity detection
                    vad_parameters=dict(min_silence_duration_ms=500)
                )
                
                # Combine segments
                text = " ".join([segment.text for segment in segments]).strip()
                
                # Handle empty transcriptions
                if not text or text == "..." or len(text) < 2:
                    logger.warning("Empty or minimal transcription detected")
                    return None
                
                logger.info(f"🎤 Transcribed: {text[:100]}...")
                return text
                
            finally:
                # Clean up temp file
                os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            return None
    
    def transcribe_file(self, file_path: str, language: str = "en") -> Optional[str]:
        """
        Transcribe audio file to text
        
        Args:
            file_path: Path to audio file
            language: Language code
            
        Returns:
            Transcribed text or None if failed
        """
        if not self.is_initialized:
            if not self.initialize():
                return None
                
        try:
            segments, info = self.model.transcribe(
                file_path, 
                language=language,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            text = " ".join([segment.text for segment in segments]).strip()
            logger.info(f"🎤 Transcribed file: {text[:100]}...")
            return text
            
        except Exception as e:
            logger.error(f"❌ File transcription failed: {e}")
            return None

# Global instance
local_stt = LocalSTTHandler()

def get_local_stt() -> LocalSTTHandler:
    """Get the global local STT instance"""
    return local_stt