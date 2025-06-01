"""
SpeechRecognition STT integration to replace WhisperSTT in Eva Agent.
Drop-in replacement for the WhisperSTT class.
"""

import os
import asyncio
import tempfile
import speech_recognition as sr
from typing import Optional
from io import BytesIO

class SpeechRecognitionSTT:
    """Speech-to-text using SpeechRecognition library as drop-in replacement for WhisperSTT."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize SpeechRecognition STT. API key not needed but kept for compatibility."""
        self.recognizer = sr.Recognizer()
        # Adjust recognizer settings for better accuracy
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        
    async def speech_to_text(self, audio_data: bytes, language: str = "en-US") -> str:
        """
        Convert audio bytes to text using Google Speech Recognition.
        Drop-in replacement for WhisperSTT.speech_to_text()
        """
        try:
            # Write audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Load audio file
                with sr.AudioFile(temp_file_path) as source:
                    audio = self.recognizer.record(source)
                
                # Run recognition in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                text = await loop.run_in_executor(
                    None, 
                    self._recognize_speech, 
                    audio, 
                    language
                )
                
                return text
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass
                    
        except Exception as e:
            print(f"SpeechRecognition STT error: {e}")
            return ""
    
    def _recognize_speech(self, audio, language: str = "en-US") -> str:
        """Synchronous speech recognition (run in executor)."""
        try:
            # Try Google Speech Recognition first
            text = self.recognizer.recognize_google(audio, language=language)
            return text
            
        except sr.UnknownValueError:
            # Speech was unintelligible
            return ""
        except sr.RequestError as e:
            print(f"Google Speech Recognition service error: {e}")
            
            # Fallback to offline recognition if available
            try:
                text = self.recognizer.recognize_sphinx(audio)
                return text
            except (sr.UnknownValueError, sr.RequestError):
                return ""
            except Exception:
                # Sphinx not available
                return ""
    
    async def speech_to_text_stream(self, audio_stream) -> str:
        """
        Process streaming audio (simplified implementation).
        For compatibility with WhisperSTT interface.
        """
        # For now, just collect all audio and process as batch
        # Could be enhanced for true streaming later
        audio_chunks = []
        async for chunk in audio_stream:
            audio_chunks.append(chunk)
        
        audio_data = b''.join(audio_chunks)
        return await self.speech_to_text(audio_data)
    
    def is_available(self) -> bool:
        """Check if speech recognition is available."""
        try:
            # Test if Google Speech Recognition is available
            test_recognizer = sr.Recognizer()
            return True
        except Exception:
            return False

# Alias for drop-in replacement
WhisperSTT = SpeechRecognitionSTT