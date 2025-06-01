#!/usr/bin/env python3
"""
Test script for ElevenLabs TTS and STT integration with Eva Agent.
"""

import asyncio
import httpx
import json
import base64
from pathlib import Path

# Eva Agent base URL
BASE_URL = "http://localhost:8000"

async def test_tts():
    """Test text-to-speech functionality."""
    print("Testing TTS...")
    
    async with httpx.AsyncClient() as client:
        # Get available voices
        voices_response = await client.get(f"{BASE_URL}/api/voices")
        if voices_response.status_code == 200:
            voices = voices_response.json()
            print(f"Available voices: {len(voices.get('voices', []))}")
            if voices.get('voices'):
                print(f"First voice: {voices['voices'][0]['name']} (ID: {voices['voices'][0]['voice_id']})")
        
        # Test TTS
        tts_data = {
            "text": "Hello! This is a test of the ElevenLabs text-to-speech integration with Eva Agent.",
            "stream": False
        }
        
        response = await client.post(
            f"{BASE_URL}/api/tts",
            json=tts_data,
            timeout=30.0
        )
        
        if response.status_code == 200:
            # Save audio file
            with open("test_tts_output.mp3", "wb") as f:
                f.write(response.content)
            print("✓ TTS successful! Audio saved to test_tts_output.mp3")
        else:
            print(f"✗ TTS failed: {response.status_code} - {response.text}")

async def test_agent_with_voice():
    """Test Eva agent with voice enabled."""
    print("\nTesting Eva agent with voice...")
    
    async with httpx.AsyncClient() as client:
        # Create a run with voice enabled
        run_data = {
            "messages": [
                {
                    "role": "user",
                    "content": "Hello Eva! Can you tell me a short joke?"
                }
            ],
            "stream": True,
            "voice_enabled": True
        }
        
        # Create run
        response = await client.post(
            f"{BASE_URL}/agents/eva/runs",
            json=run_data
        )
        
        if response.status_code != 200:
            print(f"✗ Failed to create run: {response.status_code} - {response.text}")
            return
        
        run_info = response.json()
        run_id = run_info["run_id"]
        print(f"Created run: {run_id}")
        
        # Stream events
        audio_received = False
        message_content = ""
        
        async with client.stream(
            "GET",
            f"{BASE_URL}/agents/eva/runs/{run_id}/events",
            timeout=30.0
        ) as response:
            async for line in response.aiter_lines():
                if not line or line.startswith(":"):
                    continue
                
                try:
                    event = json.loads(line)
                    event_type = event.get("event_type")
                    
                    if event_type == "agent.message":
                        message = event["data"]["message"]
                        if not message.get("is_partial", False):
                            message_content = message["content"]
                            print(f"Agent response: {message_content}")
                    
                    elif event_type == "agent.audio":
                        audio_data = event["data"]["audio"]
                        audio_bytes = base64.b64decode(audio_data)
                        
                        # Save audio
                        with open("test_agent_voice.mp3", "wb") as f:
                            f.write(audio_bytes)
                        
                        audio_received = True
                        print("✓ Voice response received! Audio saved to test_agent_voice.mp3")
                        break
                    
                    elif event_type == "agent.status":
                        status = event["data"]["status"]
                        if status == "waiting_for_input":
                            break
                            
                except json.JSONDecodeError:
                    continue
        
        if not audio_received:
            print("✗ No audio response received")

async def test_stt():
    """Test speech-to-text functionality (requires OpenAI API key)."""
    print("\nTesting STT...")
    
    # Check if we have a test audio file
    test_audio_path = Path("test_audio.webm")
    if not test_audio_path.exists():
        print("✗ STT test skipped: No test_audio.webm file found")
        print("  To test STT, record an audio file named 'test_audio.webm'")
        return
    
    async with httpx.AsyncClient() as client:
        with open(test_audio_path, "rb") as f:
            files = {"file": ("test_audio.webm", f, "audio/webm")}
            
            response = await client.post(
                f"{BASE_URL}/api/stt",
                files=files,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ STT successful! Transcription: {result['text']}")
            elif response.status_code == 503:
                print("✗ STT service not available (OpenAI API key not configured)")
            else:
                print(f"✗ STT failed: {response.status_code} - {response.text}")

async def main():
    """Run all tests."""
    print("ElevenLabs Integration Test Suite for Eva Agent")
    print("=" * 50)
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/info")
            if response.status_code == 200:
                info = response.json()
                print(f"Eva Agent is running")
                print(f"- Model: {info['model']}")
                print(f"- TTS enabled: {info.get('tts_enabled', False)}")
                print(f"- STT enabled: {info.get('stt_enabled', False)}")
                print()
            else:
                print("✗ Eva Agent is not responding properly")
                return
    except httpx.ConnectError:
        print("✗ Cannot connect to Eva Agent. Make sure it's running on http://localhost:8000")
        return
    
    # Run tests
    await test_tts()
    await test_agent_with_voice()
    await test_stt()
    
    print("\nTest suite completed!")

if __name__ == "__main__":
    asyncio.run(main())