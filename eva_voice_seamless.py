#!/usr/bin/env python3
"""
Seamless Voice Interface for Eva - Just Talk Naturally!
No wake words, no button pressing - just conversation
"""

import asyncio
import aiohttp
import json
import time
from typing import Optional
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from RealtimeSTT import AudioToTextRecorder
    REALTIMESTT_AVAILABLE = True
except ImportError:
    REALTIMESTT_AVAILABLE = False
    print("⚠️  RealtimeSTT not installed. Install with: pip install RealtimeSTT")

# Fallback to webrtcvad-based solution
import pyaudio
import webrtcvad
import collections
import wave
import tempfile
from datetime import datetime

class SeamlessEvaVoice:
    """Truly seamless voice interface - just speak!"""
    
    def __init__(self, eva_url: str = "http://localhost:8000"):
        self.eva_url = eva_url
        self.session = None
        self.is_processing = False
        self.conversation_active = True
        self.last_speech_time = time.time()
        self.response_queue = asyncio.Queue()
        
        # Audio settings
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_duration = 30  # ms
        self.chunk_size = int(self.sample_rate * self.chunk_duration / 1000)
        
        # Initialize audio
        self.audio = pyaudio.PyAudio()
        self.vad = webrtcvad.Vad(2)  # Aggressiveness level 2
        
        print("\n🎙️  Eva Seamless Voice - Just Speak Naturally!")
        print("=" * 50)
        print("✨ No wake words needed")
        print("✨ No buttons to press")
        print("✨ Just talk like you would to a friend")
        print("=" * 50)
        
    async def start(self):
        """Start the seamless voice interface"""
        self.session = aiohttp.ClientSession()
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self.audio_stream_handler()),
            asyncio.create_task(self.response_handler()),
        ]
        
        try:
            print("\n🎤 Eva is listening... Just start talking!\n")
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        finally:
            await self.cleanup()
    
    async def audio_stream_handler(self):
        """Handle continuous audio streaming"""
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        # Ring buffer for smoothing
        ring_buffer = collections.deque(maxlen=90)  # ~3 seconds
        triggered = False
        voiced_frames = []
        
        while self.conversation_active:
            try:
                # Read audio chunk
                chunk = stream.read(self.chunk_size, exception_on_overflow=False)
                
                # Check if speech
                is_speech = self.vad.is_speech(chunk, self.sample_rate)
                ring_buffer.append((chunk, is_speech))
                
                if not triggered:
                    # Check if we should start recording
                    num_voiced = len([f for f, speech in ring_buffer if speech])
                    if num_voiced > 0.5 * ring_buffer.maxlen:
                        triggered = True
                        print("💬 Listening to you...", end='', flush=True)
                        # Add buffered audio
                        for f, s in ring_buffer:
                            voiced_frames.append(f)
                        ring_buffer.clear()
                else:
                    # We're recording
                    voiced_frames.append(chunk)
                    ring_buffer.append((chunk, is_speech))
                    
                    # Check if they stopped speaking
                    num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                    if num_unvoiced > 0.8 * ring_buffer.maxlen:
                        # Speech ended
                        print(" Done!")
                        triggered = False
                        
                        # Process the audio
                        if len(voiced_frames) > 20:  # Minimum length
                            await self.process_speech(b''.join(voiced_frames))
                        
                        voiced_frames = []
                        ring_buffer.clear()
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.001)
                
            except Exception as e:
                print(f"\n❌ Audio error: {e}")
                await asyncio.sleep(0.1)
        
        stream.stop_stream()
        stream.close()
    
    async def process_speech(self, audio_data: bytes):
        """Process speech and get Eva's response"""
        if self.is_processing:
            return
            
        self.is_processing = True
        self.last_speech_time = time.time()
        
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                with wave.open(tmp_file.name, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(audio_data)
                
                # Transcribe
                print("🧠 Understanding...", end='', flush=True)
                
                with open(tmp_file.name, 'rb') as audio_file:
                    files = {'file': ('audio.wav', audio_file, 'audio/wav')}
                    
                    async with self.session.post(
                        f"{self.eva_url}/api/stt/local",
                        data=files
                    ) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            text = result.get('text', '').strip()
                            
                            if text and len(text) > 2:
                                print(f" You said: '{text}'")
                                
                                # Get Eva's response
                                await self.get_eva_response(text)
                            else:
                                print(" (no speech detected)")
                        else:
                            print(f" STT error: {resp.status}")
                
                # Clean up
                os.unlink(tmp_file.name)
                
        except Exception as e:
            print(f"\n❌ Processing error: {e}")
        finally:
            self.is_processing = False
    
    async def get_eva_response(self, text: str):
        """Get response from Eva"""
        try:
            print("💭 Eva is thinking...", end='', flush=True)
            
            async with self.session.post(
                f"{self.eva_url}/api/chat-simple",
                json={
                    "message": text,
                    "user_id": "seamless_voice_user",
                    "context": "general",
                    "mode": "friend"
                }
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    response = data.get('response', '')
                    print(f" Eva: '{response}'")
                    
                    # Queue for speech
                    await self.response_queue.put(response)
                else:
                    print(f" Error: {resp.status}")
                    
        except Exception as e:
            print(f"\n❌ Eva error: {e}")
    
    async def response_handler(self):
        """Handle speaking Eva's responses"""
        while self.conversation_active:
            try:
                # Get response from queue
                response = await asyncio.wait_for(
                    self.response_queue.get(),
                    timeout=0.1
                )
                
                # Speak the response
                print("🗣️  Eva is speaking...")
                
                async with self.session.post(
                    f"{self.eva_url}/api/tts",
                    json={
                        "text": response,
                        "voice_id": "L4so9SudEsIYzE9j4qlR"  # Eva's voice
                    }
                ) as resp:
                    if resp.status == 200:
                        audio_data = await resp.read()
                        
                        # Play audio (simplified - in production use proper audio queue)
                        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                            tmp.write(audio_data)
                            tmp.flush()
                            
                            # Play with system command (cross-platform)
                            if sys.platform == "darwin":  # macOS
                                os.system(f"afplay {tmp.name}")
                            elif sys.platform == "linux":
                                os.system(f"mpg123 -q {tmp.name} 2>/dev/null || play -q {tmp.name}")
                            else:  # Windows
                                os.system(f"start /min {tmp.name}")
                            
                            os.unlink(tmp.name)
                        
                        print("✅ Ready for next question!\n")
                        
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"\n❌ Response error: {e}")
    
    async def cleanup(self):
        """Clean up resources"""
        self.conversation_active = False
        if self.session:
            await self.session.close()
        self.audio.terminate()


async def main():
    """Run the seamless voice interface"""
    
    # Check if RealtimeSTT is available for even better experience
    if REALTIMESTT_AVAILABLE:
        print("\n✨ RealtimeSTT is available! Using enhanced seamless mode...\n")
        # TODO: Implement RealtimeSTT version
    
    # Use our custom seamless implementation
    eva = SeamlessEvaVoice()
    await eva.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")