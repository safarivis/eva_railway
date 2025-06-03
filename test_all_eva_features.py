#!/usr/bin/env python3
"""
Complete test script for all Eva's new features
Run this to test everything at once
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.eva import get_agent_response

async def test_all_eva_features():
    """Test all Eva's new features comprehensively"""
    
    print("🚀 TESTING ALL EVA'S NEW FEATURES")
    print("=" * 60)
    
    # Create test session
    session_id = "comprehensive_test"
    
    test_commands = [
        # Music tests
        {
            "category": "🎵 MUSIC CONTROL",
            "tests": [
                "Check my Spotify connection",
                "What music features do you have?",
            ]
        },
        
        # Image generation tests
        {
            "category": "🖼️ IMAGE GENERATION", 
            "tests": [
                "Generate a simple image of a blue circle",
                "Create a picture of a mountain landscape",
            ]
        },
        
        # File operation tests
        {
            "category": "📁 FILE OPERATIONS",
            "tests": [
                "List the files in the current directory", 
                "Read the first 5 lines of README.md",
                "Create a file called eva_test.txt with content 'Eva is working great!'",
            ]
        },
        
        # Email tests  
        {
            "category": "📧 EMAIL FEATURES",
            "tests": [
                "What email capabilities do you have?",
            ]
        },
        
        # Appointment booking tests
        {
            "category": "📞 APPOINTMENT BOOKING",
            "tests": [
                "What should I know about booking a dentist appointment?",
                "Help me prepare to call and book a doctor's appointment",
            ]
        },
        
        # Advanced workflow tests
        {
            "category": "🔄 ADVANCED WORKFLOWS",
            "tests": [
                "Generate an image of a sunset and then tell me about the file you created",
                "List files in the media directory and describe what you find",
            ]
        }
    ]
    
    for category_data in test_commands:
        category = category_data["category"]
        tests = category_data["tests"]
        
        print(f"\n{category}")
        print("-" * 40)
        
        for i, test_command in enumerate(tests, 1):
            print(f"\n{i}. Testing: '{test_command}'")
            try:
                response = await get_agent_response(session_id, test_command)
                print(f"✅ Eva Response: {response[:200]}...")
                if len(response) > 200:
                    print("   [Response truncated for readability]")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Small delay between tests
            await asyncio.sleep(1)
    
    print("\n" + "=" * 60)
    print("🎉 COMPREHENSIVE TEST COMPLETED!")
    print("\n💡 To test more features manually:")
    print("   python eva_chat.py")
    print("   python eva_chat_tts.py  # With voice responses")

if __name__ == "__main__":
    asyncio.run(test_all_eva_features())