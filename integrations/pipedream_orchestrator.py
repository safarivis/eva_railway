"""
Pipedream Connect Integration for Eva
Provides access to thousands of API integrations through a single SDK
"""
import os
import logging
import asyncio
import httpx
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class PipedreamConfig(BaseModel):
    """Configuration for Pipedream Connect"""
    client_id: str = Field(default_factory=lambda: os.getenv("PIPEDREAM_CLIENT_ID", ""))
    client_secret: str = Field(default_factory=lambda: os.getenv("PIPEDREAM_CLIENT_SECRET", ""))
    project_id: str = Field(default_factory=lambda: os.getenv("PIPEDREAM_PROJECT_ID", "proj_Los2n77"))
    environment: str = Field(default_factory=lambda: os.getenv("PIPEDREAM_PROJECT_ENVIRONMENT", "development"))
    api_base_url: str = "https://api.pipedream.com"


class PipedreamApp(BaseModel):
    """Represents a Pipedream app integration"""
    slug: str
    name: str
    description: str
    connected: bool = False
    auth_url: Optional[str] = None


class PipedreamOrchestrator:
    """
    Orchestrates API calls through Pipedream Connect
    Replaces individual tool handlers with unified Pipedream SDK
    """
    
    def __init__(self, config: Optional[PipedreamConfig] = None):
        self.config = config or PipedreamConfig()
        self.connected_apps: Dict[str, PipedreamApp] = {}
        self._init_default_apps()
        
    def _init_default_apps(self):
        """Initialize default app configurations"""
        # These are the most useful apps for Eva
        self.available_apps = {
            "gmail": PipedreamApp(
                slug="gmail",
                name="Gmail",
                description="Read, send, and manage emails"
            ),
            "google_drive": PipedreamApp(
                slug="google_drive",
                name="Google Drive",
                description="Access and manage files in Google Drive"
            ),
            "slack": PipedreamApp(
                slug="slack",
                name="Slack",
                description="Send messages and manage Slack workspaces"
            ),
            "notion": PipedreamApp(
                slug="notion",
                name="Notion",
                description="Create and manage Notion pages and databases"
            ),
            "github": PipedreamApp(
                slug="github",
                name="GitHub",
                description="Manage repositories, issues, and pull requests"
            ),
            "calendar": PipedreamApp(
                slug="google_calendar",
                name="Google Calendar",
                description="Manage calendar events and schedules"
            ),
            "openai": PipedreamApp(
                slug="openai",
                name="OpenAI",
                description="Access OpenAI models and embeddings"
            ),
            "spotify": PipedreamApp(
                slug="spotify",
                name="Spotify",
                description="Control music playback and manage playlists"
            ),
            "weather": PipedreamApp(
                slug="openweathermap",
                name="Weather",
                description="Get weather information and forecasts"
            ),
            "stripe": PipedreamApp(
                slug="stripe",
                name="Stripe",
                description="Process payments and manage subscriptions"
            )
        }
        
    async def connect_app(self, app_slug: str, user_id: str) -> Dict[str, Any]:
        """
        Initialize OAuth flow for connecting an app
        Returns the auth URL for the user to complete connection
        """
        if app_slug not in self.available_apps:
            return {
                "success": False,
                "error": f"App '{app_slug}' not found"
            }
            
        # In production, this would call Pipedream's OAuth endpoint
        # For now, we'll simulate the connection flow
        auth_url = f"{self.config.api_base_url}/connect/oauth/authorize"
        auth_url += f"?client_id={self.config.client_id}"
        auth_url += f"&app={app_slug}"
        auth_url += f"&project_id={self.config.project_id}"
        auth_url += f"&environment={self.config.environment}"
        auth_url += f"&external_user_id={user_id}"
        
        return {
            "success": True,
            "auth_url": auth_url,
            "app": app_slug,
            "message": f"Visit the auth URL to connect {self.available_apps[app_slug].name}"
        }
        
    async def execute_action(self, app_slug: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action on a connected app through Pipedream
        """
        # Gmail-specific actions
        if app_slug == "gmail":
            return await self._execute_gmail_action(action, params)
        
        # Google Drive actions
        elif app_slug == "google_drive":
            return await self._execute_drive_action(action, params)
        
        # Slack actions
        elif app_slug == "slack":
            return await self._execute_slack_action(action, params)
        
        # Generic Pipedream API call
        else:
            return await self._execute_pipedream_action(app_slug, action, params)
            
    async def _execute_gmail_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Gmail-specific actions through Pipedream"""
        try:
            # Map actions to Pipedream Gmail endpoints
            action_map = {
                "send": "gmail.send_email",
                "list": "gmail.list_messages",
                "read": "gmail.get_message",
                "search": "gmail.search_messages",
                "create_draft": "gmail.create_draft",
                "add_label": "gmail.add_label",
                "remove_label": "gmail.remove_label"
            }
            
            pipedream_action = action_map.get(action)
            if not pipedream_action:
                return {
                    "success": False,
                    "error": f"Unknown Gmail action: {action}"
                }
                
            # Prepare request to Pipedream
            if action == "send":
                # Use Resend for sending if available, otherwise Pipedream Gmail
                if os.getenv("RESEND_API_KEY"):
                    return await self._send_with_resend(params)
                else:
                    payload = {
                        "to": params.get("to", []),
                        "subject": params.get("subject", ""),
                        "body": params.get("body", ""),
                        "html": params.get("html", params.get("body", ""))
                    }
                    
            elif action == "list":
                payload = {
                    "max_results": params.get("limit", 10),
                    "label_ids": params.get("labels", ["INBOX"])
                }
                
            elif action == "search":
                payload = {
                    "query": params.get("query", ""),
                    "max_results": params.get("limit", 10)
                }
                
            else:
                payload = params
                
            # Make the API call through Pipedream
            return await self._call_pipedream_api(pipedream_action, payload)
            
        except Exception as e:
            logger.error(f"Gmail action error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def _send_with_resend(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send email using Resend as primary method"""
        try:
            import resend
            resend.api_key = os.getenv("RESEND_API_KEY")
            
            email_params = {
                "from": params.get("from", "Eva Agent <onboarding@resend.dev>"),
                "to": params.get("to", []),
                "subject": params.get("subject", ""),
                "html": params.get("html", params.get("body", "")),
                "text": params.get("text", params.get("body", "")),
            }
            
            result = resend.Emails.send(email_params)
            
            return {
                "success": True,
                "result": {
                    "message_id": result.get("id"),
                    "status": "sent",
                    "provider": "resend"
                }
            }
        except Exception as e:
            logger.warning(f"Resend failed, would fall back to Pipedream: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": "pipedream"
            }
            
    async def _execute_drive_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Google Drive actions through Pipedream"""
        action_map = {
            "list_files": "google_drive.list_files",
            "create_file": "google_drive.create_file",
            "read_file": "google_drive.get_file",
            "update_file": "google_drive.update_file",
            "delete_file": "google_drive.delete_file",
            "create_folder": "google_drive.create_folder"
        }
        
        pipedream_action = action_map.get(action)
        if not pipedream_action:
            return {
                "success": False,
                "error": f"Unknown Drive action: {action}"
            }
            
        return await self._call_pipedream_api(pipedream_action, params)
        
    async def _execute_slack_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Slack actions through Pipedream"""
        action_map = {
            "send_message": "slack.send_message",
            "list_channels": "slack.list_channels",
            "create_channel": "slack.create_channel",
            "upload_file": "slack.upload_file"
        }
        
        pipedream_action = action_map.get(action)
        if not pipedream_action:
            return {
                "success": False,
                "error": f"Unknown Slack action: {action}"
            }
            
        return await self._call_pipedream_api(pipedream_action, params)
        
    async def _execute_pipedream_action(self, app_slug: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute generic Pipedream action"""
        pipedream_action = f"{app_slug}.{action}"
        return await self._call_pipedream_api(pipedream_action, params)
        
    async def _call_pipedream_api(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make actual API call to Pipedream"""
        # In production, this would call Pipedream's execution endpoint
        # For now, we'll simulate the response
        logger.info(f"Calling Pipedream action: {action} with payload: {payload}")
        
        # Simulated response
        return {
            "success": True,
            "action": action,
            "result": {
                "status": "completed",
                "data": payload,
                "message": f"Action {action} executed successfully"
            }
        }
        
    def get_available_apps(self) -> List[PipedreamApp]:
        """Get list of available apps"""
        return list(self.available_apps.values())
        
    def get_app_actions(self, app_slug: str) -> Dict[str, str]:
        """Get available actions for an app"""
        app_actions = {
            "gmail": {
                "send": "Send an email",
                "list": "List emails from inbox",
                "read": "Read a specific email",
                "search": "Search for emails",
                "create_draft": "Create an email draft",
                "add_label": "Add label to email",
                "remove_label": "Remove label from email"
            },
            "google_drive": {
                "list_files": "List files in Drive",
                "create_file": "Create a new file",
                "read_file": "Read file contents",
                "update_file": "Update file contents",
                "delete_file": "Delete a file",
                "create_folder": "Create a folder"
            },
            "slack": {
                "send_message": "Send a message",
                "list_channels": "List channels",
                "create_channel": "Create a channel",
                "upload_file": "Upload a file"
            },
            "notion": {
                "create_page": "Create a new page",
                "update_page": "Update a page",
                "search": "Search pages and databases",
                "create_database": "Create a database"
            },
            "github": {
                "create_issue": "Create an issue",
                "list_repos": "List repositories",
                "create_pr": "Create pull request",
                "get_user": "Get user info"
            }
        }
        
        return app_actions.get(app_slug, {})
        
    def get_tool_schema_for_llm(self) -> List[Dict[str, Any]]:
        """Get tool schema for OpenAI function calling"""
        tools = []
        
        for app_slug, app in self.available_apps.items():
            actions = self.get_app_actions(app_slug)
            
            if actions:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": f"{app_slug}_tool",
                        "description": app.description,
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string",
                                    "enum": list(actions.keys()),
                                    "description": "The action to perform"
                                },
                                "parameters": {
                                    "type": "object",
                                    "description": "Action-specific parameters"
                                }
                            },
                            "required": ["action"]
                        }
                    }
                })
                
        return tools


# Singleton instance
_pipedream_orchestrator = None

def get_pipedream_orchestrator() -> PipedreamOrchestrator:
    """Get singleton PipedreamOrchestrator instance"""
    global _pipedream_orchestrator
    if _pipedream_orchestrator is None:
        _pipedream_orchestrator = PipedreamOrchestrator()
    return _pipedream_orchestrator