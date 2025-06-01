#!/usr/bin/env python3
"""
EVA Voice Working - Voice interface that definitely works with Python 3.13
Avoids all problematic imports and uses only basic modules
"""

import os
import sys
import time
import json
import httpx
import asyncio
import tempfile
import uuid
import wave
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Check if running in virtual environment
in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
if not in_venv:
    print("Not running in a virtual environment. Please run this script from the EVA virtual environment:")
    print("source venv/bin/activate && python eva_voice_working.py")
    sys.exit(1)

# Import only what we absolutely need - no scipy!
try:
    import sounddevice as sd
    import numpy as np
    import speech_recognition as sr
    print("✅ Core imports successful")
except ImportError as e:
    print(f"❌ Missing package: {e}")
    print("Please install: pip install sounddevice numpy SpeechRecognition")
    sys.exit(1)

# Try pygame for audio playback (optional)
try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
    print("✅ Pygame available for audio playback")
except:
    HAS_PYGAME = False
    print("⚠️  Pygame not available - no audio playback")

load_dotenv()

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
EVA_SERVER_URL = "http://localhost:8000"
USER_ID = "voice_user"
CONTEXT = "general"
MODE = "friend"

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def print_colored(text, color=Colors.GREEN):
    print(f"{color}{text}{Colors.RESET}")

class EVAVoiceWorking:
    def __init__(self):
        self.recording = False
        self.audio_data = []
        self.recognizer = sr.Recognizer()
        # Optimized settings
        self.recognizer.energy_threshold = 200
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.0
        
    def record_audio(self):
        """Record audio until user presses Enter"""
        self.audio_data = []
        self.recording = True
        
        def callback(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}")
            if self.recording:
                self.audio_data.append(indata.copy())
        
        with sd.InputStream(callback=callback, channels=CHANNELS, samplerate=SAMPLE_RATE, dtype='int16'):
            print_colored("🎤 Recording... Press ENTER to stop", Colors.YELLOW)
            input()
            self.recording = False
            
        if not self.audio_data:
            print_colored("❌ No audio recorded", Colors.RED)
            return None
            
        return np.concatenate(self.audio_data, axis=0)
    
    def save_audio(self, audio_data):
        """Save audio using standard wave module"""
        voice_dir = Path("voice_recordings/eva_recordings")
        voice_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = voice_dir / f"eva_recording_{timestamp}.wav"
        
        try:
            with wave.open(str(filename), 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio_data.astype(np.int16).tobytes())
            
            os.chmod(filename, 0o600)
            print_colored(f"🔐 Audio saved to {filename}", Colors.CYAN)
            return str(filename)
        except Exception as e:
            print_colored(f"❌ Error saving audio: {e}", Colors.RED)
            return None
    
    def transcribe_audio(self, audio_data):
        """Transcribe audio using SpeechRecognition"""
        temp_path = None
        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Write audio using wave module
            with wave.open(temp_path, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio_data.astype(np.int16).tobytes())
            
            print_colored("🔍 Transcribing audio...", Colors.PURPLE)
            
            # Transcribe using SpeechRecognition
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
        except Exception as e:
            print_colored(f"❌ Transcription error: {e}", Colors.RED)
            return None
        finally:
            # Clean up
            if temp_path and os.path.exists(temp_path):
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
                        "user_id": USER_ID,
                        "context": CONTEXT,
                        "mode": MODE
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    eva_response = data.get("response", "Sorry, I couldn't process that.")
                    print_colored(f"🤖 EVA: {eva_response}", Colors.GREEN)
                    
                    # Try TTS if available
                    if HAS_PYGAME:
                        await self.play_response(eva_response)
                    
                    return eva_response
                else:
                    print_colored(f"❌ Error: {response.status_code} - {response.text}", Colors.RED)
                    return None
                    
        except Exception as e:
            print_colored(f"❌ Error communicating with EVA: {e}", Colors.RED)
            return None
    
    async def play_response(self, text):
        """Play TTS response if available"""
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
            print_colored(f"ℹ️  TTS error: {e}", Colors.YELLOW)
    
    async def run(self):
        """Main voice chat loop"""
        print_colored("\n🎤 EVA Voice Chat (Python 3.13 Compatible) 🎤", Colors.PURPLE)
        print_colored("Press ENTER to start recording", Colors.YELLOW)
        print_colored("Press ENTER again to stop and send to EVA", Colors.YELLOW)
        print_colored("Press Ctrl+C to exit\n", Colors.YELLOW)
        
        # Test EVA connection
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{EVA_SERVER_URL}/api/info", timeout=5.0)
                if response.status_code == 200:
                    info = response.json()
                    print_colored(f"✅ Connected to EVA v{info['version']}", Colors.GREEN)
                    print_colored(f"   Model: {info['model']}", Colors.CYAN)
                    print_colored(f"   Context: {CONTEXT}, Mode: {MODE}\n", Colors.CYAN)
                else:
                    print_colored("⚠️  EVA server not ready", Colors.YELLOW)
        except:
            print_colored("❌ Cannot connect to EVA server!", Colors.RED)
            print_colored("Please start EVA first: python core/eva.py", Colors.YELLOW)
            return
        
        while True:
            try:
                input("Press ENTER to start recording...")
                
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
                print_colored("\n👋 Goodbye from EVA!", Colors.PURPLE)
                break
            except Exception as e:
                print_colored(f"Error: {e}", Colors.RED)

async def main():
    eva_voice = EVAVoiceWorking()
    await eva_voice.run()

if __name__ == "__main__":
    asyncio.run(main())