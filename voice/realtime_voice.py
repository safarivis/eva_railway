"""
Real-time voice streaming infrastructure for EVA Agent
Combines WebSocket communication with voice processing
"""

import asyncio
import json
import base64
import io
import numpy as np
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import logging
from fastapi import WebSocket, WebSocketDisconnect
import webrtcvad
import audioop
from collections import deque

logger = logging.getLogger(__name__)

class VoiceActivityDetector:
    """Voice Activity Detection using WebRTC VAD"""
    
    def __init__(self, aggressiveness: int = 2, sample_rate: int = 16000, frame_duration: int = 30):
        """
        Initialize VAD
        
        Args:
            aggressiveness: 0-3, higher = more aggressive filtering
            sample_rate: Audio sample rate (8000, 16000, 32000, 48000)
            frame_duration: Frame duration in ms (10, 20, 30)
        """
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration
        self.frame_length = int(sample_rate * frame_duration / 1000)
        self.buffer = deque(maxlen=50)  # Rolling buffer for speech detection
        
    def is_speech(self, audio_chunk: bytes) -> bool:
        """Check if audio chunk contains speech"""
        try:
            # Ensure we have the right frame size
            if len(audio_chunk) != self.frame_length * 2:  # 2 bytes per 16-bit sample
                return False
                
            # Check if this frame contains speech
            is_speech = self.vad.is_speech(audio_chunk, self.sample_rate)
            
            # Add to rolling buffer
            self.buffer.append(is_speech)
            
            # Consider it speech if recent frames show speech activity
            recent_speech = sum(self.buffer)
            return recent_speech > len(self.buffer) * 0.3  # 30% threshold
            
        except Exception as e:
            logger.error(f"VAD error: {e}")
            return False

class AudioBuffer:
    """Manages audio buffering and streaming"""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.buffer = io.BytesIO()
        self.speech_buffer = io.BytesIO()
        self.is_recording = False
        self.silence_frames = 0
        self.max_silence_frames = 30  # ~1 second at 30ms frames
        
    def add_audio(self, audio_data: bytes, is_speech: bool):
        """Add audio data to buffer"""
        self.buffer.write(audio_data)
        
        if is_speech:
            self.silence_frames = 0
            if not self.is_recording:
                self.is_recording = True
                self.speech_buffer = io.BytesIO()
                logger.info("Speech detected - started recording")
            
            self.speech_buffer.write(audio_data)
        else:
            if self.is_recording:
                self.silence_frames += 1
                self.speech_buffer.write(audio_data)  # Include some silence
                
                if self.silence_frames >= self.max_silence_frames:
                    # End of speech detected
                    logger.info("End of speech detected")
                    return self.get_speech_audio()
        
        return None
    
    def get_speech_audio(self) -> Optional[bytes]:
        """Get recorded speech audio"""
        if self.speech_buffer.tell() > 0:
            audio = self.speech_buffer.getvalue()
            self.reset_speech_buffer()
            return audio
        return None
    
    def reset_speech_buffer(self):
        """Reset speech recording"""
        self.is_recording = False
        self.silence_frames = 0
        self.speech_buffer = io.BytesIO()

