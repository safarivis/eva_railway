#!/usr/bin/env python3
"""
EVA Voice Chat - Minimal working voice interface
Works with Python 3.13 and avoids all problematic imports
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Only import what we absolutely need
try:
    import httpx
    import speech_recognition as sr
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install: pip install httpx SpeechRecognition")
    sys.exit(1)

# Configuration
EVA_SERVER_URL = "http://localhost:8000"

class SimpleVoiceChat:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 200
        self.recognizer.dynamic_energy_threshold = True
        
    def listen_once(self):
        """Listen for voice input and return text"""
        try:
            with sr.Microphone() as source:
                print("🎤 Listening... (speak now)")
                # Adjust for ambient noise quickly
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Listen with timeout
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
            print("🔍 Processing...")
            text = self.recognizer.recognize_google(audio)
            return text
            
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Recognition service error: {e}")
            return None
        except sr.WaitTimeoutError:
            print("⏰ No speech detected")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    async def send_to_eva(self, message):
        """Send message to EVA and get response"""
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
                    return data.get("response", "Sorry, I couldn't process that.")
                else:
                    print(f"❌ API Error: {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return None
    
    async def run(self):
        """Main chat loop"""
        print("\n🤖 EVA Voice Chat")
        print("📢 Press Enter to start listening")
        print("💬 Or type your message")
        print("🚪 Type 'exit' to quit\n")
        
        # Test connection
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{EVA_SERVER_URL}/api/info", timeout=3.0)
                if resp.status_code == 200:
                    print("✅ Connected to EVA\n")
                else:
                    print("⚠️  EVA not fully ready\n")
        except:
            print("❌ Cannot connect to EVA. Start it with: python core/eva.py\n")
            return
        
        while True:
            try:
                # Prompt for input method
                user_input = input("Press Enter for voice or type message: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                # If they typed something, use it
                if user_input:
                    message = user_input
                    print(f"You: {message}")
                else:
                    # Otherwise, listen for voice
                    message = self.listen_once()
                    if message:
                        print(f"You said: {message}")
                    else:
                        continue
                
                # Send to EVA
                print("Eva: ", end="", flush=True)
                response = await self.send_to_eva(message)
                if response:
                    print(response)
                
                print()  # Empty line
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

async def main():
    chat = SimpleVoiceChat()
    await chat.run()

if __name__ == "__main__":
    asyncio.run(main())