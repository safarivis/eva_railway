#!/usr/bin/env python3
"""
EVA Voice with Local STT - Talk to EVA without typing!
Uses local faster-whisper for speech recognition (no API costs)
"""

import os
import sys
import time
import wave
import asyncio
import httpx
import json
import sounddevice as sd
import numpy as np
from datetime import datetime
from pathlib import Path

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
DURATION = 5  # Max recording duration in seconds
EVA_SERVER_URL = "http://localhost:8000"

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text, color=Colors.GREEN):
    print(f"{color}{text}{Colors.RESET}")

class LocalVoiceChat:
    def __init__(self):
        self.recording = False
        self.audio_data = []
        self.context = "general"
        self.mode = "friend"
        self.user_id = "voice_user"
        
    def record_audio(self):
        """Record audio from microphone"""
        self.audio_data = []
        self.recording = True
        
        def callback(indata, frames, time, status):
            if self.recording:
                self.audio_data.append(indata.copy())
        
        with sd.InputStream(callback=callback, channels=CHANNELS, samplerate=SAMPLE_RATE, dtype='float32'):
            print_colored("🎤 Listening... Press ENTER when done speaking", Colors.YELLOW)
            input()
            self.recording = False
            
        if not self.audio_data:
            return None
            
        return np.concatenate(self.audio_data, axis=0)
    
    def save_temp_audio(self, audio_data):
        """Save audio to temporary file for transcription"""
        temp_dir = Path("data/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = temp_dir / f"temp_audio_{timestamp}.wav"
        
        try:
            # Convert to 16-bit PCM
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # Save WAV file
            with wave.open(str(filename), 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio_int16.tobytes())
            
            return str(filename)
        except Exception as e:
            print_colored(f"❌ Error saving audio: {e}", Colors.RED)
            return None
    
    async def transcribe_audio(self, audio_file):
        """Transcribe audio using local STT"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                with open(audio_file, 'rb') as f:
                    files = {'file': ('audio.wav', f, 'audio/wav')}
                    response = await client.post(
                        f"{EVA_SERVER_URL}/api/stt/local",
                        files=files
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('text', '')
                else:
                    print_colored(f"❌ STT error: {response.text}", Colors.RED)
                    return None
        except Exception as e:
            print_colored(f"❌ Transcription error: {e}", Colors.RED)
            return None
        finally:
            # Clean up temp file
            try:
                os.unlink(audio_file)
            except:
                pass
    
    async def send_to_eva(self, text):
        """Send message to EVA and get response"""
        try:
            print_colored(f"\n💭 You: {text}", Colors.CYAN)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Prepare the message
                payload = {
                    "messages": [{"role": "user", "content": text}],
                    "stream": False,
                    "context": self.context,
                    "mode": self.mode,
                    "user_id": self.user_id,
                    "voice_enabled": True,
                    "voice_id": "rachel"  # Default voice
                }
                
                # Send to EVA
                response = await client.post(
                    f"{EVA_SERVER_URL}/api/runs",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    eva_response = result.get('response', 'Sorry, I had trouble understanding.')
                    print_colored(f"\n🤖 EVA: {eva_response}", Colors.GREEN)
                    
                    # Play audio if available
                    if result.get('audio_url'):
                        await self.play_audio(result['audio_url'])
                    
                    return eva_response
                else:
                    print_colored(f"❌ EVA error: {response.text}", Colors.RED)
                    return None
                    
        except Exception as e:
            print_colored(f"❌ Communication error: {e}", Colors.RED)
            return None
    
    async def play_audio(self, audio_url):
        """Play EVA's audio response"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{EVA_SERVER_URL}{audio_url}")
                if response.status_code == 200:
                    # Save and play audio
                    temp_file = "data/temp/eva_response.mp3"
                    with open(temp_file, 'wb') as f:
                        f.write(response.content)
                    
                    # Use system command to play
                    os.system(f"mpg123 -q {temp_file} 2>/dev/null || afplay {temp_file} 2>/dev/null")
                    os.unlink(temp_file)
        except:
            pass  # Audio playback is optional
    
    async def run(self):
        """Main voice chat loop"""
        print_colored("\n🎙️  EVA Voice Chat with Local STT", Colors.BOLD)
        print_colored("=" * 50, Colors.BLUE)
        print_colored("✅ Using FREE local speech recognition", Colors.GREEN)
        print_colored("✅ No API costs for voice input", Colors.GREEN)
        print_colored("✅ Your audio stays on your computer", Colors.GREEN)
        print_colored("\n📋 Commands:", Colors.YELLOW)
        print_colored("  • Press ENTER to start/stop recording", Colors.CYAN)
        print_colored("  • Say 'exit' or 'quit' to leave", Colors.CYAN)
        print_colored("  • Type /context [work|personal|creative|research]", Colors.CYAN)
        print_colored("  • Type /mode [friend|assistant|coach|tutor]", Colors.CYAN)
        print_colored("=" * 50, Colors.BLUE)
        
        # Check EVA server
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{EVA_SERVER_URL}/api/info")
                if response.status_code != 200:
                    raise Exception("EVA server not responding")
        except:
            print_colored("\n❌ EVA server not running!", Colors.RED)
            print_colored("Please start EVA first: python core/eva.py", Colors.YELLOW)
            return
        
        print_colored("\n✅ Connected to EVA! Start speaking...\n", Colors.GREEN)
        
        while True:
            try:
                # Get user input
                user_input = input(f"{Colors.PURPLE}Press ENTER to speak (or type command): {Colors.RESET}")
                
                # Handle text commands
                if user_input.startswith('/'):
                    parts = user_input.split()
                    if parts[0] == '/context' and len(parts) > 1:
                        self.context = parts[1]
                        print_colored(f"✅ Context changed to: {self.context}", Colors.GREEN)
                        continue
                    elif parts[0] == '/mode' and len(parts) > 1:
                        self.mode = parts[1]
                        print_colored(f"✅ Mode changed to: {self.mode}", Colors.GREEN)
                        continue
                
                # Record audio
                audio_data = self.record_audio()
                if audio_data is None or len(audio_data) == 0:
                    print_colored("No audio recorded, try again", Colors.YELLOW)
                    continue
                
                # Save to temp file
                audio_file = self.save_temp_audio(audio_data)
                if not audio_file:
                    continue
                
                # Transcribe with local STT
                print_colored("🔄 Transcribing locally...", Colors.YELLOW)
                text = await self.transcribe_audio(audio_file)
                
                if not text:
                    print_colored("Could not transcribe audio", Colors.YELLOW)
                    continue
                
                # Check for exit commands
                if text.lower() in ['exit', 'quit', 'goodbye', 'bye']:
                    print_colored("\n👋 Goodbye!", Colors.GREEN)
                    break
                
                # Send to EVA
                await self.send_to_eva(text)
                
            except KeyboardInterrupt:
                print_colored("\n\n👋 Goodbye!", Colors.GREEN)
                break
            except Exception as e:
                print_colored(f"❌ Error: {e}", Colors.RED)

if __name__ == "__main__":
    chat = LocalVoiceChat()
    asyncio.run(chat.run())