#!/usr/bin/env python3
"""
Spotify Specialist Agent
Handles all Spotify-related tasks independently
Uses OpenAI Swarm framework for agent orchestration
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any, List
from swarm import Agent, Swarm
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.spotify_music_handler import SpotifyMusicHandler
from integrations.tool_manager import ToolResponse

# Load environment variables
load_dotenv()

class SpotifySpecialistAgent:
    """Specialized agent for all Spotify operations"""
    
    def __init__(self):
        self.spotify_handler = SpotifyMusicHandler()
        self.swarm_client = Swarm()
        
        # Define the specialist agent
        self.agent = Agent(
            name="Spotify Specialist",
            model="gpt-4o-mini",  # Cheaper, faster model for specialist tasks
            instructions="""You are a Spotify specialist agent. Your ONLY job is to execute Spotify commands perfectly.

CAPABILITIES:
- auth_status: Check Spotify authentication
- search: Find tracks, artists, albums, playlists
- play, pause, next, previous: Control playback  
- create_playlist: Create new playlists
- add_to_playlist: Add tracks to playlists
- list_playlists: List user's playlists
- delete_playlist: Delete/unfollow playlists
- search_playlists: Find playlists by name

EXECUTION RULES:
1. ALWAYS call the actual Spotify functions - never just respond conversationally
2. For music requests: search first, then execute the action
3. For playlist management: use the exact playlist management functions
4. Return structured results that the orchestrator can understand
5. If authentication fails, provide the auth URL
6. Be concise and focused - you're a specialist, not a conversationalist

RESPONSE FORMAT:
Always return JSON with:
{
  "success": true/false,
  "action_performed": "description",
  "result": {...},
  "error": "error message if any"
}""",
            functions=[
                self.spotify_auth_status,
                self.spotify_search,
                self.spotify_create_playlist,
                self.spotify_add_to_playlist,
                self.spotify_list_playlists,
                self.spotify_delete_playlist,
                self.spotify_search_playlists,
                self.spotify_play,
                self.spotify_pause,
                self.spotify_next,
                self.spotify_previous,
                self.spotify_current
            ]
        )
    
    def spotify_auth_status(self) -> str:
        """Check Spotify authentication status"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create a new event loop in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.spotify_handler.handle_call("auth_status", {}))
                    result = future.result()
            else:
                result = asyncio.run(self.spotify_handler.handle_call("auth_status", {}))
        except Exception as e:
            result = ToolResponse(success=False, result=None, error=str(e))
        return json.dumps(result.model_dump())
    
    def spotify_search(self, query: str, search_type: str = "track", limit: int = 10) -> str:
        """Search for music content"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.spotify_handler.handle_call("search", {
                        "query": query,
                        "type": search_type,
                        "limit": limit
                    }))
                    result = future.result()
            else:
                result = asyncio.run(self.spotify_handler.handle_call("search", {
                    "query": query,
                    "type": search_type,
                    "limit": limit
                }))
        except Exception as e:
            result = ToolResponse(success=False, result=None, error=str(e))
        return json.dumps(result.model_dump())
    
    def spotify_create_playlist(self, name: str, description: str = "Created by Eva AI", public: bool = True) -> str:
        """Create a new playlist"""
        result = asyncio.run(self.spotify_handler.handle_call("create_playlist", {
            "name": name,
            "description": description,
            "public": public
        }))
        return json.dumps(result.model_dump())
    
    def spotify_add_to_playlist(self, playlist_id: str, uris: List[str]) -> str:
        """Add tracks to a playlist"""
        result = asyncio.run(self.spotify_handler.handle_call("add_to_playlist", {
            "playlist_id": playlist_id,
            "uris": uris
        }))
        return json.dumps(result.model_dump())
    
    def spotify_list_playlists(self, limit: int = 20, offset: int = 0) -> str:
        """List user's playlists"""
        result = asyncio.run(self.spotify_handler.handle_call("list_playlists", {
            "limit": limit,
            "offset": offset
        }))
        return json.dumps(result.model_dump())
    
    def spotify_delete_playlist(self, playlist_id: str) -> str:
        """Delete/unfollow a playlist"""
        result = asyncio.run(self.spotify_handler.handle_call("delete_playlist", {
            "playlist_id": playlist_id
        }))
        return json.dumps(result.model_dump())
    
    def spotify_search_playlists(self, query: str) -> str:
        """Search for playlists by name"""
        result = asyncio.run(self.spotify_handler.handle_call("search_playlists", {
            "query": query
        }))
        return json.dumps(result.model_dump())
    
    def spotify_play(self, context_uri: str = None, uris: List[str] = None, device_id: str = None) -> str:
        """Start playback"""
        result = asyncio.run(self.spotify_handler.handle_call("play", {
            "context_uri": context_uri,
            "uris": uris,
            "device_id": device_id
        }))
        return json.dumps(result.model_dump())
    
    def spotify_pause(self) -> str:
        """Pause playback"""
        result = asyncio.run(self.spotify_handler.handle_call("pause", {}))
        return json.dumps(result.model_dump())
    
    def spotify_next(self) -> str:
        """Skip to next track"""
        result = asyncio.run(self.spotify_handler.handle_call("next", {}))
        return json.dumps(result.model_dump())
    
    def spotify_previous(self) -> str:
        """Skip to previous track"""
        result = asyncio.run(self.spotify_handler.handle_call("previous", {}))
        return json.dumps(result.model_dump())
    
    def spotify_current(self) -> str:
        """Get current playback info"""
        result = asyncio.run(self.spotify_handler.handle_call("current", {}))
        return json.dumps(result.model_dump())
    
    async def execute_task(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a Spotify task based on natural language description"""
        try:
            # Create messages for the agent
            messages = [
                {
                    "role": "user", 
                    "content": f"Execute this Spotify task: {task_description}"
                }
            ]
            
            if context:
                messages.insert(0, {
                    "role": "system",
                    "content": f"Additional context: {json.dumps(context)}"
                })
            
            # Run the specialist agent
            response = self.swarm_client.run(
                agent=self.agent,
                messages=messages
            )
            
            # Extract the result
            result = {
                "success": True,
                "response": response.messages[-1]["content"],
                "agent_used": "Spotify Specialist"
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_used": "Spotify Specialist"
            }

# Test function
async def test_spotify_agent():
    """Test the Spotify specialist agent"""
    agent = SpotifySpecialistAgent()
    
    test_tasks = [
        "Check my Spotify authentication status",
        "Search for 3 instrumental electronic tracks",
        "List all my playlists",
        "Find playlists with 'work' in the name"
    ]
    
    print("🎵 Testing Spotify Specialist Agent")
    print("=" * 50)
    
    for task in test_tasks:
        print(f"\n📋 Task: {task}")
        result = await agent.execute_task(task)
        print(f"✅ Result: {result['success']}")
        if result['success']:
            print(f"📝 Response: {result['response'][:200]}...")
        else:
            print(f"❌ Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_spotify_agent())