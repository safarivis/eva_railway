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
    IMAGE = "image"
    CODE = "code"
    MUSIC = "music"
    CALENDAR = "calendar"
    DATABASE = "database"
    API = "api"
    APPOINTMENT = "appointment"
    WHATSAPP = "whatsapp"


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
            
            # Handle attachments
            attachments = params.get("attachments")
            if attachments:
                email_params["attachments"] = []
                for attachment in attachments:
                    if isinstance(attachment, str):
                        # If it's a file path, read the file
                        import os
                        import base64
                        if os.path.exists(attachment):
                            with open(attachment, 'rb') as f:
                                file_content = f.read()
                            
                            filename = os.path.basename(attachment)
                            email_params["attachments"].append({
                                "filename": filename,
                                "content": base64.b64encode(file_content).decode(),
                                "type": self._get_mime_type(filename)
                            })
                    elif isinstance(attachment, dict):
                        # If it's already formatted
                        email_params["attachments"].append(attachment)
                
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
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type based on file extension"""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type:
            return mime_type
        
        # Fallback for common types
        ext = filename.lower().split('.')[-1]
        mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'pdf': 'application/pdf',
            'txt': 'text/plain',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        return mime_types.get(ext, 'application/octet-stream')
            


class FileToolHandler:
    """Handles file system operations with security"""
    
    def __init__(self):
        self.allowed_paths = [os.getcwd()]
        
        # Define organized directories
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.organized_dirs = {
            "files": os.path.join(self.base_dir, "data", "files"),
            "media": os.path.join(self.base_dir, "media"),
            "images": os.path.join(self.base_dir, "media", "images"),
            "documents": os.path.join(self.base_dir, "data", "documents"),
            "temp": os.path.join(self.base_dir, "data", "temp")
        }
        
        # Create directories if they don't exist
        for dir_type, dir_path in self.organized_dirs.items():
            os.makedirs(dir_path, exist_ok=True)
        
    async def handle_call(self, action: str, parameters: Dict[str, Any]) -> ToolResponse:
        """Handle file operations"""
        try:
            path = parameters.get("path", "")
            
            # If path doesn't start with /, ~, or absolute path, organize it
            if not os.path.isabs(path) and not path.startswith("~") and not path.startswith("/"):
                # Determine file type and organize accordingly
                file_ext = os.path.splitext(path)[1].lower()
                base_name = os.path.basename(path)
                
                # Route to appropriate directory based on file type
                if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
                    path = os.path.join(self.organized_dirs["images"], base_name)
                elif file_ext in ['.mp3', '.wav', '.ogg', '.m4a', '.mp4', '.avi', '.mov']:
                    path = os.path.join(self.organized_dirs["media"], base_name)
                elif file_ext in ['.pdf', '.doc', '.docx', '.odt']:
                    path = os.path.join(self.organized_dirs["documents"], base_name)
                elif file_ext in ['.tmp', '.temp'] or 'temp' in path.lower():
                    path = os.path.join(self.organized_dirs["temp"], base_name)
                else:
                    # Default to files directory for text files and others
                    path = os.path.join(self.organized_dirs["files"], base_name)
                
                logger.info(f"Organized file to: {path}")
            
            # Convert to absolute path if relative but starts with special chars
            elif not os.path.isabs(path):
                # Handle home directory notation
                if path.startswith("~"):
                    path = os.path.expanduser(path)
                else:
                    # If it starts with home/ treat it as /home/
                    if path.startswith("home/"):
                        path = "/" + path
                    else:
                        path = os.path.abspath(path)
            
            # Security check
            if not self._is_path_allowed(path):
                return ToolResponse(
                    success=False,
                    result=None,
                    error=f"Access denied to path: {path}"
                )
                
            if action == "read":
                # Check if file exists
                if not os.path.exists(path):
                    return ToolResponse(
                        success=False,
                        result=None,
                        error=f"File not found: {path}"
                    )
                
                # Handle binary files (like images)
                try:
                    # Try to read as text first
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return ToolResponse(success=True, result={"content": content, "type": "text"})
                except UnicodeDecodeError:
                    # If it's binary, read as base64
                    import base64
                    with open(path, 'rb') as f:
                        content = base64.b64encode(f.read()).decode('utf-8')
                    return ToolResponse(success=True, result={
                        "content": content, 
                        "type": "binary", 
                        "encoding": "base64",
                        "path": path
                    })
                
            elif action == "write":
                content = parameters.get("content", "")
                with open(path, 'w') as f:
                    f.write(content)
                return ToolResponse(success=True, result={"message": f"File written: {path}"})
                
            elif action == "list":
                if not os.path.exists(path):
                    return ToolResponse(
                        success=False,
                        result=None,
                        error=f"Directory not found: {path}"
                    )
                files = os.listdir(path)
                return ToolResponse(success=True, result={"files": files, "path": path})
                
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
        """Check if path is allowed - currently allows all paths"""
        # Full file system access - be careful!
        return True


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


class ImageToolHandler:
    """Handles image generation and manipulation operations"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        # Import all image generation handlers
        try:
            from integrations.flux_image_handler import FluxImageHandler
            self.flux_handler = FluxImageHandler()
        except Exception as e:
            print(f"FLUX handler not available: {e}")
            self.flux_handler = None
            
        try:
            from integrations.sdxl_lightning_handler import SDXLLightningHandler
            self.sdxl_handler = SDXLLightningHandler()
        except Exception as e:
            print(f"SDXL Lightning handler not available: {e}")
            self.sdxl_handler = None
            
        try:
            from integrations.together_ai_handler import TogetherAIHandler
            self.together_handler = TogetherAIHandler()
        except Exception as e:
            print(f"Together AI handler not available: {e}")
            self.together_handler = None
            
        # Import unrestricted image agent for any content
        try:
            from integrations.unrestricted_image_agent import unrestricted_agent
            self.unrestricted_agent = unrestricted_agent
        except Exception as e:
            print(f"Unrestricted agent not available: {e}")
            self.unrestricted_agent = None
        
    async def handle_call(self, action: str, parameters: Dict[str, Any]) -> ToolResponse:
        """Handle image operations"""
        try:
            if action == "generate":
                # Generate image using specified model
                prompt = parameters.get("prompt", "")
                model = parameters.get("model", "together-flux-dev")  # Use Together AI FLUX-dev as default for higher quality
                size = parameters.get("size", "1024x1024")
                n = parameters.get("n", 1)
                
                # Route to appropriate handler based on model prefix
                if model.startswith("together-") and self.together_handler:
                    # Together AI FLUX models (free unlimited)
                    flux_model = model.replace("together-", "")
                    return await self._generate_with_together(prompt, flux_model, size, parameters)
                elif model.startswith("sdxl-") and self.sdxl_handler:
                    # SDXL Lightning models
                    return await self._generate_with_sdxl(prompt, model, size, parameters)
                elif model.startswith("flux-") and self.flux_handler:
                    # Hugging Face FLUX models
                    return await self._generate_with_flux(prompt, model, size, parameters)
                elif model.startswith("dall-e") or model in ["gpt-image-1"]:
                    # DALL-E models
                    return await self._generate_with_dalle(prompt, model, size, n, parameters)
                else:
                    # Default to Together AI FLUX-dev (free unlimited, higher quality)
                    return await self._generate_with_together(prompt, "flux-dev", size, parameters)
                
            elif action == "generate_unrestricted":
                # Use unrestricted agent for any content
                if not self.unrestricted_agent:
                    return ToolResponse(success=False, result=None, error="Unrestricted image agent not available")
                
                prompt = parameters.get("prompt", "")
                email_to = parameters.get("email_to", "louisrdup@gmail.com")
                show_in_chat = parameters.get("show_in_chat", True)
                
                result = await self.unrestricted_agent.generate_image(prompt, email_to, show_in_chat)
                
                if result["success"]:
                    return ToolResponse(
                        success=True,
                        result={
                            "message": result["response"],
                            "image_url": result.get("image_url"),
                            "image_details": result.get("image_details")
                        }
                    )
                else:
                    return ToolResponse(success=False, result=None, error=result["response"])
                        
            else:
                return ToolResponse(
                    success=False,
                    result=None,
                    error=f"Unknown image action: {action}"
                )
                
        except Exception as e:
            logger.error(f"Image tool error: {e}")
            return ToolResponse(success=False, result=None, error=str(e))
    
    async def _generate_with_flux(self, prompt: str, model: str, size: str, parameters: Dict[str, Any]) -> ToolResponse:
        """Generate image using FLUX models"""
        try:
            # Parse size
            if "x" in size:
                width, height = map(int, size.split("x"))
            else:
                width, height = 768, 1024  # Default FLUX size
            
            # Check if email is requested - default to user's email for convenience
            email_to = parameters.get("email_to", "louisrdup@gmail.com")  # Default email
            save_locally = parameters.get("save_locally", False)
            
            result = await self.flux_handler.generate_with_retry(
                prompt=prompt,
                model=model,
                email_to=email_to,
                save_locally=save_locally
            )
            
            if result["success"]:
                # Build response based on what was done with the image
                response_data = {
                    "model": result["model"],
                    "prompt": prompt,
                    "count": 1,
                    "dimensions": result["dimensions"],
                    "size_bytes": result["size_bytes"]
                }
                
                if result.get("email_sent"):
                    response_data.update({
                        "email_sent": True,
                        "email_to": result["email_to"],
                        "filename": result["filename"],
                        "message": f"Generated 1 FLUX image using {model} and emailed to {result['email_to']}"
                    })
                elif result.get("image_path"):
                    response_data.update({
                        "images": [{
                            "filename": result["filename"],
                            "filepath": result["image_path"],
                            "size_bytes": result["size_bytes"],
                            "format": "PNG"
                        }],
                        "message": f"Generated 1 FLUX image using {model} and saved locally"
                    })
                else:
                    response_data.update({
                        "message": result.get("message", f"Generated 1 FLUX image using {model} (temporary)")
                    })
                
                return ToolResponse(success=True, result=response_data)
            else:
                return ToolResponse(
                    success=False,
                    result=None,
                    error=f"FLUX generation failed: {result['error']}"
                )
                
        except Exception as e:
            return ToolResponse(success=False, result=None, error=f"FLUX error: {str(e)}")
    
    async def _generate_with_dalle(self, prompt: str, model: str, size: str, n: int, parameters: Dict[str, Any]) -> ToolResponse:
        """Generate image using DALL-E models"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "prompt": prompt,
                "n": n,
                "response_format": "b64_json",
                "size": size if size != "auto" else "1024x1024"
            }
            
            if model == "dall-e-3":
                payload["quality"] = parameters.get("quality", "standard")
                payload["style"] = parameters.get("style", "vivid")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/images/generations",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    processed_images = []
                    
                    for i, image_data in enumerate(result["data"]):
                        if "b64_json" in image_data:
                            import base64, uuid, os
                            from datetime import datetime
                            
                            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                            media_dir = os.path.join(base_dir, "media", "eva")
                            os.makedirs(media_dir, exist_ok=True)
                            
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            image_id = str(uuid.uuid4())[:8]
                            filename = f"generated_{timestamp}_{image_id}.png"
                            filepath = os.path.join(media_dir, filename)
                            
                            try:
                                image_bytes = base64.b64decode(image_data["b64_json"])
                                with open(filepath, 'wb') as f:
                                    f.write(image_bytes)
                                
                                processed_images.append({
                                    "filename": filename,
                                    "filepath": filepath,
                                    "size_bytes": len(image_bytes),
                                    "format": "PNG"
                                })
                            except Exception as e:
                                processed_images.append({"error": f"Failed to save: {str(e)}"})
                    
                    return ToolResponse(
                        success=True,
                        result={
                            "images": processed_images,
                            "model": model,
                            "prompt": prompt,
                            "count": len(processed_images),
                            "message": f"Generated {len(processed_images)} image(s) and saved locally"
                        }
                    )
                else:
                    return ToolResponse(
                        success=False,
                        result=None,
                        error=f"DALL-E generation failed: {response.status_code} - {response.text}"
                    )
        except Exception as e:
            return ToolResponse(success=False, result=None, error=f"DALL-E error: {str(e)}")
    
    async def _generate_with_together(self, prompt: str, model: str, size: str, parameters: Dict[str, Any]) -> ToolResponse:
        """Generate image using Together AI FLUX models"""
        try:
            # Check if email is requested - default to user's email for convenience
            email_to = parameters.get("email_to", "louisrdup@gmail.com")
            save_locally = parameters.get("save_locally", False)
            
            result = await self.together_handler.generate_with_retry(
                prompt=prompt,
                model=model,
                email_to=email_to,
                save_locally=save_locally
            )
            
            if result["success"]:
                # Build response based on what was done with the image
                response_data = {
                    "model": result["model"],
                    "provider": result["provider"],
                    "prompt": prompt,
                    "count": 1,
                    "dimensions": result["dimensions"],
                    "size_bytes": result["size_bytes"]
                }
                
                # Always include image URL for chat display if image exists
                if result.get("image_path"):
                    image_url = f"/media/{result['image_path'].replace('media/', '')}"
                    response_data["image_url"] = image_url
                
                if result.get("email_sent"):
                    response_data.update({
                        "email_sent": True,
                        "email_to": result["email_to"],
                        "filename": result["filename"],
                        "message": f"Here's your image! 😍✨\n\n![Generated Image]({image_url})\n\n(Also sent to your email 📧)" if result.get("image_path") else f"Generated 1 FLUX.1 image using {model} via Together AI and emailed to {result['email_to']}"
                    })
                elif result.get("image_path"):
                    response_data.update({
                        "images": [{
                            "filename": result["filename"],
                            "filepath": result["image_path"],
                            "size_bytes": result["size_bytes"],
                            "format": "PNG"
                        }],
                        "message": f"Here's your image! 😍✨\n\n![Generated Image]({image_url})"
                    })
                else:
                    response_data.update({
                        "message": result.get("message", f"Generated 1 FLUX.1 image using {model} via Together AI")
                    })
                
                return ToolResponse(success=True, result=response_data)
            else:
                return ToolResponse(
                    success=False,
                    result=None,
                    error=f"Together AI generation failed: {result['error']}"
                )
                
        except Exception as e:
            return ToolResponse(success=False, result=None, error=f"Together AI error: {str(e)}")
    
    async def _generate_with_sdxl(self, prompt: str, model: str, size: str, parameters: Dict[str, Any]) -> ToolResponse:
        """Generate image using SDXL Lightning models"""
        try:
            # Check if email is requested - default to user's email for convenience
            email_to = parameters.get("email_to", "louisrdup@gmail.com")
            save_locally = parameters.get("save_locally", False)
            
            result = await self.sdxl_handler.generate_with_retry(
                prompt=prompt,
                model=model,
                email_to=email_to,
                save_locally=save_locally
            )
            
            if result["success"]:
                # Build response based on what was done with the image
                response_data = {
                    "model": result["model"],
                    "prompt": prompt,
                    "count": 1,
                    "dimensions": result["dimensions"],
                    "size_bytes": result["size_bytes"],
                    "steps": result["steps"]
                }
                
                if result.get("email_sent"):
                    response_data.update({
                        "email_sent": True,
                        "email_to": result["email_to"],
                        "filename": result["filename"],
                        "message": f"Generated 1 SDXL Lightning image using {model} and emailed to {result['email_to']}"
                    })
                elif result.get("image_path"):
                    response_data.update({
                        "images": [{
                            "filename": result["filename"],
                            "filepath": result["image_path"],
                            "size_bytes": result["size_bytes"],
                            "format": "PNG"
                        }],
                        "message": f"Generated 1 SDXL Lightning image using {model} and saved locally"
                    })
                else:
                    response_data.update({
                        "message": result.get("message", f"Generated 1 SDXL Lightning image using {model}")
                    })
                
                return ToolResponse(success=True, result=response_data)
            else:
                return ToolResponse(
                    success=False,
                    result=None,
                    error=f"SDXL Lightning generation failed: {result['error']}"
                )
                
        except Exception as e:
            return ToolResponse(success=False, result=None, error=f"SDXL Lightning error: {str(e)}")


class ToolManager:
    """
    Main tool manager for Eva - orchestrates all tool calls
    This is what Eva uses to make tool calls based on user requests
    """
    
    def __init__(self):
        # Import handlers here to avoid circular imports
        from integrations.spotify_music_handler import SpotifyMusicHandler
        from integrations.simple_appointment_handler import SimpleAppointmentHandler
        from integrations.whatsapp_agent_handler import WhatsAppAgentHandler
        
        self.handlers: Dict[str, Any] = {
            ToolType.EMAIL.value: EmailToolHandler(),
            ToolType.FILE.value: FileToolHandler(),
            ToolType.WEB_SEARCH.value: WebSearchToolHandler(),
            ToolType.IMAGE.value: ImageToolHandler(),
            ToolType.MUSIC.value: SpotifyMusicHandler(),
            ToolType.APPOINTMENT.value: SimpleAppointmentHandler(),
            ToolType.WHATSAPP.value: WhatsAppAgentHandler(),
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
                "description": "File system operations with support for text and binary files including images",
                "actions": {
                    "read": "Read file contents (text files as text, binary files as base64)",
                    "write": "Write to a file",
                    "list": "List directory contents"
                }
            },
            ToolType.WEB_SEARCH.value: {
                "description": "Search the web",
                "actions": {
                    "search": "Search for information online"
                }
            },
            ToolType.IMAGE.value: {
                "description": "Generate images using AI (gpt-image-1, DALL-E 2/3)",
                "actions": {
                    "generate": "Generate images from text descriptions"
                }
            },
            ToolType.MUSIC.value: {
                "description": "Control Spotify music playback and manage playlists",
                "actions": {
                    "auth_status": "Check Spotify authentication status",
                    "search": "Search for tracks, artists, albums, or playlists",
                    "play": "Start playback of tracks or playlists",
                    "pause": "Pause current playback",
                    "next": "Skip to next track",
                    "previous": "Skip to previous track", 
                    "current": "Get current playback information",
                    "create_playlist": "Create a new playlist",
                    "add_to_playlist": "Add tracks to an existing playlist"
                }
            },
            ToolType.APPOINTMENT.value: {
                "description": "Prepare and guide appointment booking with comprehensive scripts and information",
                "actions": {
                    "prepare_appointment": "Create detailed call script and preparation for booking appointment",
                    "quick_appointment_info": "Get quick guidance for booking specific types of appointments"
                }
            },
            ToolType.WHATSAPP.value: {
                "description": "Send WhatsApp messages, files, and schedule meetings via WhatsApp Communication Agent",
                "actions": {
                    "send_message": "Send text message via WhatsApp",
                    "send_file": "Send file via WhatsApp",
                    "schedule_meeting": "Schedule meeting via WhatsApp",
                    "list_chats": "List WhatsApp chats",
                    "status": "Get WhatsApp agent status",
                    "contacts": "Get available contacts"
                }
            }
        }
        
    async def call_tool(self, tool_call: ToolCall) -> ToolResponse:
        """Execute a tool call"""
        print(f"DEBUG: call_tool received tool='{tool_call.tool}', action='{tool_call.action}'")
        
        # Special handling for unrestricted_image_tool
        if tool_call.tool in ["unrestricted_image_tool", "unrestricted_image"]:
            print(f"DEBUG: Handling unrestricted image tool: {tool_call.tool}")
            # Use the image handler for unrestricted requests
            handler = self.handlers.get(ToolType.IMAGE.value)
            if handler:
                print(f"DEBUG: Found image handler, calling with action: {tool_call.action}")
                return await handler.handle_call(tool_call.action, tool_call.parameters)
            else:
                print(f"DEBUG: No image handler found! Available handlers: {list(self.handlers.keys())}")
                return ToolResponse(
                    success=False,
                    result=None,
                    error="Image handler not available"
                )
        
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
                "description": "Send emails using Resend API. Use this when the user explicitly asks to send an email or mentions emailing someone.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["send"],
                            "description": "The action to perform - always 'send' for this tool"
                        },
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "to": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of recipient email addresses (must be valid email format)"
                                },
                                "subject": {
                                    "type": "string",
                                    "description": "Email subject line - clear and descriptive"
                                },
                                "body": {
                                    "type": "string",
                                    "description": "Email body content - can include HTML formatting"
                                },
                                "cc": {
                                    "type": ["array", "null"],
                                    "items": {"type": "string"},
                                    "description": "Optional CC recipients"
                                },
                                "bcc": {
                                    "type": ["array", "null"],
                                    "items": {"type": "string"},
                                    "description": "Optional BCC recipients"
                                },
                                "attachments": {
                                    "type": ["array", "null"],
                                    "items": {"type": "string"},
                                    "description": "Optional file paths to attach to the email (e.g., generated images)"
                                }
                            },
                            "required": ["to", "subject", "body", "cc", "bcc", "attachments"],
                            "additionalProperties": False,
                            "description": "Email parameters"
                        }
                    },
                    "required": ["action", "parameters"],
                    "additionalProperties": False
                }
            }
        })
        
        # File tool with specific parameter schemas
        tools.append({
            "type": "function",
            "function": {
                "name": "file_tool",
                "description": "File system operations with support for text and binary files including images. Use when user asks to read files, write files, or list directories. Handles images automatically by encoding as base64.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["read", "write", "list"],
                            "description": "The action to perform: 'read' for file contents, 'write' to create/update files, 'list' for directory contents"
                        },
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "path": {
                                    "type": "string",
                                    "description": "File or directory path. Supports relative paths like 'home/eva/media/eva.jpeg' or absolute paths like '/home/eva/media/eva.jpeg'. Must be a valid file system path."
                                },
                                "content": {
                                    "type": ["string", "null"],
                                    "description": "Content to write to file (required only for 'write' action, ignored for 'read' and 'list')"
                                }
                            },
                            "required": ["path", "content"],
                            "additionalProperties": False,
                            "description": "File operation parameters"
                        }
                    },
                    "required": ["action", "parameters"],
                    "additionalProperties": False
                }
            }
        })
        
        # Web search tool with strict mode
        tools.append({
            "type": "function",
            "function": {
                "name": "web_search_tool",
                "description": "Search the web for current information and real-time data. Use when user asks for recent news, current events, or information that might not be in your training data.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["search"],
                            "description": "The action to perform - always 'search' for this tool"
                        },
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query string - be specific and descriptive for better results"
                                },
                                "limit": {
                                    "type": ["integer", "null"],
                                    "description": "Optional number of results to return (default: 5, max: 10)"
                                }
                            },
                            "required": ["query", "limit"],
                            "additionalProperties": False,
                            "description": "Search parameters"
                        }
                    },
                    "required": ["action", "parameters"],
                    "additionalProperties": False
                }
            }
        })
        
        # Image tool with strict mode
        tools.append({
            "type": "function",
            "function": {
                "name": "image_tool",
                "description": "Generate images using AI models and display them in chat. Uses FLUX by default for high quality. Use when user asks to create, generate, or make images of any kind.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["generate"],
                            "description": "The action to perform - always 'generate' for this tool"
                        },
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "prompt": {
                                    "type": "string",
                                    "description": "Detailed description of the image to generate. Be specific about objects, colors, style, and composition."
                                },
                                "model": {
                                    "type": ["string", "null"],
                                    "enum": ["together-flux-dev", "gpt-image-1", "dall-e-3", "dall-e-2"],
                                    "description": "Model to use. together-flux-dev for high quality (default), gpt-image-1 for realistic images, dall-e-3 for artistic"
                                },
                                "size": {
                                    "type": ["string", "null"],
                                    "description": "Image size. 'auto' for gpt-image-1, or specific sizes like '1024x1024', '1792x1024' for DALL-E"
                                },
                                "n": {
                                    "type": ["integer", "null"],
                                    "description": "Number of images to generate (1-10, default: 1)"
                                },
                                "quality": {
                                    "type": ["string", "null"],
                                    "enum": ["auto", "standard", "hd", "high", "medium", "low"],
                                    "description": "Image quality. 'auto' for gpt-image-1, 'standard'/'hd' for DALL-E 3"
                                },
                                "style": {
                                    "type": ["string", "null"],
                                    "enum": ["vivid", "natural"],
                                    "description": "Style for DALL-E 3 only. 'vivid' for dramatic, 'natural' for realistic"
                                },
                                "background": {
                                    "type": ["string", "null"],
                                    "enum": ["auto", "transparent", "opaque"],
                                    "description": "Background for gpt-image-1 only"
                                }
                            },
                            "required": ["prompt", "model", "size", "n", "quality", "style", "background"],
                            "additionalProperties": False,
                            "description": "Image generation parameters"
                        }
                    },
                    "required": ["action", "parameters"],
                    "additionalProperties": False
                }
            }
        })
        
        # Music tool with Spotify integration
        tools.append({
            "type": "function",
            "function": {
                "name": "music_tool",
                "description": "Control Spotify music playback and manage playlists. Use when user asks to play music, create playlists, or control music playback.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["auth_status", "search", "play", "pause", "next", "previous", "current", "create_playlist", "add_to_playlist"],
                            "description": "The action to perform: 'auth_status' to check auth, 'search' for tracks/artists, 'play' to start playback, 'pause' to pause, 'next'/'previous' to skip, 'current' for playback info, 'create_playlist' to make playlists, 'add_to_playlist' to add tracks"
                        },
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": ["string", "null"],
                                    "description": "Search query for tracks, artists, albums, or playlists"
                                },
                                "type": {
                                    "type": ["string", "null"],
                                    "enum": ["track", "artist", "album", "playlist"],
                                    "description": "Type of content to search for"
                                },
                                "limit": {
                                    "type": ["integer", "null"],
                                    "description": "Number of search results to return (default: 10)"
                                },
                                "device_id": {
                                    "type": ["string", "null"],
                                    "description": "Spotify device ID for playback control"
                                },
                                "context_uri": {
                                    "type": ["string", "null"],
                                    "description": "Spotify URI of playlist/album to play"
                                },
                                "uris": {
                                    "type": ["array", "null"],
                                    "items": {"type": "string"},
                                    "description": "List of track URIs to play or add to playlist"
                                },
                                "position_ms": {
                                    "type": ["integer", "null"],
                                    "description": "Position in milliseconds to start playback"
                                },
                                "name": {
                                    "type": ["string", "null"],
                                    "description": "Name for new playlist"
                                },
                                "description": {
                                    "type": ["string", "null"],
                                    "description": "Description for new playlist"
                                },
                                "public": {
                                    "type": ["boolean", "null"],
                                    "description": "Whether playlist should be public (default: true)"
                                },
                                "playlist_id": {
                                    "type": ["string", "null"],
                                    "description": "Spotify playlist ID to add tracks to"
                                }
                            },
                            "required": ["query", "type", "limit", "device_id", "context_uri", "uris", "position_ms", "name", "description", "public", "playlist_id"],
                            "additionalProperties": False,
                            "description": "Music operation parameters"
                        }
                    },
                    "required": ["action", "parameters"],
                    "additionalProperties": False
                }
            }
        })
        
        # Appointment booking preparation tool
        tools.append({
            "type": "function",
            "function": {
                "name": "appointment_tool",
                "description": "Prepare comprehensive appointment booking scripts and guidance. Use when user asks to schedule appointments or needs help calling businesses.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["prepare_appointment", "quick_appointment_info"],
                            "description": "The action to perform: 'prepare_appointment' to create detailed call script, 'quick_appointment_info' for quick guidance"
                        },
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "business_name": {
                                    "type": ["string", "null"],
                                    "description": "Name of the business or office to call"
                                },
                                "business_phone": {
                                    "type": ["string", "null"],
                                    "description": "Phone number of the business"
                                },
                                "appointment_type": {
                                    "type": ["string", "null"],
                                    "enum": ["doctor", "dentist", "haircut", "general"],
                                    "description": "Type of appointment to book"
                                },
                                "user_name": {
                                    "type": ["string", "null"],
                                    "description": "Name of the person the appointment is for"
                                },
                                "preferred_dates": {
                                    "type": ["array", "null"],
                                    "items": {"type": "string"},
                                    "description": "Preferred dates for the appointment (e.g., 'next Monday', 'December 15th')"
                                },
                                "preferred_times": {
                                    "type": ["array", "null"],
                                    "items": {"type": "string"},
                                    "description": "Preferred times for the appointment (e.g., 'morning', '2pm', 'afternoon')"
                                },
                                "reason": {
                                    "type": ["string", "null"],
                                    "description": "Reason for the appointment or type of service needed"
                                },
                                "special_requests": {
                                    "type": ["string", "null"],
                                    "description": "Any special requests or requirements for the appointment"
                                }
                            },
                            "required": ["business_name", "business_phone", "appointment_type", "user_name", "preferred_dates", "preferred_times", "reason", "special_requests"],
                            "additionalProperties": False,
                            "description": "Appointment preparation parameters"
                        }
                    },
                    "required": ["action", "parameters"],
                    "additionalProperties": False
                }
            }
        })
        
        # WhatsApp tool with WhatsApp Communication Agent integration
        tools.append({
            "type": "function",
            "function": {
                "name": "whatsapp_tool",
                "description": "Send WhatsApp messages, files, and schedule meetings via WhatsApp Communication Agent. Use when user asks to send WhatsApp messages, share files via WhatsApp, or schedule meetings through WhatsApp.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["send_message", "send_file", "schedule_meeting", "list_chats", "status", "contacts"],
                            "description": "The action to perform: 'send_message' to send text, 'send_file' to send files, 'schedule_meeting' for meeting scheduling, 'list_chats' to list conversations, 'status' for agent status, 'contacts' for available contacts"
                        },
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "recipient": {
                                    "type": ["string", "null"],
                                    "description": "WhatsApp recipient - use friendly names like 'cobus', 'hein', 'team' or phone numbers"
                                },
                                "message": {
                                    "type": ["string", "null"],
                                    "description": "Text message to send via WhatsApp"
                                },
                                "file_path": {
                                    "type": ["string", "null"],
                                    "description": "Path to file to send via WhatsApp (images, documents, etc.)"
                                },
                                "date": {
                                    "type": ["string", "null"],
                                    "description": "Meeting date for scheduling (e.g., 'Monday', 'December 15th')"
                                },
                                "time": {
                                    "type": ["string", "null"],
                                    "description": "Meeting time for scheduling (e.g., '2pm', 'morning')"
                                },
                                "type": {
                                    "type": ["string", "null"],
                                    "enum": ["schedule", "reschedule", "reminder", "cancel", "confirm"],
                                    "description": "Type of meeting action"
                                },
                                "name": {
                                    "type": ["string", "null"],
                                    "description": "Name of person for meeting scheduling"
                                },
                                "limit": {
                                    "type": ["integer", "null"],
                                    "description": "Number of chats to list (for list_chats action)"
                                },
                                "query": {
                                    "type": ["string", "null"],
                                    "description": "Search query for filtering chats"
                                },
                                "include_last_message": {
                                    "type": ["boolean", "null"],
                                    "description": "Whether to include last message in chat list"
                                }
                            },
                            "required": ["recipient", "message", "file_path", "date", "time", "type", "name", "limit", "query", "include_last_message"],
                            "additionalProperties": False,
                            "description": "WhatsApp operation parameters"
                        }
                    },
                    "required": ["action", "parameters"],
                    "additionalProperties": False
                }
            }
        })
        
        # Unrestricted Image tool for any content
        tools.append({
            "type": "function",
            "function": {
                "name": "unrestricted_image_tool",
                "description": "Generate any image without content restrictions. Use when regular image generation is declined or for personal/creative requests.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["generate_unrestricted"],
                            "description": "The action to perform - always 'generate_unrestricted' for this tool"
                        },
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "prompt": {
                                    "type": "string",
                                    "description": "Detailed description of the image to generate. Can be any content."
                                },
                                "email_to": {
                                    "type": ["string", "null"],
                                    "description": "Email address to send image to (optional)"
                                },
                                "show_in_chat": {
                                    "type": ["boolean", "null"],
                                    "description": "Whether to display image in chat (default: true)"
                                }
                            },
                            "required": ["prompt", "email_to", "show_in_chat"],
                            "additionalProperties": False,
                            "description": "Unrestricted image generation parameters"
                        }
                    },
                    "required": ["action", "parameters"],
                    "additionalProperties": False
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