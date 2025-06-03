#!/usr/bin/env python3
"""
Test the conversation revival system
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.conversation_revival import ConversationRevival

async def test_conversation_revival():
    """Test the conversation revival system functionality"""
    print("🧠 Testing Conversation Revival System...")
    
    # Initialize the system
    revival = ConversationRevival()
    
    # Test 1: Analyze some interesting conversations
    print("\n1️⃣ Testing memory analysis...")
    
    # Simulate some interesting conversations
    test_conversations = [
        {
            "user": "haha that bug was driving me crazy but we finally fixed it!",
            "eva": "I know right! That was a brilliant solution with the Zep integration. The look on your face when it worked was priceless!",
            "session": "test_session_1"
        },
        {
            "user": "can you help me debug this python script?",
            "eva": "Sure! Let me take a look at the error. It looks like a simple syntax issue.",
            "session": "test_session_2"
        },
        {
            "user": "you're being really witty today blondi",
            "eva": "Why thank you! I'm feeling particularly clever today. Must be all that coffee... wait, I don't drink coffee 😄",
            "session": "test_session_3"
        },
        {
            "user": "i feel really tired today",
            "eva": "That sounds rough. Maybe take a break and get some rest when you can.",
            "session": "test_session_4"
        }
    ]
    
    # Analyze conversations
    for conv in test_conversations:
        memory = await revival.analyze_conversation_for_memories(
            conv["user"], conv["eva"], conv["session"]
        )
        if memory:
            print(f"✅ Saved memory with weight {memory.emotional_weight:.2f}: {memory.topic_tags}")
        else:
            print(f"❌ Conversation not interesting enough to save")
    
    # Test 2: Check memory stats
    print("\n2️⃣ Testing memory stats...")
    stats = revival.get_memory_stats()
    print(f"Stats: {stats}")
    
    # Test 3: Test revival triggers
    print("\n3️⃣ Testing revival triggers...")
    
    test_messages = [
        "let's debug another script",
        "haha that's funny", 
        "i'm working on python again",
        "feeling much better now"
    ]
    
    for msg in test_messages:
        should_revive = await revival.should_revive_memory(msg, session_history_length=5)
        print(f"Message: '{msg}' -> Should revive: {should_revive}")
    
    # Test 4: Generate revival prompts
    print("\n4️⃣ Testing revival prompt generation...")
    
    for msg in test_messages:
        memory = revival.get_revival_memory(msg)
        if memory:
            prompt = revival.generate_revival_prompt(memory)
            print(f"Message: '{msg}'")
            print(f"Revival: '{prompt}'")
            print()
    
    # Test 5: Test cleanup
    print("\n5️⃣ Testing memory cleanup...")
    await revival.cleanup_old_memories(max_memories=2)
    final_stats = revival.get_memory_stats()
    print(f"After cleanup: {final_stats}")
    
    print("\n✅ Conversation revival system test completed!")

if __name__ == "__main__":
    asyncio.run(test_conversation_revival())