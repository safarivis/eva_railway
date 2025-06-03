"""
Spotify Music Handler for Eva Agent
Handles Spotify Web API integration for playlist creation and playback control
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
import base64
from urllib.parse import urlencode

from integrations.tool_manager import ToolResponse

logger = logging.getLogger(__name__)


class SpotifyMusicHandler:
    """Handles Spotify API operations for music control"""
    
    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8000/spotify/callback")
        self.base_url = "https://api.spotify.com/v1"
        self.auth_url = "https://accounts.spotify.com/authorize"
        self.token_url = "https://accounts.spotify.com/api/token"
        
        # Token management
        self.access_token = None
        self.refresh_token = None
        self.token_expires = None
        
        # Load saved tokens if available
        self._load_tokens()
    
    def _load_tokens(self):
        """Load saved Spotify tokens from file"""
        token_file = "data/spotify_tokens.json"
        if os.path.exists(token_file):
            try:
                with open(token_file, 'r') as f:
                    data = json.load(f)
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")
                    expires_at = data.get("expires_at")
                    if expires_at:
                        self.token_expires = datetime.fromisoformat(expires_at)
            except Exception as e:
                logger.error(f"Failed to load Spotify tokens: {e}")
    
    def _save_tokens(self):
        """Save Spotify tokens to file"""
        token_file = "data/spotify_tokens.json"
        os.makedirs("data", exist_ok=True)
        try:
            with open(token_file, 'w') as f:
                json.dump({
                    "access_token": self.access_token,
                    "refresh_token": self.refresh_token,
                    "expires_at": self.token_expires.isoformat() if self.token_expires else None
                }, f)
        except Exception as e:
            logger.error(f"Failed to save Spotify tokens: {e}")
    
    def get_auth_url(self) -> str:
        """Generate Spotify authorization URL"""
        scopes = [
            "playlist-read-private",
            "playlist-read-collaborative", 
            "playlist-modify-public",
            "playlist-modify-private",
            "user-modify-playback-state",
            "user-read-playback-state",
            "user-read-currently-playing",
            "user-library-read",
            "user-library-modify"
        ]
        
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
            "show_dialog": "true"
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, headers=headers, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                self.refresh_token = token_data.get("refresh_token")
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires = datetime.now() + timedelta(seconds=expires_in)
                self._save_tokens()
                return token_data
            else:
                raise Exception(f"Token exchange failed: {response.text}")
    
    async def refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            return False
            
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, headers=headers, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires = datetime.now() + timedelta(seconds=expires_in)
                self._save_tokens()
                return True
            else:
                logger.error(f"Token refresh failed: {response.text}")
                return False
    
    async def ensure_valid_token(self) -> bool:
        """Ensure we have a valid access token"""
        if not self.access_token:
            return False
            
        if self.token_expires and datetime.now() >= self.token_expires:
            return await self.refresh_access_token()
            
        return True
    
    async def _api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated API request to Spotify"""
        if not await self.ensure_valid_token():
            raise Exception("No valid Spotify access token")
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code in [200, 201, 204]:
                return response.json() if response.text else {}
            else:
                raise Exception(f"Spotify API error: {response.status_code} - {response.text}")
    
    async def handle_call(self, action: str, parameters: Dict[str, Any]) -> ToolResponse:
        """Handle music tool calls"""
        try:
            if not self.client_id or not self.client_secret:
                return ToolResponse(
                    success=False,
                    result=None,
                    error="Spotify credentials not configured. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables."
                )
            
            if action == "auth_status":
                # Check authentication status
                has_token = self.access_token is not None
                is_valid = await self.ensure_valid_token() if has_token else False
                
                if not has_token:
                    auth_url = self.get_auth_url()
                    return ToolResponse(
                        success=True,
                        result={
                            "authenticated": False,
                            "auth_url": auth_url,
                            "message": f"Please authorize Eva with Spotify by visiting: {auth_url}"
                        }
                    )
                else:
                    return ToolResponse(
                        success=True,
                        result={
                            "authenticated": is_valid,
                            "message": "Spotify is connected and ready!" if is_valid else "Token expired, need to re-authenticate"
                        }
                    )
                    
            elif action == "search":
                # Search for music
                query = parameters.get("query")
                search_type = parameters.get("type", "track")  # track, artist, album, playlist
                limit = parameters.get("limit", 10)
                
                if not query:
                    return ToolResponse(success=False, result=None, error="Search query required")
                
                results = await self._api_request(
                    "GET", 
                    f"search?q={query}&type={search_type}&limit={limit}"
                )
                
                return ToolResponse(success=True, result=results)
                
            elif action == "play":
                # Control playback
                device_id = parameters.get("device_id")
                context_uri = parameters.get("context_uri")  # Spotify URI of playlist/album
                uris = parameters.get("uris")  # List of track URIs
                position_ms = parameters.get("position_ms", 0)
                
                data = {}
                if context_uri:
                    data["context_uri"] = context_uri
                if uris:
                    data["uris"] = uris
                if position_ms:
                    data["position_ms"] = position_ms
                    
                endpoint = "me/player/play"
                if device_id:
                    endpoint += f"?device_id={device_id}"
                    
                await self._api_request("PUT", endpoint, data)
                return ToolResponse(success=True, result={"message": "Playback started"})
                
            elif action == "pause":
                # Pause playback
                await self._api_request("PUT", "me/player/pause")
                return ToolResponse(success=True, result={"message": "Playback paused"})
                
            elif action == "next":
                # Skip to next track
                await self._api_request("POST", "me/player/next")
                return ToolResponse(success=True, result={"message": "Skipped to next track"})
                
            elif action == "previous":
                # Skip to previous track
                await self._api_request("POST", "me/player/previous")
                return ToolResponse(success=True, result={"message": "Skipped to previous track"})
                
            elif action == "current":
                # Get current playback info
                result = await self._api_request("GET", "me/player/currently-playing")
                return ToolResponse(success=True, result=result)
                
            elif action == "create_playlist":
                # Create a new playlist
                name = parameters.get("name", f"Eva's Playlist {datetime.now().strftime('%Y-%m-%d')}")
                description = parameters.get("description", "Created by Eva AI")
                public = parameters.get("public", True)
                
                # Get user ID first
                user_data = await self._api_request("GET", "me")
                user_id = user_data["id"]
                
                # Create playlist
                playlist_data = {
                    "name": name,
                    "description": description,
                    "public": public
                }
                
                result = await self._api_request(
                    "POST", 
                    f"users/{user_id}/playlists",
                    playlist_data
                )
                
                return ToolResponse(
                    success=True,
                    result={
                        "playlist_id": result["id"],
                        "playlist_url": result["external_urls"]["spotify"],
                        "message": f"Created playlist '{name}'"
                    }
                )
                
            elif action == "add_to_playlist":
                # Add tracks to playlist
                playlist_id = parameters.get("playlist_id")
                uris = parameters.get("uris")  # List of track URIs
                
                if not playlist_id or not uris:
                    return ToolResponse(
                        success=False,
                        result=None,
                        error="playlist_id and uris required"
                    )
                
                await self._api_request(
                    "POST",
                    f"playlists/{playlist_id}/tracks",
                    {"uris": uris}
                )
                
                return ToolResponse(
                    success=True,
                    result={"message": f"Added {len(uris)} tracks to playlist"}
                )
                
            elif action == "list_playlists":
                # List user's playlists
                limit = parameters.get("limit", 20)
                offset = parameters.get("offset", 0)
                
                result = await self._api_request(
                    "GET", 
                    f"me/playlists?limit={limit}&offset={offset}"
                )
                
                return ToolResponse(success=True, result=result)
                
            elif action == "delete_playlist":
                # Unfollow (delete) a playlist
                playlist_id = parameters.get("playlist_id")
                
                if not playlist_id:
                    return ToolResponse(
                        success=False,
                        result=None,
                        error="playlist_id required"
                    )
                
                # Use DELETE for unfollowing/deleting playlist
                await self._api_request(
                    "DELETE",
                    f"playlists/{playlist_id}/followers"
                )
                
                return ToolResponse(
                    success=True,
                    result={"message": f"Deleted playlist {playlist_id}"}
                )
                
            elif action == "search_playlists":
                # Search for playlists by name
                query = parameters.get("query")
                if not query:
                    return ToolResponse(
                        success=False,
                        result=None,
                        error="Search query required"
                    )
                
                # Get user's playlists and filter by name
                playlists_result = await self._api_request("GET", "me/playlists?limit=50")
                
                matching_playlists = []
                for playlist in playlists_result.get("items", []):
                    if query.lower() in playlist["name"].lower():
                        matching_playlists.append({
                            "id": playlist["id"],
                            "name": playlist["name"],
                            "url": playlist["external_urls"]["spotify"],
                            "tracks": playlist["tracks"]["total"]
                        })
                
                return ToolResponse(
                    success=True,
                    result={
                        "playlists": matching_playlists,
                        "total_found": len(matching_playlists)
                    }
                )
                
            else:
                return ToolResponse(
                    success=False,
                    result=None,
                    error=f"Unknown music action: {action}"
                )
                
        except Exception as e:
            logger.error(f"Spotify music handler error: {e}")
            return ToolResponse(success=False, result=None, error=str(e))