"""
ElevenLabs integration for TTS and STT in Eva Agent.
"""

import os
import asyncio
import httpx
import base64
import json
from typing import Optional, Dict, Any, AsyncGenerator
from io import BytesIO

class ElevenLabsIntegration:
    """Handle TTS and STT using ElevenLabs API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        # Default voice ID - using your preferred voice
        self.default_voice_id = "L4so9SudEsIYzE9j4qlR"  # Your chosen voice
        self.model_id = "eleven_turbo_v2_5"  # Latest turbo model for better quality
        
    async def text_to_speech(
        self, 
        text: str, 
        voice_id: Optional[str] = None,
        model_id: Optional[str] = None,
        stream: bool = False
    ) -> bytes:
        """Convert text to speech using ElevenLabs API."""
        voice_id = voice_id or self.default_voice_id
        model_id = model_id or self.model_id
        
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        if stream:
            url += "/stream"
        
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.75,        # Higher stability for consistent voice
                "similarity_boost": 0.8,  # Higher similarity for natural sound
                "style": 0.4,            # Some style for personality
                "use_speaker_boost": True
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"ElevenLabs TTS error: {response.status_code} - {response.text}")
            
            return response.content
    
    async def text_to_speech_stream(
        self, 
        text: str, 
        voice_id: Optional[str] = None,
        model_id: Optional[str] = None
    ) -> AsyncGenerator[bytes, None]:
        """Stream text to speech using ElevenLabs API."""
        voice_id = voice_id or self.default_voice_id
        model_id = model_id or self.model_id
        
        url = f"{self.base_url}/text-to-speech/{voice_id}/stream"
        
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.75,        # Higher stability for consistent voice
                "similarity_boost": 0.8,  # Higher similarity for natural sound
                "style": 0.4,            # Some style for personality
                "use_speaker_boost": True
            },
            "optimize_streaming_latency": 2
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                url,
                json=payload,
                headers=self.headers,
                timeout=30.0
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise Exception(f"ElevenLabs TTS stream error: {response.status_code} - {error_text}")
                
                async for chunk in response.aiter_bytes():
                    if chunk:
                        yield chunk
    
    async def speech_to_text(self, audio_data: bytes, language_code: Optional[str] = "en") -> str:
        """Convert speech to text using ElevenLabs API."""
        # Note: As of my knowledge, ElevenLabs primarily focuses on TTS
        # For STT, we'll use their audio isolation endpoint as a preprocessing step
        # and potentially integrate with another service or use a placeholder
        
        # ElevenLabs doesn't have a direct STT API yet
        # This is a placeholder that returns a message indicating this
        # In a real implementation, you might want to use another service like:
        # - OpenAI Whisper API
        # - Google Speech-to-Text
        # - Azure Speech Services
        
        # For now, we'll create a mock response
        return "ElevenLabs STT is not yet available. Consider using OpenAI Whisper or Google Speech-to-Text for STT functionality."
    
    async def get_voices(self) -> Dict[str, Any]:
        """Get available voices from ElevenLabs."""
        url = f"{self.base_url}/voices"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self.headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise Exception(f"ElevenLabs get voices error: {response.status_code} - {response.text}")
            
            return response.json()
    
    async def get_models(self) -> Dict[str, Any]:
        """Get available models from ElevenLabs."""
        url = f"{self.base_url}/models"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self.headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise Exception(f"ElevenLabs get models error: {response.status_code} - {response.text}")
            
            return response.json()
    
    def audio_to_base64(self, audio_data: bytes) -> str:
        """Convert audio bytes to base64 string."""
        return base64.b64encode(audio_data).decode('utf-8')
    
    def base64_to_audio(self, base64_string: str) -> bytes:
        """Convert base64 string to audio bytes."""
        return base64.b64decode(base64_string)


# For actual STT, we can create a separate class that uses OpenAI Whisper
class WhisperSTT:
    """Speech to Text using OpenAI Whisper API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/audio"
        
    async def speech_to_text(
        self, 
        audio_data: bytes, 
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "text"
    ) -> str:
        """Convert speech to text using OpenAI Whisper."""
        url = f"{self.base_url}/transcriptions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Create form data
        files = {
            "file": ("audio.webm", audio_data, "audio/webm")
        }
        
        data = {
            "model": "whisper-1",
            "response_format": response_format
        }
        
        if language:
            data["language"] = language
            
        if prompt:
            data["prompt"] = prompt
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                files=files,
                data=data,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Whisper STT error: {response.status_code} - {response.text}")
            
            if response_format == "text":
                return response.text
            else:
                return response.json()