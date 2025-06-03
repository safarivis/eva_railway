#!/usr/bin/env python3
"""
Debug EVA's file tool and vision workflow
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.eva import get_agent_response
from core.eva import active_conversations

async def test_eva_file_workflow():
    """Test EVA's file tool workflow step by step"""
    print("🔍 Testing EVA's file tool workflow...")
    
    # Create test session
    session_id = "debug_file_workflow"
    active_conversations[session_id] = {
        "messages": [],
        "context": "general",
        "mode": "assistant"
    }
    
    print("\n1️⃣ Testing directory listing:")
    try:
        response1 = await get_agent_response(
            session_id, 
            "List the files in the /home/ldp/louisdup/agents/eva_agent/tests directory"
        )
        print(f"EVA Response 1: {response1}")
    except Exception as e:
        print(f"❌ Error in directory listing: {e}")
    
    print("\n2️⃣ Testing file reading:")
    try:
        response2 = await get_agent_response(
            session_id,
            "Read the file /home/ldp/louisdup/agents/eva_agent/README.md and show me the first 5 lines"
        )
        print(f"EVA Response 2: {response2}")
    except Exception as e:
        print(f"❌ Error in file reading: {e}")
    
    print("\n3️⃣ Testing file creation and reading back:")
    try:
        # Test creating a file
        response3 = await get_agent_response(
            session_id,
            "Create a file /tmp/eva_test.txt with the content 'Hello from EVA!'"
        )
        print(f"EVA Response 3: {response3}")
        
        # Read it back
        response4 = await get_agent_response(
            session_id,
            "Now read the file /tmp/eva_test.txt"
        )
        print(f"EVA Response 4: {response4}")
            
    except Exception as e:
        print(f"❌ Error in file creation test: {e}")
        import traceback
        traceback.print_exc()

async def main():
    print("🔧 Debugging EVA file tool and vision workflow")
    print("=" * 60)
    
    await test_eva_file_workflow()
    
    print("=" * 60)
    print("✅ Debug test completed")

if __name__ == "__main__":
    asyncio.run(main())