class RealTimeVoiceManager:
    """Manages real-time voice connections and processing"""
    
    def __init__(self, stt_handler, tts_handler):
        self.stt_handler = stt_handler
        self.tts_handler = tts_handler
        self.active_connections: Dict[str, WebSocket] = {}
        self.voice_sessions: Dict[str, Dict[str, Any]] = {}
        
    async def connect_voice_session(self, websocket: WebSocket, session_id: str, 
                                  user_id: str, context: str, mode: str):
        """Initialize a new voice session"""
        await websocket.accept()
        
        self.active_connections[session_id] = websocket
        self.voice_sessions[session_id] = {
            "user_id": user_id,
            "context": context,
            "mode": mode,
            "vad": VoiceActivityDetector(),
            "audio_buffer": AudioBuffer(),
            "is_speaking": False,
            "conversation_active": False,
            "last_activity": datetime.now()
        }
        
        logger.info(f"Voice session {session_id} connected for user {user_id}")
        
        await self.send_voice_event(session_id, "voice_session_connected", {
            "session_id": session_id,
            "status": "connected"
        })
    
    async def disconnect_voice_session(self, session_id: str):
        """Clean up voice session"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.voice_sessions:
            del self.voice_sessions[session_id]
        logger.info(f"Voice session {session_id} disconnected")
    
    async def send_voice_event(self, session_id: str, event_type: str, data: Dict[str, Any]):
        """Send event to voice session"""
        if session_id not in self.active_connections:
            return
            
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            await self.active_connections[session_id].send_text(json.dumps(event))
        except Exception as e:
            logger.error(f"Error sending voice event: {e}")
            await self.disconnect_voice_session(session_id)
    
    async def process_audio_chunk(self, session_id: str, audio_data: bytes):
        """Process incoming audio chunk"""
        if session_id not in self.voice_sessions:
            return
            
        session = self.voice_sessions[session_id]
        vad = session["vad"]
        audio_buffer = session["audio_buffer"]
        
        # Update last activity
        session["last_activity"] = datetime.now()
        
        # Check for speech
        is_speech = vad.is_speech(audio_data)
        
        # Add to buffer and check for complete utterance
        complete_audio = audio_buffer.add_audio(audio_data, is_speech)
        
        if complete_audio:
            # Speech utterance complete - process it
            await self.process_speech_utterance(session_id, complete_audio)
    
    async def process_speech_utterance(self, session_id: str, audio_data: bytes):
        """Process a complete speech utterance"""
        if session_id not in self.voice_sessions:
            return
            
        session = self.voice_sessions[session_id]
        
        try:
            # Send status update
            await self.send_voice_event(session_id, "speech_processing", {
                "status": "transcribing"
            })
            
            # Convert speech to text
            text = await self.stt_handler.speech_to_text(audio_data)
            
            if text.strip():
                await self.send_voice_event(session_id, "speech_transcribed", {
                    "text": text
                })
                
                # Process the text through EVA's conversation system
                await self.process_conversation_turn(session_id, text)
            
        except Exception as e:
            logger.error(f"Error processing speech: {e}")
            await self.send_voice_event(session_id, "error", {
                "message": f"Speech processing error: {str(e)}"
            })
    
    async def process_conversation_turn(self, session_id: str, user_text: str):
        """Process a conversation turn with EVA"""
        if session_id not in self.voice_sessions:
            return
            
        session = self.voice_sessions[session_id]
        
        try:
            # This will integrate with EVA's existing conversation system
            # For now, we'll create a placeholder response
            
            await self.send_voice_event(session_id, "eva_thinking", {
                "status": "processing"
            })
            
            # TODO: Integrate with EVA's conversation system
            # This should call the same logic as the regular chat endpoint
            # but return streaming response
            
            # Placeholder response
            response_text = f"I heard you say: {user_text}"
            
            await self.send_voice_event(session_id, "eva_response", {
                "text": response_text
            })
            
            # Generate TTS
            await self.generate_voice_response(session_id, response_text)
            
        except Exception as e:
            logger.error(f"Error in conversation turn: {e}")
            await self.send_voice_event(session_id, "error", {
                "message": f"Conversation error: {str(e)}"
            })
    
    async def generate_voice_response(self, session_id: str, text: str):
        """Generate and stream TTS response"""
        if session_id not in self.voice_sessions:
            return
            
        try:
            await self.send_voice_event(session_id, "tts_generating", {
                "status": "generating"
            })
            
            # Generate TTS audio
            audio_data = await self.tts_handler.text_to_speech(text)
            
            # Encode audio as base64 for WebSocket transmission
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            await self.send_voice_event(session_id, "voice_response", {
                "audio": audio_base64,
                "format": "mp3"
            })
            
        except Exception as e:
            logger.error(f"Error generating voice response: {e}")
            await self.send_voice_event(session_id, "error", {
                "message": f"TTS error: {str(e)}"
            })
    
    async def handle_websocket_message(self, session_id: str, message: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "audio_chunk":
                # Decode base64 audio data
                audio_data = base64.b64decode(data["audio"])
                await self.process_audio_chunk(session_id, audio_data)
                
            elif message_type == "start_conversation":
                session = self.voice_sessions.get(session_id)
                if session:
                    session["conversation_active"] = True
                    await self.send_voice_event(session_id, "conversation_started", {
                        "status": "listening"
                    })
                    
            elif message_type == "stop_conversation":
                session = self.voice_sessions.get(session_id)
                if session:
                    session["conversation_active"] = False
                    await self.send_voice_event(session_id, "conversation_stopped", {
                        "status": "idle"
                    })
                    
            elif message_type == "interrupt":
                # Handle interruption - stop current TTS/processing
                await self.handle_interruption(session_id)
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self.send_voice_event(session_id, "error", {
                "message": f"Message handling error: {str(e)}"
            })
    
    async def handle_interruption(self, session_id: str):
        """Handle user interruption"""
        if session_id not in self.voice_sessions:
            return
            
        # Stop any ongoing TTS or processing
        # Reset audio buffer
        session = self.voice_sessions[session_id]
        session["audio_buffer"].reset_speech_buffer()
        
        await self.send_voice_event(session_id, "interrupted", {
            "status": "ready"
        })

# Global voice manager instance
voice_manager = None

def get_voice_manager(stt_handler, tts_handler):
    """Get or create voice manager instance"""
    global voice_manager
    if voice_manager is None:
        voice_manager = RealTimeVoiceManager(stt_handler, tts_handler)
    return voice_manager