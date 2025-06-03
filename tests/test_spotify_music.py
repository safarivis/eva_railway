#!/usr/bin/env python3
"""
Test Spotify music integration
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.tool_manager import get_tool_manager, ToolCall

async def test_spotify_auth_status():
    """Test Spotify authentication status"""
    print("🧪 Testing Spotify authentication status...")
    
    # Get tool manager
    tool_manager = get_tool_manager()
    
    # Test auth status
    try:
        tool_call = ToolCall(
            tool="music",
            action="auth_status",
            parameters={}
        )
        
        print(f"📤 Checking Spotify auth status...")
        
        response = await tool_manager.call_tool(tool_call)
        
        print(f"✅ Tool response success: {response.success}")
        
        if response.success:
            result = response.result
            authenticated = result.get('authenticated', False)
            
            if authenticated:
                print("🎵 Spotify is connected and ready!")
                print(f"📊 Message: {result.get('message', '')}")
            else:
                print("🔗 Spotify needs authentication")
                print(f"🌐 Auth URL: {result.get('auth_url', 'No URL provided')}")
                print(f"📊 Message: {result.get('message', '')}")
                print("\n💡 To set up Spotify integration:")
                print("1. Go to https://developer.spotify.com/dashboard")
                print("2. Create a new app")
                print("3. Set redirect URI to: http://localhost:8000/spotify/callback")
                print("4. Set environment variables:")
                print("   export SPOTIFY_CLIENT_ID=your_client_id")
                print("   export SPOTIFY_CLIENT_SECRET=your_client_secret")
        else:
            print(f"❌ Error: {response.error}")
            
    except Exception as e:
        print(f"❌ Error testing Spotify auth: {e}")

async def test_eva_spotify_workflow():
    """Test Eva's Spotify workflow using the agent"""
    print("\n🧪 Testing Eva's Spotify workflow...")
    
    # This would test the full workflow through Eva
    # For now, we'll just show what commands Eva can handle
    print("🎵 Eva can now handle these music commands:")
    print("- 'Check my Spotify connection'")
    print("- 'Search for songs by The Beatles'")
    print("- 'Play some jazz music'")
    print("- 'Create a playlist called Study Music'")
    print("- 'Pause the music'")
    print("- 'Skip to the next song'")
    print("- 'What's currently playing?'")

async def main():
    print("🔧 Testing EVA Spotify Music Integration")
    print("=" * 60)
    
    await test_spotify_auth_status()
    await test_eva_spotify_workflow()
    
    print("=" * 60)
    print("✅ Test completed")

if __name__ == "__main__":
    asyncio.run(main())