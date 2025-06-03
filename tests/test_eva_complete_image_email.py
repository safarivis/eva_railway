#!/usr/bin/env python3
"""
Test EVA complete image generation and email workflow
"""
import asyncio
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.eva import get_agent_response
from core.eva import active_conversations

async def test_eva_complete_workflow():
    """Test EVA generating an image and emailing it with attachment"""
    print("🧪 Testing EVA complete image generation and email workflow...")
    
    # Create a test session
    session_id = "test_complete_workflow"
    active_conversations[session_id] = {
        "messages": [],
        "context": "general",
        "mode": "assistant"
    }
    
    try:
        # Test message asking Eva to generate an image and email it
        test_message = "Generate an image of a green circle and email it as an attachment to louisrdup@gmail.com with the subject 'Complete Image Generation Test'"
        
        print(f"📤 Sending message to Eva: '{test_message}'")
        
        response = await get_agent_response(session_id, test_message)
        
        print(f"📨 Eva's response:")
        print(response)
        
        # Check if images were generated
        import glob
        latest_images = glob.glob("/home/ldp/eva/media/eva/generated_*.png")
        if latest_images:
            latest_image = max(latest_images, key=os.path.getctime)
            print(f"📁 Latest generated image: {latest_image}")
            print(f"📊 Image size: {os.path.getsize(latest_image)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Eva: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🔧 Testing EVA complete image generation and email workflow")
    print("=" * 70)
    
    success = await test_eva_complete_workflow()
    
    print("=" * 70)
    if success:
        print("✅ Test completed - check your email for the attached image!")
    else:
        print("❌ Test failed")

if __name__ == "__main__":
    asyncio.run(main())