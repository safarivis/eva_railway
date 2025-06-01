#!/usr/bin/env python3
"""
Global Voice-to-Claude Code System
Based on the architecture from the video: RealtimeSTT + Claude Code + OpenAI TTS
~700 lines for complete implementation
"""

import os
import sys
import subprocess
import asyncio
import json
import tempfile
from datetime import datetime
from typing import Optional, List, Dict, Any
import threading
import queue

# Real-time STT
from RealtimeSTT import AudioToTextRecorder
import sounddevice as sd
import numpy as np

# OpenAI for TTS and optional STT
import openai
from openai import OpenAI

# Audio playback
import pygame
import soundfile as sf

# System integration
from pynput import keyboard
import pyperclip

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
CLAUDE_CODE_PATH = "claude"  # Or full path to claude executable
TRIGGER_WORDS = ["claude", "sonnet", "opus", "hey claude"]
USE_COMPRESSED_RESPONSE = True  # Compress Claude's response with GPT-4 mini

class Colors:
    """Terminal colors for output"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text, color=Colors.GREEN):
    """Print colored text to terminal"""
    print(f"{color}{text}{Colors.RESET}")

class ClaudeCodeVoiceAssistant:
    """Global voice assistant for Claude Code"""
    
    def __init__(self):
        # Initialize components
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        pygame.mixer.init()
        
        # State
        self.listening = True
        self.processing = False
        self.conversation_history = []
        self.output_dir = "claude_code_conversations"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Audio queue for TTS
        self.audio_queue = queue.Queue()
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.tts_thread.start()
        
        # Initialize RealtimeSTT
        self.recorder = AudioToTextRecorder(
            model="tiny.en",  # Fast model for wake word detection
            language="en",
            silero_sensitivity=0.4,
            webrtcvad_aggressiveness=3,
            post_speech_silence_duration=0.4,
            min_length_of_recording=0.5,
            min_gap_between_recordings=0,
            enable_realtime_transcription=True,
            realtime_processing_pause=0.2,
            on_realtime_transcription_update=self._on_realtime_update,
            on_recording_start=self._on_recording_start,
            on_recording_stop=self._on_recording_stop
        )
        
        print_colored("\n🎤 Voice-to-Claude Code Assistant Started! 🎤", Colors.PURPLE)
        print_colored(f"Trigger words: {', '.join(TRIGGER_WORDS)}", Colors.YELLOW)
        print_colored("Say trigger word + your command", Colors.YELLOW)
        print_colored("Press Ctrl+C to exit\n", Colors.YELLOW)
    
    def _on_recording_start(self):
        """Called when recording starts"""
        print_colored("🎙️ Recording...", Colors.YELLOW)
    
    def _on_recording_stop(self):
        """Called when recording stops"""
        print_colored("⏹️ Processing...", Colors.YELLOW)
    
    def _on_realtime_update(self, text):
        """Called with real-time transcription updates"""
        # Show partial transcription
        print(f"\r💭 {text}", end='', flush=True)
    
    def _contains_trigger_word(self, text):
        """Check if text contains any trigger word"""
        text_lower = text.lower()
        return any(trigger in text_lower for trigger in TRIGGER_WORDS)
    
    def _extract_command(self, text):
        """Extract command after trigger word"""
        text_lower = text.lower()
        for trigger in TRIGGER_WORDS:
            if trigger in text_lower:
                # Find the trigger position and extract everything after
                idx = text_lower.find(trigger)
                command = text[idx + len(trigger):].strip()
                if command:
                    return command
        return text  # Return full text if no clear separation
    
    async def _call_claude_code(self, prompt):
        """Call Claude Code as a programmable tool"""
        print_colored(f"\n🤖 Calling Claude Code...", Colors.BLUE)
        
        try:
            # Save conversation history
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            history_file = os.path.join(self.output_dir, f"conversation_{timestamp}.json")
            
            # Add to history
            self.conversation_history.append({
                "timestamp": timestamp,
                "user": prompt,
                "processing": True
            })
            
            # Write history
            with open(history_file, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
            
            # Call Claude Code via CLI
            # Note: This assumes 'claude' command is available globally
            # You might need to adjust the path or use the API directly
            process = await asyncio.create_subprocess_exec(
                CLAUDE_CODE_PATH,
                'chat',
                '--message', prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                response = stdout.decode('utf-8').strip()
                
                # Update history with response
                self.conversation_history[-1]["processing"] = False
                self.conversation_history[-1]["assistant"] = response
                
                with open(history_file, 'w') as f:
                    json.dump(self.conversation_history, f, indent=2)
                
                return response
            else:
                error_msg = stderr.decode('utf-8').strip()
                print_colored(f"❌ Error: {error_msg}", Colors.RED)
                return None
                
        except Exception as e:
            print_colored(f"❌ Error calling Claude Code: {e}", Colors.RED)
            return None
    
    def _compress_response(self, response):
        """Compress Claude's response using GPT-4 mini for natural speech"""
        if not USE_COMPRESSED_RESPONSE or not response:
            return response
            
        try:
            compressed = self.openai_client.chat.completions.create(
                model="gpt-4-0125-preview",  # Or "gpt-3.5-turbo" for faster/cheaper
                messages=[
                    {"role": "system", "content": "Compress the following response into a natural, conversational summary. Keep technical details but make it sound natural when spoken aloud. Maximum 2-3 sentences."},
                    {"role": "user", "content": response}
                ],
                max_tokens=150,
                temperature=0.7
            )
            return compressed.choices[0].message.content
        except Exception as e:
            print_colored(f"Compression error: {e}", Colors.YELLOW)
            return response[:500] + "..." if len(response) > 500 else response
    
    def _generate_speech(self, text):
        """Generate speech using OpenAI TTS"""
        try:
            response = self.openai_client.audio.speech.create(
                model="tts-1",  # or "tts-1-hd" for better quality
                voice="nova",   # Options: alloy, echo, fable, onyx, nova, shimmer
                input=text,
                speed=1.0
            )
            
            # Save to temporary file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file = os.path.join(self.output_dir, f"response_{timestamp}.mp3")
            
            with open(audio_file, 'wb') as f:
                f.write(response.content)
            
            return audio_file
            
        except Exception as e:
            print_colored(f"❌ TTS error: {e}", Colors.RED)
            return None
    
    def _play_audio(self, audio_file):
        """Play audio file"""
        try:
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print_colored(f"❌ Audio playback error: {e}", Colors.RED)
    
    def _tts_worker(self):
        """Worker thread for TTS playback"""
        while True:
            try:
                text = self.audio_queue.get()
                if text is None:  # Shutdown signal
                    break
                    
                audio_file = self._generate_speech(text)
                if audio_file:
                    self._play_audio(audio_file)
                    
            except Exception as e:
                print_colored(f"TTS worker error: {e}", Colors.RED)
    
    async def process_command(self, transcription):
        """Process a voice command"""
        print(f"\n💬 You: {transcription}", flush=True)
        
        # Check for trigger word
        if not self._contains_trigger_word(transcription):
            print_colored("No trigger word detected", Colors.YELLOW)
            return
        
        # Extract command
        command = self._extract_command(transcription)
        if not command:
            print_colored("No command found after trigger word", Colors.YELLOW)
            return
        
        print_colored(f"📤 Command: {command}", Colors.BLUE)
        
        # Call Claude Code
        response = await self._call_claude_code(command)
        
        if response:
            print_colored(f"\n🤖 Claude: {response}", Colors.GREEN)
            
            # Compress and speak response
            compressed = self._compress_response(response)
            print_colored(f"🔊 Speaking: {compressed}", Colors.PURPLE)
            self.audio_queue.put(compressed)
    
    def start_listening(self):
        """Start the main listening loop"""
        try:
            print_colored("👂 Listening for commands...", Colors.CYAN)
            
            while self.listening:
                # Get transcription from RealtimeSTT
                transcription = self.recorder.text()
                
                if transcription:
                    # Process in background
                    asyncio.run(self.process_command(transcription))
                    
        except KeyboardInterrupt:
            print_colored("\n\n👋 Shutting down...", Colors.YELLOW)
        finally:
            self.stop()
    
    def stop(self):
        """Stop the assistant"""
        self.listening = False
        self.audio_queue.put(None)  # Signal TTS worker to stop
        self.recorder.stop()
        print_colored("Assistant stopped", Colors.GREEN)


