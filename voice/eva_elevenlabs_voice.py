#!/usr/bin/env python3
"""
EVA ElevenLabs Voice - Pure ElevenLabs voice interface
Uses ElevenLabs for both STT and TTS, no SpeechRecognition needed
"""

import os
import sys
import asyncio
import tempfile
from datetime import datetime
from pathlib import Path

try:
    import httpx
    import sounddevice as sd
    import numpy as np
except ImportError as e:
    print(f"❌ Missing package: {e}")
    print("Please install: pip install httpx sounddevice numpy")
    sys.exit(1)

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
EVA_SERVER_URL = "http://localhost:8000"
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not ELEVENLABS_API_KEY:
    print("❌ ELEVENLABS_API_KEY not found in environment")
    print("Please set your ElevenLabs API key")
    sys.exit(1)

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

class ElevenLabsVoiceChat:
    def __init__(self):
        self.recording = False
        self.audio_data = []
        
    def record_audio(self):
        """Record audio for ElevenLabs"""
        self.audio_data = []
        self.recording = True
        
        def callback(indata, frames, time, status):
            if self.recording:
                self.audio_data.append(indata.copy())
        
        with sd.InputStream(callback=callback, channels=CHANNELS, samplerate=SAMPLE_RATE, dtype='float32'):
            print_colored("🎤 Recording... Press ENTER to stop", Colors.YELLOW)
            input()
            self.recording = False
            
        if not self.audio_data:
            return None
            
        return np.concatenate(self.audio_data, axis=0)
    
    def save_audio(self, audio_data):
        """Save audio file"""
        voice_dir = Path("voice_recordings/eva_recordings")
        voice_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = voice_dir / f"eva_recording_{timestamp}.wav"
        
        try:
            # Convert to 16-bit PCM
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # Simple WAV file creation
            import wave
            with wave.open(str(filename), 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio_int16.tobytes())
            
            os.chmod(filename, 0o600)
            print_colored(f"🔐 Audio saved to {filename}", Colors.CYAN)
            return str(filename)
        except Exception as e:
            print_colored(f"❌ Error saving: {e}", Colors.RED)
            return None
    
    async def transcribe_with_elevenlabs(self, audio_data):
        """Use ElevenLabs speech-to-text"""
        try:
            # Convert to proper format for ElevenLabs
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_path = temp_file.name
                
            # Convert to MP3 using pydub if available, otherwise skip STT
            try:
                from pydub import AudioSegment
                from pydub.utils import make_chunks
                
                # Create audio segment
                audio_segment = AudioSegment(
                    audio_int16.tobytes(),
                    frame_rate=SAMPLE_RATE,
                    sample_width=2,
                    channels=CHANNELS
                )
                
                # Export as MP3
                audio_segment.export(temp_path, format="mp3", bitrate="128k")
                
            except ImportError:
                print_colored("❌ pydub not available, skipping ElevenLabs STT", Colors.RED)
                print_colored("💡 Install with: pip install pydub", Colors.YELLOW)
                return "Could not transcribe - please install pydub"
            
            print_colored("🔍 Transcribing with ElevenLabs...", Colors.PURPLE)
            
            async with httpx.AsyncClient() as client:
                with open(temp_path, 'rb') as audio_file:
                    files = {"audio": ("audio.mp3", audio_file, "audio/mpeg")}
                    headers = {"xi-api-key": ELEVENLABS_API_KEY}
                    
                    response = await client.post(
                        "https://api.elevenlabs.io/v1/speech-to-text",
                        headers=headers,
                        files=files,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        text = data.get("text", "").strip()
                        if text:
                            print_colored(f"💬 You: {text}", Colors.BLUE)
                            return text
                        else:
                            print_colored("❌ No speech detected", Colors.RED)
                            return None
                    else:
                        print_colored(f"❌ ElevenLabs STT error: {response.status_code}", Colors.RED)
                        return None
            
        except Exception as e:
            print_colored(f"❌ Transcription error: {e}", Colors.RED)
            return None
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass
    
    async def send_to_eva(self, message):
        """Send message to EVA and get response"""
        print_colored(f"📤 Sending to EVA: {message}", Colors.BLUE)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{EVA_SERVER_URL}/api/chat-simple",
                    json={
                        "message": message,
                        "user_id": "elevenlabs_user",
                        "context": "general",
                        "mode": "friend"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    eva_response = data.get("response", "Sorry, I couldn't process that.")
                    print_colored(f"🤖 EVA: {eva_response}", Colors.GREEN)
                    
                    # Generate TTS with ElevenLabs
                    await self.speak_with_elevenlabs(eva_response)
                    
                    return eva_response
                else:
                    print_colored(f"❌ EVA error: {response.status_code}", Colors.RED)
                    return None
                    
        except Exception as e:
            print_colored(f"❌ Error: {e}", Colors.RED)
            return None
    
    async def speak_with_elevenlabs(self, text):
        """Use ElevenLabs TTS to speak response"""
        try:
            print_colored("🔊 Generating speech with ElevenLabs...", Colors.PURPLE)
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "Content-Type": "application/json"
                }
                
                # Use a good voice (Rachel)
                voice_id = "21m00Tcm4TlvDq8ikWAM"  
                
                payload = {
                    "text": text,
                    "model_id": "eleven_turbo_v2_5",
                    "voice_settings": {
                        "stability": 0.75,
                        "similarity_boost": 0.8,
                        "style": 0.4
                    }
                }
                
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    # Save and play audio
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                        temp_file.write(response.content)
                        temp_path = temp_file.name
                    
                    # Simple audio playback (you might need to install a player)
                    try:
                        import pygame
                        pygame.mixer.init()
                        pygame.mixer.music.load(temp_path)
                        pygame.mixer.music.play()
                        
                        while pygame.mixer.music.get_busy():
                            pygame.time.Clock().tick(10)
                    except:
                        print_colored("🔊 Audio generated (install pygame for playback)", Colors.CYAN)
                    
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                        
                else:
                    print_colored(f"❌ ElevenLabs TTS error: {response.status_code}", Colors.RED)
                    
        except Exception as e:
            print_colored(f"❌ TTS error: {e}", Colors.RED)
    
    async def run(self):
        """Main chat loop"""
        print_colored("\n🎤 EVA + ElevenLabs Voice Chat 🎤", Colors.PURPLE)
        print_colored("Using ElevenLabs for both STT and TTS", Colors.CYAN)
        print_colored("Press ENTER to record, ENTER to stop, Ctrl+C to exit\n", Colors.YELLOW)
        
        # Test connections
        try:
            async with httpx.AsyncClient() as client:
                # Test EVA
                eva_resp = await client.get(f"{EVA_SERVER_URL}/api/info", timeout=3.0)
                if eva_resp.status_code == 200:
                    print_colored("✅ EVA server connected", Colors.GREEN)
                
                # Test ElevenLabs
                headers = {"xi-api-key": ELEVENLABS_API_KEY}
                el_resp = await client.get("https://api.elevenlabs.io/v1/voices", headers=headers, timeout=3.0)
                if el_resp.status_code == 200:
                    print_colored("✅ ElevenLabs API connected", Colors.GREEN)
                else:
                    print_colored("❌ ElevenLabs API error", Colors.RED)
                    return
                    
        except Exception as e:
            print_colored(f"❌ Connection test failed: {e}", Colors.RED)
            return
        
        print()
        
        while True:
            try:
                input("Press ENTER to start recording...")
                
                # Record
                audio = self.record_audio()
                if audio is None:
                    continue
                
                # Save
                self.save_audio(audio)
                
                # Transcribe with ElevenLabs
                text = await self.transcribe_with_elevenlabs(audio)
                if text is None:
                    continue
                
                # Send to EVA (will also speak response)
                await self.send_to_eva(text)
                
            except KeyboardInterrupt:
                print_colored("\n👋 Goodbye from EVA + ElevenLabs!", Colors.PURPLE)
                break
            except Exception as e:
                print_colored(f"Error: {e}", Colors.RED)

async def main():
    chat = ElevenLabsVoiceChat()
    await chat.run()

if __name__ == "__main__":
    asyncio.run(main())