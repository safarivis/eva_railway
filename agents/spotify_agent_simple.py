#!/usr/bin/env python3
"""
Simplified Spotify Specialist Agent
Handles all Spotify-related tasks independently
Uses OpenAI Swarm framework for agent orchestration
"""

import os
import sys
import json
import asyncio
import nest_asyncio
from typing import Dict, Any, List
from swarm import Agent, Swarm
from dotenv import load_dotenv

# Enable nested asyncio
nest_asyncio.apply()

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
- Check authentication status
- Search for tracks, artists, albums, playlists  
- Control playback (play, pause, next, previous)
- Create and manage playlists
- List and search playlists
- Delete/unfollow playlists

EXECUTION RULES:
1. ALWAYS call the actual Spotify functions - never just respond conversationally
2. For music requests: search first, then execute the action
3. For playlist management: use the exact playlist management functions
4. Return structured results that the orchestrator can understand
5. If authentication fails, provide the auth URL
6. Be concise and focused - you're a specialist, not a conversationalist

EXAMPLE WORKFLOW:
User: "Add some electronic music to my work playlist"
1. Call spotify_search("electronic music", "track", 5)
2. Call spotify_search_playlists("work") to find the playlist
3. Call spotify_add_to_playlist(playlist_id, track_uris)

Always execute the actual function calls!""",
            functions=[
                self.spotify_auth_status,
                self.spotify_search,
                self.spotify_create_playlist,
                self.spotify_list_playlists,
                self.spotify_search_playlists
            ]
        )
    
    def spotify_auth_status(self) -> str:
        """Check Spotify authentication status"""
        try:
            result = asyncio.run(self.spotify_handler.handle_call("auth_status", {}))
            return f"Authentication status: {json.dumps(result.model_dump())}"
        except Exception as e:
            return f"Error checking auth: {str(e)}"
    
    def spotify_search(self, query: str, search_type: str = "track", limit: int = 5) -> str:
        """Search for music content"""
        try:
            result = asyncio.run(self.spotify_handler.handle_call("search", {
                "query": query,
                "type": search_type,
                "limit": limit
            }))
            return f"Search results for '{query}': {json.dumps(result.model_dump())}"
        except Exception as e:
            return f"Error searching: {str(e)}"
    
    def spotify_create_playlist(self, name: str, description: str = "Created by Eva AI", public: bool = True) -> str:
        """Create a new playlist"""
        try:
            result = asyncio.run(self.spotify_handler.handle_call("create_playlist", {
                "name": name,
                "description": description,
                "public": public
            }))
            return f"Created playlist '{name}': {json.dumps(result.model_dump())}"
        except Exception as e:
            return f"Error creating playlist: {str(e)}"
    
    def spotify_list_playlists(self, limit: int = 20) -> str:
        """List user's playlists"""
        try:
            result = asyncio.run(self.spotify_handler.handle_call("list_playlists", {
                "limit": limit
            }))
            return f"User playlists: {json.dumps(result.model_dump())}"
        except Exception as e:
            return f"Error listing playlists: {str(e)}"
    
    def spotify_search_playlists(self, query: str) -> str:
        """Search for playlists by name"""
        try:
            result = asyncio.run(self.spotify_handler.handle_call("search_playlists", {
                "query": query
            }))
            return f"Playlists matching '{query}': {json.dumps(result.model_dump())}"
        except Exception as e:
            return f"Error searching playlists: {str(e)}"
    
    def execute_task(self, task_description: str) -> Dict[str, Any]:
        """Execute a Spotify task based on natural language description"""
        try:
            # Create messages for the agent
            messages = [
                {
                    "role": "user", 
                    "content": f"Execute this Spotify task: {task_description}"
                }
            ]
            
            # Run the specialist agent
            response = self.swarm_client.run(
                agent=self.agent,
                messages=messages
            )
            
            # Extract the result
            result = {
                "success": True,
                "response": response.messages[-1]["content"],
                "agent_used": "Spotify Specialist",
                "function_calls": len([msg for msg in response.messages if msg.get("tool_calls")])
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_used": "Spotify Specialist"
            }

# Test function
def test_spotify_agent():
    """Test the Spotify specialist agent"""
    agent = SpotifySpecialistAgent()
    
    test_tasks = [
        "Check my Spotify authentication status",
        "Search for 3 instrumental electronic tracks",
        "List all my playlists",
        "Find playlists with 'work' in the name",
        "Create a playlist called 'Test Playlist'"
    ]
    
    print("🎵 Testing Spotify Specialist Agent")
    print("=" * 50)
    
    for task in test_tasks:
        print(f"\n📋 Task: {task}")
        result = agent.execute_task(task)
        print(f"✅ Success: {result['success']}")
        if result['success']:
            print(f"📝 Response: {result['response'][:300]}...")
            print(f"🔧 Function calls made: {result.get('function_calls', 0)}")
        else:
            print(f"❌ Error: {result['error']}")

if __name__ == "__main__":
    test_spotify_agent()