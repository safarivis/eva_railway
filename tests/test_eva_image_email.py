#!/usr/bin/env python3
"""
Test EVA image generation and email sending end-to-end
"""
import asyncio
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.eva import get_agent_response
from core.eva import active_conversations

async def test_eva_image_and_email():
    """Test EVA generating an image and sending it via email"""
    print("🧪 Testing EVA image generation and email...")
    
    # Create a test session
    session_id = "test_image_email_session"
    active_conversations[session_id] = {
        "messages": [],
        "context": "general",
        "mode": "assistant"
    }
    
    try:
        # Test message asking Eva to generate an image and email it
        test_message = "Generate a simple image of a blue square and email it to louisrdup@gmail.com with the subject 'Test Image Generation Fix'"
        
        print(f"📤 Sending message to Eva: '{test_message}'")
        
        response = await get_agent_response(session_id, test_message)
        
        print(f"📨 Eva's response:")
        print(response)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Eva: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🔧 Testing EVA end-to-end image generation and email")
    print("=" * 60)
    
    success = await test_eva_image_and_email()
    
    print("=" * 60)
    if success:
        print("✅ Test completed - check your email!")
    else:
        print("❌ Test failed")

if __name__ == "__main__":
    asyncio.run(main())