#!/usr/bin/env python3
"""
Test script for Eva's session persistence functionality.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.session_persistence import SessionPersistence
from datetime import datetime


async def test_session_persistence():
    """Test the session persistence functionality."""
    print("Testing Eva Session Persistence...")
    
    # Initialize persistence
    persistence = SessionPersistence(storage_dir="test_data/sessions")
    
    # Test 1: Save a session
    print("\n1. Testing session save...")
    test_session_id = "test_session_123"
    test_session_data = {
        "messages": [
            {"role": "user", "content": "Hello Eva!"},
            {"role": "assistant", "content": "Hello! How can I help you today?"},
            {"role": "user", "content": "Tell me about yourself"},
            {"role": "assistant", "content": "I'm Eva, your friendly AI companion!"}
        ],
        "context": "general",
        "mode": "friend",
        "base_user_id": "test_user",
        "created_at": datetime.now().isoformat()
    }
    
    persistence.save_session(test_session_id, test_session_data)
    print(f"✓ Saved session: {test_session_id}")
    
    # Test 2: Save Zep mapping
    print("\n2. Testing Zep mapping save...")
    test_zep_id = "zep_session_abc123"
    persistence.save_zep_mapping(test_session_id, test_zep_id)
    print(f"✓ Saved Zep mapping: {test_session_id} -> {test_zep_id}")
    
    # Test 3: Retrieve session
    print("\n3. Testing session retrieval...")
    retrieved_session = persistence.get_session(test_session_id)
    if retrieved_session:
        print(f"✓ Retrieved session with {len(retrieved_session.get('messages', []))} messages")
    else:
        print("✗ Failed to retrieve session")
    
    # Test 4: Get Zep mapping
    print("\n4. Testing Zep mapping retrieval...")
    retrieved_zep_id = persistence.get_zep_session_id(test_session_id)
    if retrieved_zep_id == test_zep_id:
        print(f"✓ Retrieved correct Zep mapping: {retrieved_zep_id}")
    else:
        print("✗ Failed to retrieve Zep mapping")
    
    # Test 5: Get user sessions
    print("\n5. Testing user session listing...")
    user_sessions = persistence.get_user_sessions("test_user")
    print(f"✓ Found {len(user_sessions)} sessions for test_user")
    for session in user_sessions:
        print(f"  - Session: {session['session_id']} ({session['context']}/{session['mode']})")
    
    # Test 6: Test persistence across restart
    print("\n6. Testing persistence across restart...")
    # Create new instance (simulating restart)
    new_persistence = SessionPersistence(storage_dir="test_data/sessions")
    
    # Check if data persists
    persisted_session = new_persistence.get_session(test_session_id)
    persisted_zep_id = new_persistence.get_zep_session_id(test_session_id)
    
    if persisted_session and persisted_zep_id == test_zep_id:
        print("✓ Data successfully persisted across restart!")
    else:
        print("✗ Data persistence failed")
    
    # Test 7: Large conversation history
    print("\n7. Testing large conversation history...")
    large_session_id = "large_session_456"
    large_messages = []
    for i in range(50):
        large_messages.extend([
            {"role": "user", "content": f"Question {i}"},
            {"role": "assistant", "content": f"Answer {i}"}
        ])
    
    large_session_data = {
        "messages": large_messages,
        "context": "work",
        "mode": "assistant",
        "base_user_id": "test_user",
        "created_at": datetime.now().isoformat()
    }
    
    persistence.save_session(large_session_id, large_session_data)
    retrieved_large = persistence.get_session(large_session_id)
    
    if retrieved_large and len(retrieved_large.get("messages", [])) == 100:
        print(f"✓ Successfully handled large conversation with {len(retrieved_large['messages'])} messages")
    else:
        print("✗ Failed to handle large conversation")
    
    # Test 8: Export user data
    print("\n8. Testing user data export...")
    export_path = persistence.export_user_data("test_user", "test_exports")
    if os.path.exists(export_path):
        print(f"✓ Successfully exported user data to: {export_path}")
    else:
        print("✗ Failed to export user data")
    
    print("\n✅ All tests completed!")
    
    # Cleanup test data
    import shutil
    if os.path.exists("test_data"):
        shutil.rmtree("test_data")
    if os.path.exists("test_exports"):
        shutil.rmtree("test_exports")
    print("\n🧹 Test data cleaned up")


if __name__ == "__main__":
    asyncio.run(test_session_persistence())