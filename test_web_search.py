#!/usr/bin/env python3
"""
Test Eva's web search functionality
"""

import httpx
import json

def test_web_search():
    """Test web search with forced tool usage"""
    
    test_queries = [
        # Force tool usage
        {
            "message": "What's the latest news about OpenAI?",
            "tool_choice": "required"  # Force Eva to use tools
        },
        # Specific tool
        {
            "message": "Search the web for OpenAI announcements this week",
            "tool_choice": {"type": "function", "function": {"name": "web_search_tool"}}
        },
        # Let Eva decide but with strong prompt
        {
            "message": "Use the web_search tool to find current news about artificial intelligence",
            "tool_choice": "auto"
        }
    ]
    
    for test in test_queries:
        print(f"\n🔍 Testing: {test['message']}")
        print(f"   Tool choice: {test['tool_choice']}")
        
        try:
            response = httpx.post(
                "http://localhost:8000/api/chat-simple",
                json={
                    "message": test["message"],
                    "user_id": "test_user",
                    "tool_choice": test["tool_choice"]
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Response: {result.get('response', 'No response')[:200]}...")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        print("-" * 80)

if __name__ == "__main__":
    print("🧪 Testing Eva's Web Search Tool")
    print("=" * 80)
    test_web_search()
    print("\n💡 If web search isn't working, check the server logs for:")
    print("   - 'DEBUG: Forcing tool usage'")
    print("   - 'DEBUG: Calling tool web_search'")
    print("   - Any error messages")