class GlobalHotkeyListener:
    """Global hotkey listener for push-to-talk mode"""
    
    def __init__(self, assistant):
        self.assistant = assistant
        self.recording = False
        self.ptt_key = keyboard.Key.cmd  # Windows key, change as needed
        
    def on_press(self, key):
        if key == self.ptt_key and not self.recording:
            self.recording = True
            print_colored("\n🎤 Push-to-talk activated", Colors.GREEN)
            # Start recording
            
    def on_release(self, key):
        if key == self.ptt_key and self.recording:
            self.recording = False
            print_colored("🎤 Push-to-talk released", Colors.YELLOW)
            # Stop recording and process
            
        if key == keyboard.Key.esc:
            # Stop listener
            return False
    
    def start(self):
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        ) as listener:
            listener.join()


# Alternative implementation using system command execution
def execute_claude_code_command(prompt):
    """Execute Claude Code command and return result"""
    try:
        # Method 1: Using subprocess with claude CLI
        result = subprocess.run(
            ['claude', 'chat', '--message', prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except FileNotFoundError:
        # Method 2: Try using the web API if CLI not found
        return call_claude_api_directly(prompt)
    except Exception as e:
        return f"Error: {str(e)}"


def call_claude_api_directly(prompt):
    """Call Claude API directly if CLI not available"""
    # This would use the Anthropic Python SDK
    # Similar to the EVA agent implementation
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    except Exception as e:
        return f"API Error: {str(e)}"


def main():
    """Main entry point"""
    # Check dependencies
    required_packages = ['RealtimeSTT', 'openai', 'pygame', 'sounddevice', 'pynput']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print_colored(f"Missing packages: {', '.join(missing)}", Colors.RED)
        print_colored("Install with: pip install RealtimeSTT openai pygame sounddevice pynput", Colors.YELLOW)
        sys.exit(1)
    
    # Check environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print_colored("Error: OPENAI_API_KEY not set", Colors.RED)
        sys.exit(1)
    
    # Start assistant
    assistant = ClaudeCodeVoiceAssistant()
    
    # Option 1: Always listening mode with trigger words
    assistant.start_listening()
    
    # Option 2: Push-to-talk mode (uncomment to use)
    # hotkey_listener = GlobalHotkeyListener(assistant)
    # hotkey_listener.start()


if __name__ == "__main__":
    main()