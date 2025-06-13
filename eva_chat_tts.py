#!/usr/bin/env python3
"""
EVA Chat with TTS - Text chat interface with Text-to-Speech
Combines the working text chat with ElevenLabs TTS for voice responses
"""

import asyncio
import httpx
import sys
import os
import tempfile
import subprocess
import platform
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from integrations.elevenlabs_integration import ElevenLabsIntegration

# Configuration
EVA_SERVER_URL = "http://localhost:1234"
USER_ID = "text_tts_user"
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'

class TTSPlayer:
    """Simple TTS audio player using system commands"""
    
    def __init__(self):
        self.system = platform.system().lower()
        
    async def play_audio(self, audio_data: bytes):
        """Play audio data using system audio player"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            # Play based on system
            if self.system == "linux":
                # Try common Linux audio players
                for player in ["mpg123", "ffplay", "aplay", "paplay"]:
                    try:
                        if player == "ffplay":
                            process = await asyncio.create_subprocess_exec(
                                player, "-nodisp", "-autoexit", tmp_path,
                                stdout=asyncio.subprocess.DEVNULL,
                                stderr=asyncio.subprocess.DEVNULL
                            )
                        else:
                            process = await asyncio.create_subprocess_exec(
                                player, tmp_path,
                                stdout=asyncio.subprocess.DEVNULL,
                                stderr=asyncio.subprocess.DEVNULL
                            )
                        await process.wait()
                        break
                    except FileNotFoundError:
                        continue
            elif self.system == "darwin":  # macOS
                process = await asyncio.create_subprocess_exec(
                    "afplay", tmp_path,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await process.wait()
            elif self.system == "windows":
                # Windows Media Player
                import winsound
                winsound.PlaySound(tmp_path, winsound.SND_FILENAME)
            
            # Clean up
            os.unlink(tmp_path)
            
        except Exception as e:
            print(f"{Colors.RED}TTS Error: {e}{Colors.RESET}")

async def chat_with_eva(message: str, context="general", mode="friend"):
    """Send message to EVA and get response"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EVA_SERVER_URL}/api/chat-simple",
                json={
                    "message": message,
                    "user_id": USER_ID,
                    "context": context,
                    "mode": mode
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "Sorry, I couldn't process that.")
            else:
                return f"Error: {response.status_code}"
                
    except Exception as e:
        return f"Connection error: {e}"

async def main():
    print(f"{Colors.PURPLE}🤖 EVA Text Chat + TTS{Colors.RESET}")
    print(f"{Colors.YELLOW}Type 'exit' to quit{Colors.RESET}")
    print(f"{Colors.YELLOW}Type '/context work|personal|creative|research' to switch context{Colors.RESET}")
    print(f"{Colors.YELLOW}Type '/mode friend|assistant|coach|tutor' to switch mode{Colors.RESET}")
    print(f"{Colors.YELLOW}Type '/tts on|off' to toggle text-to-speech{Colors.RESET}\n")
    
    # Initialize TTS
    tts_enabled = False
    tts = None
    player = TTSPlayer()
    
    if ELEVENLABS_API_KEY:
        try:
            tts = ElevenLabsIntegration(ELEVENLABS_API_KEY)
            tts_enabled = True
            print(f"{Colors.MAGENTA}🔊 TTS Ready (ElevenLabs){Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}TTS Error: {e}{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠️  TTS Disabled (No ELEVENLABS_API_KEY){Colors.RESET}")
    
    # Test connection
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{EVA_SERVER_URL}/api/info", timeout=3.0)
            if resp.status_code == 200:
                info = resp.json()
                print(f"{Colors.GREEN}✅ Connected to EVA v{info['version']}{Colors.RESET}")
                print(f"{Colors.CYAN}Model: {info['model']}{Colors.RESET}\n")
    except:
        print(f"{Colors.RED}❌ Cannot connect to EVA!{Colors.RESET}")
        print(f"{Colors.YELLOW}Start EVA with: python core/eva.py{Colors.RESET}")
        return
    
    context = "general"
    mode = "friend"
    tts_active = tts_enabled
    
    while True:
        try:
            # Show TTS status in prompt
            tts_indicator = "🔊" if tts_active else "🔇"
            user_input = input(f"{Colors.BLUE}You {tts_indicator}: {Colors.RESET}")
            
            # Check for exit
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print(f"{Colors.PURPLE}👋 Goodbye!{Colors.RESET}")
                break
            
            # Check for commands
            if user_input.startswith('/context '):
                new_context = user_input.split(' ', 1)[1]
                if new_context in ['work', 'personal', 'creative', 'research', 'general']:
                    context = new_context
                    print(f"{Colors.CYAN}Switched to {context} context{Colors.RESET}")
                continue
                
            if user_input.startswith('/mode '):
                new_mode = user_input.split(' ', 1)[1]
                if new_mode in ['friend', 'assistant', 'coach', 'tutor', 'advisor', 'analyst', 'creative']:
                    mode = new_mode
                    print(f"{Colors.CYAN}Switched to {mode} mode{Colors.RESET}")
                continue
            
            if user_input.startswith('/tts '):
                tts_command = user_input.split(' ', 1)[1].lower()
                if tts_command == 'on' and tts_enabled:
                    tts_active = True
                    print(f"{Colors.MAGENTA}🔊 TTS Enabled{Colors.RESET}")
                elif tts_command == 'off':
                    tts_active = False
                    print(f"{Colors.CYAN}🔇 TTS Disabled{Colors.RESET}")
                elif tts_command == 'on' and not tts_enabled:
                    print(f"{Colors.RED}TTS not available (check ELEVENLABS_API_KEY){Colors.RESET}")
                continue
            
            # Skip empty
            if not user_input.strip():
                continue
            
            # Send to EVA
            print(f"{Colors.GREEN}Eva: {Colors.RESET}", end="", flush=True)
            response = await chat_with_eva(user_input, context, mode)
            print(response)
            
            # Play TTS if enabled
            if tts_active and tts and response and not response.startswith("Error"):
                try:
                    print(f"{Colors.MAGENTA}🔊 Speaking...{Colors.RESET}", end="", flush=True)
                    audio_data = await tts.text_to_speech(response)
                    await player.play_audio(audio_data)
                    print(f"\r{Colors.MAGENTA}🔊 Done      {Colors.RESET}")
                except Exception as e:
                    print(f"\r{Colors.RED}TTS Error: {e}{Colors.RESET}")
            
            print()
            
        except KeyboardInterrupt:
            print(f"\n{Colors.PURPLE}👋 Goodbye!{Colors.RESET}")
            break
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")

if __name__ == "__main__":
    asyncio.run(main())