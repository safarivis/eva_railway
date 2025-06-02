"""
Tool Manager for Eva - Orchestrates tool calls to external agents
Provides a unified interface for Eva to call various tools and agents
"""
import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from pydantic import BaseModel, Field
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class ToolType(Enum):
    """Types of tools Eva can call"""
    EMAIL = "email"
    FILE = "file"
    WEB_SEARCH = "web_search"
    CODE = "code"
    MUSIC = "music"
    CALENDAR = "calendar"
    DATABASE = "database"
    API = "api"


class ToolCall(BaseModel):
    """Represents a tool call request"""
    tool: str
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    

class ToolResponse(BaseModel):
    """Represents a tool call response"""
    success: bool
    result: Any
    error: Optional[str] = None
    

class EmailToolHandler:
    """Handles email operations using Resend for sending and Gmail for other operations"""
    
    def __init__(self):
        self.resend_api_key = os.getenv("RESEND_API_KEY")
        self.gmail_service_url = os.getenv("GMAIL_SERVICE_URL", "http://localhost:3000")
        
    async def handle_call(self, action: str, parameters: Dict[str, Any]) -> ToolResponse:
        """Handle email actions using Resend only"""
        try:
            if action == "send":
                # Use Resend for sending emails
                return await self._send_with_resend(parameters)
            else:
                return ToolResponse(
                    success=False,
                    result=None,
                    error=f"Email action '{action}' not supported. Only 'send' is available via Resend."
                )
                
        except Exception as e:
            logger.error(f"Email tool error: {e}")
            return ToolResponse(success=False, result=None, error=str(e))
            
    async def _send_with_resend(self, params: Dict[str, Any]) -> ToolResponse:
        """Send email using Resend API"""
        try:
            import resend
            resend.api_key = self.resend_api_key
            
            # Ensure 'to' is always a list for Resend
            to_recipients = params.get("to", [])
            if isinstance(to_recipients, str):
                to_recipients = [to_recipients]
            
            email_params = {
                "from": params.get("from", "Eva Agent <onboarding@resend.dev>"),  # Use Resend's verified domain
                "to": to_recipients,
                "subject": params.get("subject", ""),
                "html": params.get("html", params.get("body", "")),
                "text": params.get("text", params.get("body", "")),
            }
            
            if params.get("cc"):
                email_params["cc"] = params["cc"]
            if params.get("bcc"):
                email_params["bcc"] = params["bcc"]
                
            result = resend.Emails.send(email_params)
            
            return ToolResponse(
                success=True,
                result={
                    "message_id": result.get("id"),
                    "status": "sent",
                    "to": to_recipients,
                    "subject": email_params["subject"]
                }
            )
            
        except Exception as e:
            logger.error(f"Resend email send failed: {e}")
            return ToolResponse(
                success=False,
                result=None,
                error=f"Failed to send email via Resend: {str(e)}"
            )
            


class FileToolHandler:
    """Handles file system operations with security"""
    
    def __init__(self):
        self.allowed_paths = [os.getcwd()]
        
    async def handle_call(self, action: str, parameters: Dict[str, Any]) -> ToolResponse:
        """Handle file operations"""
        try:
            path = parameters.get("path", "")
            
            # Security check
            if not self._is_path_allowed(path):
                return ToolResponse(
                    success=False,
                    result=None,
                    error=f"Access denied to path: {path}"
                )
                
            if action == "read":
                with open(path, 'r') as f:
                    content = f.read()
                return ToolResponse(success=True, result={"content": content})
                
            elif action == "write":
                content = parameters.get("content", "")
                with open(path, 'w') as f:
                    f.write(content)
                return ToolResponse(success=True, result={"message": f"File written: {path}"})
                
            elif action == "list":
                files = os.listdir(path)
                return ToolResponse(success=True, result={"files": files})
                
            else:
                return ToolResponse(
                    success=False,
                    result=None,
                    error=f"Unknown file action: {action}"
                )
                
        except Exception as e:
            logger.error(f"File tool error: {e}")
            return ToolResponse(success=False, result=None, error=str(e))
            
    def _is_path_allowed(self, path: str) -> bool:
        """Check if path is within allowed directories"""
        abs_path = os.path.abspath(path)
        return any(abs_path.startswith(os.path.abspath(allowed)) 
                  for allowed in self.allowed_paths)


