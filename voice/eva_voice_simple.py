#!/usr/bin/env python3
"""
Claude Voice Simple - Simplified voice interface that works with Python 3.13
"""

import os
import sys
import time
import json
import asyncio
import tempfile
from datetime import datetime
from pathlib import Path

# Basic imports that should work
try:
    import httpx
    import numpy as np
    import sounddevice as sd
    import speech_recognition as sr
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install: pip install httpx numpy sounddevice SpeechRecognition")
    sys.exit(1)

# Try to import pygame for audio playback
try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except:
    HAS_PYGAME = False
    print("Note: pygame not available, audio playback disabled")

# Try to import scipy for wav file writing
try:
    from scipy.io import wavfile
    HAS_SCIPY = True
except:
    HAS_SCIPY = False
    # Fallback to wave module
    try:
        import wave
        HAS_WAVE = True
    except:
        HAS_WAVE = False

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
EVA_SERVER_URL = "http://localhost:8000"

class Colors:
    """Terminal colors"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def print_colored(text, color=Colors.GREEN):
    """Print colored text"""
    print(f"{color}{text}{Colors.RESET}")

class SimpleVoiceClient:
    def __init__(self):
        self.recording = False
        self.audio_data = []
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 200
        self.recognizer.dynamic_energy_threshold = True
        
    def record_audio(self):
        """Record audio until Enter is pressed"""
        self.audio_data = []
        self.recording = True
        
        def callback(indata, frames, time, status):
            if self.recording:
                self.audio_data.append(indata.copy())
        
        with sd.InputStream(callback=callback, channels=CHANNELS, samplerate=SAMPLE_RATE, dtype='int16'):
            print_colored("🎤 Recording... Press ENTER to stop", Colors.YELLOW)
            input()
            self.recording = False
        
        if not self.audio_data:
            return None
            
        return np.concatenate(self.audio_data, axis=0)
    
    def save_audio(self, audio_data):
        """Save audio to file"""
        voice_dir = Path("voice_recordings/claude_recordings")
        voice_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = voice_dir / f"claude_recording_{timestamp}.wav"
        
        if HAS_SCIPY:
            # Use scipy
            wavfile.write(filename, SAMPLE_RATE, audio_data)
        elif HAS_WAVE:
            # Use wave module as fallback
            with wave.open(str(filename), 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio_data.astype(np.int16).tobytes())
        else:
            print_colored("⚠️  Cannot save audio file (no scipy or wave module)", Colors.YELLOW)
            return None
        
        os.chmod(filename, 0o600)
        print_colored(f"🔐 Audio saved to {filename}", Colors.CYAN)
        return str(filename)
    
    def transcribe_audio(self, audio_data):
        """Transcribe audio using SpeechRecognition"""
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Write audio
        if HAS_SCIPY:
            wavfile.write(temp_path, SAMPLE_RATE, audio_data)
        elif HAS_WAVE:
            with wave.open(temp_path, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio_data.astype(np.int16).tobytes())
        else:
            print_colored("❌ Cannot save temp audio for transcription", Colors.RED)
            return None
        
        try:
            print_colored("🔍 Transcribing audio...", Colors.PURPLE)
            
            with sr.AudioFile(temp_path) as source:
                audio = self.recognizer.record(source)
            
            text = self.recognizer.recognize_google(audio, language='en-US')
            print_colored(f"💬 You: {text}", Colors.BLUE)
            return text
            
        except sr.UnknownValueError:
            print_colored("❌ Could not understand audio", Colors.RED)
            return None
        except sr.RequestError as e:
            print_colored(f"❌ Speech recognition error: {e}", Colors.RED)
            return None
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass
    
    async def send_to_eva(self, message):
        """Send message to EVA"""
        print_colored(f"📤 Sending to EVA: {message}", Colors.BLUE)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{EVA_SERVER_URL}/api/chat-simple",
                    json={
                        "message": message,
                        "user_id": "voice_user",
                        "context": "general",
                        "mode": "friend"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    eva_response = data.get("response", "Sorry, I couldn't process that.")
                    print_colored(f"🤖 EVA: {eva_response}", Colors.GREEN)
                    
                    # Try to play audio if available
                    if HAS_PYGAME:
                        await self.play_response(eva_response)
                    
                    return eva_response
                else:
                    print_colored(f"❌ Error: {response.text}", Colors.RED)
                    return None
                    
        except Exception as e:
            print_colored(f"❌ Error: {e}", Colors.RED)
            return None
    
    async def play_response(self, text):
        """Play TTS response"""
        if not HAS_PYGAME:
            return
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{EVA_SERVER_URL}/api/tts",
                    json={"text": text},
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    print_colored("🔊 Playing response...", Colors.PURPLE)
                    
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                        temp_file.write(response.content)
                        temp_path = temp_file.name
                    
                    try:
                        pygame.mixer.music.load(temp_path)
                        pygame.mixer.music.play()
                        
                        while pygame.mixer.music.get_busy():
                            pygame.time.Clock().tick(10)
                    finally:
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                            
        except Exception as e:
            print_colored(f"ℹ️  Audio playback error: {e}", Colors.YELLOW)
    
    async def run(self):
        """Main loop"""
        print_colored("\n🎤 Simple Voice Interface for EVA 🎤", Colors.PURPLE)
        print_colored("Press ENTER to start recording", Colors.YELLOW)
        print_colored("Press ENTER again to stop and send to EVA", Colors.YELLOW)
        print_colored("Press Ctrl+C to exit\n", Colors.YELLOW)
        
        # Test EVA connection
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{EVA_SERVER_URL}/api/info", timeout=5.0)
                if response.status_code == 200:
                    print_colored("✅ Connected to EVA server", Colors.GREEN)
                else:
                    print_colored("⚠️  EVA server not ready", Colors.YELLOW)
        except:
            print_colored("❌ Cannot connect to EVA. Make sure to run: python core/eva.py", Colors.RED)
            return
        
        while True:
            try:
                input("\nPress ENTER to start recording...")
                
                # Record
                audio = self.record_audio()
                if audio is None:
                    continue
                
                # Save
                self.save_audio(audio)
                
                # Transcribe
                text = self.transcribe_audio(audio)
                if text is None:
                    continue
                
                # Send to EVA
                await self.send_to_eva(text)
                
            except KeyboardInterrupt:
                print_colored("\n👋 Goodbye!", Colors.PURPLE)
                break
            except Exception as e:
                print_colored(f"Error: {e}", Colors.RED)

async def main():
    client = SimpleVoiceClient()
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())