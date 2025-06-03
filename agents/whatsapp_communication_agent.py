#!/usr/bin/env python3
"""
WhatsApp Communication Agent
Separate agent that handles all WhatsApp operations via MCP
Can be called by Eva or other agents
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import subprocess

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app for agent API
app = FastAPI(title="WhatsApp Communication Agent", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    recipient: str
    message: str
    
class FileRequest(BaseModel):
    recipient: str
    file_path: str
    
class MeetingRequest(BaseModel):
    recipient: str
    date: str
    time: str
    name: Optional[str] = None
    type: str = "schedule"  # schedule, reschedule, reminder, cancel
    
class ChatListRequest(BaseModel):
    limit: int = 20
    query: Optional[str] = None
    include_last_message: bool = True

class WhatsAppCommunicationAgent:
    """Separate agent for all WhatsApp communication"""
    
    def __init__(self):
        self.mcp_server_path = "/home/ldp/louisdup/Clients/VelocityFibre/Agents/WhatsAppMonitor/whatsapp-mcp/whatsapp-mcp-server"
        self.bridge_path = "/home/ldp/louisdup/Clients/VelocityFibre/Agents/WhatsAppMonitor/whatsapp-mcp/whatsapp-bridge"
        
        # Contact mappings for easier usage
        self.contacts = {
            "cobus": "27824939462",
            "hein": "27123456789",  # Replace with actual
            "team": "120363417538730975@g.us",  # Replace with actual group JID
            "client_group": "group_jid_here@g.us",
            "velocity_team": "team_jid_here@g.us",
            "melanie": "contact_jid_here@s.whatsapp.net"
        }
        
        # Meeting message templates
        self.meeting_templates = {
            "schedule": "Hi {name}, are you available for a meeting on {date} at {time}? Please confirm.",
            "reschedule": "Hi {name}, can we reschedule our meeting to {new_date} at {new_time}?",
            "reminder": "Hi {name}, just a reminder about our meeting tomorrow at {time}.",
            "cancel": "Hi {name}, I need to cancel our meeting scheduled for {date}. Sorry for the inconvenience.",
            "confirm": "Hi {name}, confirming our meeting on {date} at {time}. Looking forward to it!"
        }
        
        self.bridge_running = False
        self.mcp_available = False
    
    def _get_recipient_info(self, recipient: str) -> tuple[str, str]:
        """Convert friendly names to phone numbers or JIDs"""
        if recipient.lower() in self.contacts:
            jid = self.contacts[recipient.lower()]
            return jid, recipient
        return recipient, recipient
    
    async def _check_bridge_status(self) -> bool:
        """Check if WhatsApp bridge is running"""
        try:
            # Check if bridge process is running
            result = subprocess.run(
                ["pgrep", "-f", "whatsapp-bridge"],
                capture_output=True,
                text=True
            )
            self.bridge_running = result.returncode == 0
            return self.bridge_running
        except Exception as e:
            logger.error(f"Error checking bridge status: {e}")
            return False
    
    async def _start_bridge(self) -> bool:
        """Start the WhatsApp bridge if not running"""
        try:
            if await self._check_bridge_status():
                logger.info("WhatsApp bridge already running")
                return True
            
            logger.info("Starting WhatsApp bridge...")
            # Start bridge in background
            process = subprocess.Popen(
                ["go", "run", "main.go"],
                cwd=self.bridge_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment for startup
            await asyncio.sleep(3)
            
            # Check if it started successfully
            if process.poll() is None:  # Still running
                self.bridge_running = True
                logger.info("WhatsApp bridge started successfully")
                return True
            else:
                logger.error("WhatsApp bridge failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Error starting bridge: {e}")
            return False
    
    async def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool via subprocess"""
        try:
            # Prepare command to call MCP tool
            cmd = [
                "/home/ldp/.local/bin/uv",
                "--directory", self.mcp_server_path,
                "run", "python", "-c",
                f"""
import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
import json

async def call_tool():
    server_params = StdioServerParameters(
        command="/home/ldp/.local/bin/uv",
        args=["--directory", "{self.mcp_server_path}", "run", "main.py"]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                result = await session.call_tool("{tool_name}", {json.dumps(arguments)})
                print(json.dumps(result))
    except Exception as e:
        print(json.dumps({{"error": str(e)}}))

asyncio.run(call_tool())
"""
            ]
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout.strip())
            else:
                raise Exception(f"MCP call failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"MCP tool call failed: {e}")
            raise
    
    async def send_message(self, recipient: str, message: str) -> Dict[str, Any]:
        """Send WhatsApp message"""
        try:
            # Ensure bridge is running
            if not await self._check_bridge_status():
                if not await self._start_bridge():
                    return {
                        "success": False,
                        "error": "WhatsApp bridge is not running and could not be started"
                    }
            
            # Get recipient info
            recipient_jid, display_name = self._get_recipient_info(recipient)
            
            # Call MCP tool
            result = await self._call_mcp_tool("send_message", {
                "recipient": recipient_jid,
                "message": message
            })
            
            return {
                "success": True,
                "message": f"WhatsApp message sent to {display_name}",
                "recipient": display_name,
                "sent_message": message,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Send message error: {e}")
            return {
                "success": False,
                "error": f"Failed to send WhatsApp message: {str(e)}"
            }
    
    async def send_file(self, recipient: str, file_path: str) -> Dict[str, Any]:
        """Send file via WhatsApp"""
        try:
            # Check file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            # Ensure bridge is running
            if not await self._check_bridge_status():
                if not await self._start_bridge():
                    return {
                        "success": False,
                        "error": "WhatsApp bridge is not running"
                    }
            
            # Get recipient info
            recipient_jid, display_name = self._get_recipient_info(recipient)
            
            # Call MCP tool
            result = await self._call_mcp_tool("send_file", {
                "recipient": recipient_jid,
                "media_path": file_path
            })
            
            return {
                "success": True,
                "message": f"File sent to {display_name} via WhatsApp",
                "recipient": display_name,
                "file": os.path.basename(file_path),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Send file error: {e}")
            return {
                "success": False,
                "error": f"Failed to send file: {str(e)}"
            }
    
    async def schedule_meeting(self, recipient: str, date: str, time: str, 
                             meeting_type: str = "schedule", name: Optional[str] = None) -> Dict[str, Any]:
        """Schedule a meeting via WhatsApp"""
        try:
            name = name or recipient
            
            # Generate appropriate message
            if meeting_type in self.meeting_templates:
                message = self.meeting_templates[meeting_type].format(
                    name=name,
                    date=date,
                    time=time,
                    new_date=date,  # For reschedule
                    new_time=time   # For reschedule
                )
            else:
                message = f"Hi {name}, meeting {meeting_type} for {date} at {time}."
            
            # Send the message
            result = await self.send_message(recipient, message)
            
            if result["success"]:
                result["meeting_type"] = meeting_type
                result["meeting_date"] = date
                result["meeting_time"] = time
            
            return result
            
        except Exception as e:
            logger.error(f"Schedule meeting error: {e}")
            return {
                "success": False,
                "error": f"Failed to schedule meeting: {str(e)}"
            }
    
    async def list_chats(self, limit: int = 20, query: Optional[str] = None) -> Dict[str, Any]:
        """List WhatsApp chats"""
        try:
            result = await self._call_mcp_tool("list_chats", {
                "limit": limit,
                "query": query or "",
                "include_last_message": True
            })
            
            return {
                "success": True,
                "chats": result,
                "count": len(result) if isinstance(result, list) else 0
            }
            
        except Exception as e:
            logger.error(f"List chats error: {e}")
            return {
                "success": False,
                "error": f"Failed to list chats: {str(e)}"
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get WhatsApp agent status"""
        bridge_status = await self._check_bridge_status()
        
        return {
            "success": True,
            "bridge_running": bridge_status,
            "mcp_available": True,  # Assume available if bridge is running
            "available_contacts": list(self.contacts.keys()),
            "agent_status": "running",
            "timestamp": datetime.now().isoformat()
        }

# Initialize agent
whatsapp_agent = WhatsAppCommunicationAgent()

# API Routes
@app.post("/send_message")
async def send_message(request: MessageRequest):
    """Send WhatsApp message"""
    result = await whatsapp_agent.send_message(request.recipient, request.message)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/send_file")
async def send_file(request: FileRequest):
    """Send file via WhatsApp"""
    result = await whatsapp_agent.send_file(request.recipient, request.file_path)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/schedule_meeting")
async def schedule_meeting(request: MeetingRequest):
    """Schedule meeting via WhatsApp"""
    result = await whatsapp_agent.schedule_meeting(
        request.recipient, 
        request.date, 
        request.time, 
        request.type,
        request.name
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/list_chats")
async def list_chats(request: ChatListRequest):
    """List WhatsApp chats"""
    result = await whatsapp_agent.list_chats(request.limit, request.query)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get("/status")
async def get_status():
    """Get agent status"""
    return await whatsapp_agent.get_status()

@app.get("/contacts")
async def get_contacts():
    """Get available contacts"""
    return {
        "success": True,
        "contacts": whatsapp_agent.contacts
    }

@app.get("/")
async def root():
    """Agent info"""
    return {
        "agent": "WhatsApp Communication Agent",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/send_message",
            "/send_file", 
            "/schedule_meeting",
            "/list_chats",
            "/status",
            "/contacts"
        ]
    }

if __name__ == "__main__":
    print("🚀 Starting WhatsApp Communication Agent...")
    print("📱 Agent will be available at http://localhost:8001")
    print("📋 Available endpoints:")
    print("   - POST /send_message")
    print("   - POST /send_file")
    print("   - POST /schedule_meeting")
    print("   - POST /list_chats")
    print("   - GET /status")
    print("   - GET /contacts")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)