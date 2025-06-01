#!/usr/bin/env python3
"""
Simple Voice Client for EVA - No SpeechRecognition dependency
Uses direct API calls to EVA server for STT and TTS
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

# Import only what we absolutely need - no SpeechRecognition!
try:
    import sounddevice as sd
    import numpy as np
except ImportError as e:
    print(f"❌ Missing package: {e}")
    print("Please install: pip install sounddevice numpy")
    sys.exit(1)

# Try to import pygame for audio playback
try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except:
    HAS_PYGAME = False
    print("⚠️ Pygame not available, TTS playback disabled")

# Constants
API_URL = "http://localhost:8000"
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = 'int16'
MAX_SECONDS = 60
USER_ID = "lu"
CONTEXT = "personal"
MODE = "friend"

# Terminal colors
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

class SimpleVoiceClient:
    def __init__(self):
        self.recording = False
        self.audio_data = []
        
        # Create voice recordings directory if it doesn't exist
        self.recordings_dir = Path("voice_recordings")
        self.recordings_dir.mkdir(exist_ok=True)
        
        # Check EVA server connection
        try:
            response = httpx.get(f"{API_URL}/api/info")
            if response.status_code == 200:
                info = response.json()
                print_colored(f"✅ Connected to EVA v{info.get('version', '0.1.0')}")
                print_colored(f"Model: {info.get('model', 'unknown')}")
            else:
                print_colored(f"❌ Error connecting to EVA server: {response.status_code}", Colors.RED)
        except Exception as e:
            print_colored(f"❌ Error connecting to EVA server: {e}", Colors.RED)
            sys.exit(1)
    
    def record_audio(self):
        """Record audio until Enter is pressed"""
        print_colored("🎤 Recording... Press ENTER to stop", Colors.YELLOW)
        self.recording = True
        self.audio_data = []
        
        # Start recording
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE, 
                           callback=self.callback):
            # Wait for Enter key to stop recording
            input()
        
        self.recording = False
        
        # Convert to numpy array
        if len(self.audio_data) > 0:
            return np.concatenate(self.audio_data)
        return None
    
    def callback(self, indata, frames, time, status):
        """Callback for sounddevice"""
        if status:
            print(f"⚠️ {status}")
        if self.recording:
            self.audio_data.append(indata.copy())
    
    def save_audio(self, audio_data):
        """Save audio to WAV file"""
        if audio_data is None or len(audio_data) == 0:
            return None
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.recordings_dir / f"voice_clip_{timestamp}.wav"
        
        # Save as WAV file
        with wave.open(str(filename), 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data.tobytes())
        
        print_colored(f"✅ Audio saved to {filename}")
        return filename
    
    async def transcribe_audio(self, audio_file):
        """Transcribe audio using EVA's STT API"""
        if audio_file is None:
            return None
        
        print_colored("🔍 Transcribing audio using EVA's STT API...", Colors.BLUE)
        
        try:
            # Use EVA's STT API
            files = {'file': open(audio_file, 'rb')}
            response = httpx.post(f"{API_URL}/api/stt", files=files)
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get('text', '')
                if transcript:
                    print_colored(f"💬 Transcription: {transcript}")
                    return transcript
                else:
                    print_colored("❌ No transcription available", Colors.RED)
                    return None
            else:
                print_colored(f"❌ Error: {response.status_code} - {response.text}", Colors.RED)
                return None
        except Exception as e:
            print_colored(f"❌ Error: {e}", Colors.RED)
            return None
    
    async def send_to_eva(self, message):
        """Send message to EVA using the proper API endpoints"""
        if not message:
            return None
        
        print_colored("🤖 Sending to EVA...", Colors.BLUE)
        
        try:
            # Create a new run
            run_data = {
                "user_id": USER_ID,
                "context": CONTEXT,
                "mode": MODE,
                "messages": [{"role": "user", "content": message}]
            }
            
            response = httpx.post(f"{API_URL}/agents/eva/runs", json=run_data)
            
            if response.status_code == 200:
                run_info = response.json()
                run_id = run_info.get("run_id")
                
                if not run_id:
                    print_colored("❌ No run_id in response", Colors.RED)
                    return None
                
                # Get the response
                events_response = httpx.get(f"{API_URL}/agents/eva/runs/{run_id}/events")
                
                if events_response.status_code == 200:
                    events = events_response.json()
                    for event in events:
                        if event.get("event") == "message" and event.get("message", {}).get("role") == "assistant":
                            response_text = event.get("message", {}).get("content", "")
                            print_colored(f"🤖 EVA: {response_text}", Colors.CYAN)
                            return response_text
                    
                    print_colored("❌ No assistant message found in events", Colors.RED)
                    return None
                else:
                    print_colored(f"❌ Error getting events: {events_response.status_code}", Colors.RED)
                    return None
            else:
                print_colored(f"❌ Error creating run: {response.status_code}", Colors.RED)
                return None
        except Exception as e:
            print_colored(f"❌ Error: {e}", Colors.RED)
            return None
    
    async def play_response(self, text):
        """Play TTS response"""
        if not text:
            return
        
        try:
            # Request TTS from EVA
            tts_data = {"text": text, "voice": "alloy"}
            response = httpx.post(f"{API_URL}/api/tts", json=tts_data)
            
            if response.status_code == 200:
                # Save audio to temp file
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp:
                    temp.write(response.content)
                    temp_filename = temp.name
                
                # Play audio
                if HAS_PYGAME:
                    print_colored("🔊 Playing response...", Colors.BLUE)
                    pygame.mixer.music.load(temp_filename)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                else:
                    print_colored("⚠️ Audio playback not available", Colors.YELLOW)
                
                # Clean up temp file
                os.unlink(temp_filename)
            else:
                print_colored(f"❌ Error getting TTS: {response.status_code}", Colors.RED)
        except Exception as e:
            print_colored(f"❌ Error playing response: {e}", Colors.RED)
    
    async def run(self):
        """Main loop"""
        print_colored("🎤 Simple Voice Client for EVA", Colors.PURPLE)
        print_colored("Press ENTER to start recording")
        print_colored("Press ENTER again to stop recording and send to EVA")
        print_colored("Press Ctrl+C to exit\n")
        
        try:
            while True:
                # Wait for user to press Enter to start recording
                input("Press ENTER to start recording...")
                
                # Record audio
                audio_data = self.record_audio()
                
                if audio_data is not None and len(audio_data) > 0:
                    # Save audio to file
                    audio_file = self.save_audio(audio_data)
                    
                    # Transcribe audio
                    transcript = await self.transcribe_audio(audio_file)
                    
                    if transcript:
                        # Send to EVA
                        response = await self.send_to_eva(transcript)
                        
                        # Play response
                        await self.play_response(response)
                
                print_colored("\nReady for next recording!", Colors.GREEN)
        
        except KeyboardInterrupt:
            print_colored("\nExiting...", Colors.YELLOW)
            sys.exit(0)

async def main():
    client = SimpleVoiceClient()
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())