class WebSearchToolHandler:
    """Handles web search operations"""
    
    async def handle_call(self, action: str, parameters: Dict[str, Any]) -> ToolResponse:
        """Handle web search"""
        try:
            if action == "search":
                query = parameters.get("query", "")
                # Placeholder - would integrate with actual search API
                return ToolResponse(
                    success=True,
                    result={
                        "query": query,
                        "results": [
                            {"title": "Result 1", "url": "https://example.com", "snippet": "..."},
                            {"title": "Result 2", "url": "https://example.com", "snippet": "..."}
                        ]
                    }
                )
            else:
                return ToolResponse(
                    success=False,
                    result=None,
                    error=f"Unknown search action: {action}"
                )
                
        except Exception as e:
            logger.error(f"Search tool error: {e}")
            return ToolResponse(success=False, result=None, error=str(e))


class ToolManager:
    """
    Main tool manager for Eva - orchestrates all tool calls
    This is what Eva uses to make tool calls based on user requests
    """
    
    def __init__(self):
        self.handlers: Dict[str, Any] = {
            ToolType.EMAIL.value: EmailToolHandler(),
            ToolType.FILE.value: FileToolHandler(),
            ToolType.WEB_SEARCH.value: WebSearchToolHandler(),
        }
        
        # Tool descriptions for Eva to understand what each tool does
        self.tool_descriptions = {
            ToolType.EMAIL.value: {
                "description": "Send emails using Resend API",
                "actions": {
                    "send": "Send an email using Resend API"
                }
            },
            ToolType.FILE.value: {
                "description": "File system operations",
                "actions": {
                    "read": "Read file contents",
                    "write": "Write to a file",
                    "list": "List directory contents"
                }
            },
            ToolType.WEB_SEARCH.value: {
                "description": "Search the web",
                "actions": {
                    "search": "Search for information online"
                }
            }
        }
        
    async def call_tool(self, tool_call: ToolCall) -> ToolResponse:
        """Execute a tool call"""
        handler = self.handlers.get(tool_call.tool)
        
        if not handler:
            return ToolResponse(
                success=False,
                result=None,
                error=f"Unknown tool: {tool_call.tool}"
            )
            
        return await handler.handle_call(tool_call.action, tool_call.parameters)
        
    async def process_natural_language_request(self, request: str) -> Dict[str, Any]:
        """
        Process a natural language request and determine which tool(s) to call
        This is where Eva's intelligence maps user requests to tool calls
        """
        # This would use Eva's LLM to parse the request and determine tool calls
        # For now, showing the structure:
        
        # Example mappings:
        if "email" in request.lower():
            if "send" in request.lower():
                return {
                    "tool_calls": [
                        ToolCall(
                            tool=ToolType.EMAIL.value,
                            action="send",
                            parameters={
                                # Parameters would be extracted from the request
                            }
                        )
                    ]
                }
            elif "inbox" in request.lower() or "list" in request.lower():
                return {
                    "tool_calls": [
                        ToolCall(
                            tool=ToolType.EMAIL.value,
                            action="list",
                            parameters={"limit": 10}
                        )
                    ]
                }
                
        return {"tool_calls": []}
        
    def get_tool_schema(self) -> Dict[str, Any]:
        """Get schema of available tools for LLM to understand"""
        tools = []
        
        # Email tool with specific schemas per action
        tools.append({
            "type": "function",
            "function": {
                "name": "email_tool",
                "description": "Send emails using Resend API",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["send"],
                            "description": "The action to perform"
                        },
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "to": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of recipient email addresses"
                                },
                                "subject": {
                                    "type": "string",
                                    "description": "Email subject line"
                                },
                                "body": {
                                    "type": "string",
                                    "description": "Email body content"
                                }
                            },
                            "required": ["to", "subject", "body"],
                            "description": "Email parameters"
                        }
                    },
                    "required": ["action", "parameters"]
                }
            }
        })
        
        # Other tools
        for tool_type, desc in self.tool_descriptions.items():
            if tool_type != ToolType.EMAIL.value:
                tools.append({
                    "type": "function", 
                    "function": {
                        "name": f"{tool_type}_tool",
                        "description": desc["description"],
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string",
                                    "enum": list(desc["actions"].keys()),
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
        
        return {"tools": tools}
        
    async def execute_multiple_tools(self, tool_calls: List[ToolCall]) -> List[ToolResponse]:
        """Execute multiple tool calls in parallel"""
        tasks = [self.call_tool(tc) for tc in tool_calls]
        return await asyncio.gather(*tasks)


# Singleton instance
_tool_manager = None

def get_tool_manager() -> ToolManager:
    """Get the singleton ToolManager instance"""
    global _tool_manager
    if _tool_manager is None:
        _tool_manager = ToolManager()
    return _tool_manager