#!/usr/bin/env python3
"""
Claude Voice Direct - Fixed version using correct EVA API and SpeechRecognition STT
- Press Enter to start recording
- Press Enter again to stop and send to EVA
- Uses the correct EVA API endpoints and SpeechRecognition for STT
"""

import os
import sys
import time
import json
import httpx
import asyncio
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Check if running in virtual environment
in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
if not in_venv:
    print("Not running in a virtual environment. Please run this script from the EVA virtual environment:")
    print("source venv/bin/activate && python claude_voice_direct_fixed.py")
    sys.exit(1)

# Import required packages
try:
    import sounddevice as sd
    import numpy as np
    import speech_recognition as sr
    import pygame
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Installing required packages...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "sounddevice", "numpy", "pygame"])
        import sounddevice as sd
        import numpy as np
        import speech_recognition as sr
        import pygame
    except Exception as e:
        print(f"Error installing packages: {e}")
        print("\nPlease install the required packages manually:")
        print("source venv/bin/activate")
        print("pip install sounddevice numpy pygame")
        sys.exit(1)

# Import scipy wavfile separately with fallback to avoid aifc issues
try:
    import scipy.io.wavfile as wavfile
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    import wave  # Use standard wave module as fallback

# Load environment variables
load_dotenv()

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
EVA_SERVER_URL = "http://localhost:8000"
USER_ID = "claude_voice_user"
CONTEXT = "general"
MODE = "friend"

# Initialize pygame for audio playback
pygame.mixer.init()

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

