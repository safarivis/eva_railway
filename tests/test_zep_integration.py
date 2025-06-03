#!/usr/bin/env python3
"""Test script for Zep memory integration."""

import asyncio
import os
from dotenv import load_dotenv
import sys
sys.path.insert(0, '..')
from integrations.zep_memory import ZepMemoryManager

load_dotenv()

async def test_zep_integration():
    """Test basic Zep functionality."""
    api_key = os.getenv("ZEP_API_KEY")
    
    if not api_key or api_key == "your_zep_api_key_here":
        print("⚠️  Please set a valid ZEP_API_KEY in your .env file")
        print("   Get your API key from: https://app.getzep.com/")
        return
    
    print("🧪 Testing Zep Memory Integration...")
    
    try:
        # Initialize memory manager
        memory_manager = ZepMemoryManager(api_key=api_key)
        print("✅ Zep client initialized")
        
        # Test user creation
        test_user_id = "test_user_123"
        await memory_manager.create_or_get_user(
            test_user_id, 
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        print("✅ User created/retrieved")
        
        # Test session creation
        test_run_id = "test_run_123"
        session_id = await memory_manager.create_session(test_run_id, test_user_id)
        print(f"✅ Session created: {session_id}")
        
        # Test adding messages
        test_messages = [
            {"role": "user", "content": "Hello, I'm testing the Zep integration!"},
            {"role": "assistant", "content": "Great! I can now remember our conversations."}
        ]
        await memory_manager.add_messages(test_run_id, test_messages)
        print("✅ Messages added to memory")
        
        # Test retrieving memory context
        context = await memory_manager.get_memory_context(test_run_id)
        if context:
            print(f"✅ Memory context retrieved: {len(context)} characters")
        else:
            print("⚠️  No memory context retrieved (this is normal for first run)")
        
        # Test memory search
        search_results = await memory_manager.search_memory(test_run_id, "Zep integration")
        print(f"✅ Memory search completed: {len(search_results)} results")
        
        print("\n🎉 All tests passed! Zep integration is working correctly.")
        
        # Cleanup
        await memory_manager.close()
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure your ZEP_API_KEY is valid")
        print("2. Check your internet connection")
        print("3. Verify Zep service is accessible")

if __name__ == "__main__":
    asyncio.run(test_zep_integration())