class ClaudeVoiceDirectFixed:
    def __init__(self):
        self.recording = False
        self.audio_data = []
        self.recognizer = sr.Recognizer()
        # Adjust recognizer settings for better accuracy
        self.recognizer.energy_threshold = 200  # Lower threshold for quieter audio
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.0  # Slightly longer pause detection
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5
        
    def record_audio(self):
        """Record audio until user presses Enter"""
        self.audio_data = []
        self.recording = True
        
        def callback(indata, frames, time, status):
            if status:
                print(f"Status: {status}")
            if self.recording:
                self.audio_data.append(indata.copy())
        
        # Start the audio stream
        with sd.InputStream(callback=callback, channels=CHANNELS, samplerate=SAMPLE_RATE, dtype='int16'):
            print_colored("🎤 Recording... Press ENTER to stop", Colors.YELLOW)
            input()  # Wait for Enter key
            self.recording = False
            
        if not self.audio_data:
            print_colored("❌ No audio recorded", Colors.RED)
            return None
            
        # Convert to numpy array
        audio = np.concatenate(self.audio_data, axis=0)
        return audio
    
    def save_audio(self, audio, filename=None):
        """Save audio to secure WAV file"""
        # Use secure voice recordings directory
        voice_dir = Path("voice_recordings/eva_recordings")
        voice_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = voice_dir / f"eva_recording_{timestamp}.wav"
        else:
            filename = voice_dir / filename
            
        try:
            if HAS_SCIPY:
                wavfile.write(filename, SAMPLE_RATE, audio)
            else:
                # Use wave module as fallback
                with wave.open(str(filename), 'wb') as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(SAMPLE_RATE)
                    wf.writeframes(audio.astype(np.int16).tobytes())
            
            # Set secure permissions
            os.chmod(filename, 0o600)
            print_colored(f"🔐 Audio saved to {filename}", Colors.CYAN)
            return str(filename)
        except Exception as e:
            print_colored(f"❌ Error saving audio: {e}", Colors.RED)
            return None
    
    def transcribe_audio(self, audio_data):
        """Transcribe audio using SpeechRecognition"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
            
        try:
            # Save audio to temporary file
            if HAS_SCIPY:
                wavfile.write(temp_path, SAMPLE_RATE, audio_data)
            else:
                with wave.open(temp_path, 'wb') as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(2)
                    wf.setframerate(SAMPLE_RATE)
                    wf.writeframes(audio_data.astype(np.int16).tobytes())
            
            print_colored("🔍 Transcribing audio...", Colors.PURPLE)
            
            # Use SpeechRecognition to transcribe
            with sr.AudioFile(temp_path) as source:
                audio = self.recognizer.record(source)
                
            try:
                # Try Google Speech Recognition
                transcription = self.recognizer.recognize_google(audio, language='en-US')
                print_colored(f"💬 You: {transcription}", Colors.BLUE)
                return transcription
            except sr.UnknownValueError:
                print_colored("❌ Could not understand audio", Colors.RED)
                return None
            except sr.RequestError as e:
                print_colored(f"❌ Speech recognition service error: {e}", Colors.RED)
                return None
            
        except Exception as e:
            print_colored(f"❌ Error transcribing audio: {e}", Colors.RED)
            return None
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
    
    async def send_to_eva(self, message):
        """Send message to EVA using the correct API endpoint"""
        print_colored(f"📤 Sending to Claude: {message}", Colors.BLUE)
        
        try:
            # Use the simple chat endpoint that exists in EVA
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
                    
                    # Play response using text-to-speech if available
                    await self.play_response(eva_response)
                    
                    return eva_response
                else:
                    print_colored(f"❌ Error: {response.text}", Colors.RED)
                    return None
                    
        except Exception as e:
            print_colored(f"❌ Error communicating with EVA: {e}", Colors.RED)
            return None
    
    async def play_response(self, text):
        """Play EVA's response using TTS"""
        try:
            # Try EVA's TTS API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{EVA_SERVER_URL}/api/tts",
                    json={"text": text},
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    print_colored("🔊 Playing response...", Colors.PURPLE)
                    
                    # Save audio to temporary file
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                        temp_file.write(response.content)
                        temp_path = temp_file.name
                    
                    try:
                        # Play audio
                        pygame.mixer.music.load(temp_path)
                        pygame.mixer.music.play()
                        
                        # Wait for playback to finish
                        while pygame.mixer.music.get_busy():
                            pygame.time.Clock().tick(10)
                    finally:
                        # Clean up temp file
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                else:
                    print_colored(f"ℹ️ TTS not available: {response.status_code}", Colors.YELLOW)
        except Exception as e:
            print_colored(f"ℹ️ Couldn't play audio response: {str(e)}", Colors.YELLOW)
    
    async def run(self):
        """Run the Claude Voice Direct interface"""
        print_colored("\n🎤 Direct Voice to Claude 🎤", Colors.PURPLE)
        print_colored("Press ENTER to start recording", Colors.YELLOW)
        print_colored("Press ENTER again to stop recording and send to Claude", Colors.YELLOW)
        print_colored("Press Ctrl+C to exit\n", Colors.YELLOW)
        
        # Test EVA connection
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{EVA_SERVER_URL}/api/info", timeout=5.0)
                if response.status_code == 200:
                    print_colored("✅ Connected to EVA server", Colors.GREEN)
                else:
                    print_colored("⚠️  EVA server responded but not ready", Colors.YELLOW)
        except Exception as e:
            print_colored(f"❌ Cannot connect to EVA server: {e}", Colors.RED)
            print_colored("Make sure EVA is running: python eva.py", Colors.YELLOW)
            return
        
        while True:
            try:
                input("Press ENTER to start recording...")
                
                # Record audio
                audio = self.record_audio()
                if audio is None:
                    continue
                
                # Save audio (optional)
                self.save_audio(audio)
                
                # Transcribe audio
                message = self.transcribe_audio(audio)
                if message is None:
                    continue
                
                # Send to EVA
                await self.send_to_eva(message)
                
            except KeyboardInterrupt:
                print_colored("\nExiting Claude Voice Direct", Colors.PURPLE)
                break
            except Exception as e:
                print_colored(f"Error: {str(e)}", Colors.RED)

async def main():
    voice = ClaudeVoiceDirectFixed()
    await voice.run()

if __name__ == "__main__":
    asyncio.run(main())