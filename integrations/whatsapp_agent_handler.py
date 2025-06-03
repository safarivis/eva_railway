#!/usr/bin/env python3
"""
WhatsApp Agent Handler for Eva
Connects Eva to the separate WhatsApp Communication Agent
"""

import httpx
import logging
from typing import Dict, Any
from integrations.tool_manager import ToolResponse

logger = logging.getLogger(__name__)

class WhatsAppAgentHandler:
    """Handles communication with WhatsApp Communication Agent"""
    
    def __init__(self):
        self.agent_url = "http://localhost:8001"
        
    async def handle_call(self, action: str, parameters: Dict[str, Any]) -> ToolResponse:
        """Handle WhatsApp tool calls by forwarding to WhatsApp agent"""
        try:
            if action == "send_message":
                return await self._send_message(parameters)
            elif action == "send_file":
                return await self._send_file(parameters)
            elif action == "schedule_meeting":
                return await self._schedule_meeting(parameters)
            elif action == "list_chats":
                return await self._list_chats(parameters)
            elif action == "status":
                return await self._get_status()
            elif action == "contacts":
                return await self._get_contacts()
            else:
                return ToolResponse(
                    success=False,
                    result=None,
                    error=f"Unknown WhatsApp action: {action}"
                )
        except Exception as e:
            logger.error(f"WhatsApp agent handler error: {e}")
            return ToolResponse(success=False, result=None, error=str(e))
    
    async def _send_message(self, parameters: Dict[str, Any]) -> ToolResponse:
        """Send WhatsApp message via agent"""
        recipient = parameters.get("recipient", "")
        message = parameters.get("message", "")
        
        if not recipient or not message:
            return ToolResponse(
                success=False,
                result=None,
                error="Both recipient and message are required"
            )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.agent_url}/send_message",
                    json={
                        "recipient": recipient,
                        "message": message
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return ToolResponse(success=True, result=result)
                else:
                    error_text = response.text
                    return ToolResponse(
                        success=False,
                        result=None,
                        error=f"WhatsApp agent error: {error_text}"
                    )
                    
        except Exception as e:
            return ToolResponse(
                success=False,
                result=None,
                error=f"Failed to communicate with WhatsApp agent: {str(e)}"
            )
    
    async def _send_file(self, parameters: Dict[str, Any]) -> ToolResponse:
        """Send file via WhatsApp agent"""
        recipient = parameters.get("recipient", "")
        file_path = parameters.get("file_path", "")
        
        if not recipient or not file_path:
            return ToolResponse(
                success=False,
                result=None,
                error="Both recipient and file_path are required"
            )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.agent_url}/send_file",
                    json={
                        "recipient": recipient,
                        "file_path": file_path
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return ToolResponse(success=True, result=result)
                else:
                    error_text = response.text
                    return ToolResponse(
                        success=False,
                        result=None,
                        error=f"WhatsApp agent error: {error_text}"
                    )
                    
        except Exception as e:
            return ToolResponse(
                success=False,
                result=None,
                error=f"Failed to send file via WhatsApp agent: {str(e)}"
            )
    
    async def _schedule_meeting(self, parameters: Dict[str, Any]) -> ToolResponse:
        """Schedule meeting via WhatsApp agent"""
        recipient = parameters.get("recipient", "")
        date = parameters.get("date", "")
        time = parameters.get("time", "")
        meeting_type = parameters.get("type", "schedule")
        name = parameters.get("name")
        
        if not recipient or not date or not time:
            return ToolResponse(
                success=False,
                result=None,
                error="Recipient, date, and time are required"
            )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.agent_url}/schedule_meeting",
                    json={
                        "recipient": recipient,
                        "date": date,
                        "time": time,
                        "type": meeting_type,
                        "name": name
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return ToolResponse(success=True, result=result)
                else:
                    error_text = response.text
                    return ToolResponse(
                        success=False,
                        result=None,
                        error=f"WhatsApp agent error: {error_text}"
                    )
                    
        except Exception as e:
            return ToolResponse(
                success=False,
                result=None,
                error=f"Failed to schedule meeting via WhatsApp: {str(e)}"
            )
    
    async def _list_chats(self, parameters: Dict[str, Any]) -> ToolResponse:
        """List chats via WhatsApp agent"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.agent_url}/list_chats",
                    json={
                        "limit": parameters.get("limit", 20),
                        "query": parameters.get("query"),
                        "include_last_message": parameters.get("include_last_message", True)
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return ToolResponse(success=True, result=result)
                else:
                    error_text = response.text
                    return ToolResponse(
                        success=False,
                        result=None,
                        error=f"WhatsApp agent error: {error_text}"
                    )
                    
        except Exception as e:
            return ToolResponse(
                success=False,
                result=None,
                error=f"Failed to list chats: {str(e)}"
            )
    
    async def _get_status(self) -> ToolResponse:
        """Get WhatsApp agent status"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.agent_url}/status",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return ToolResponse(success=True, result=result)
                else:
                    return ToolResponse(
                        success=False,
                        result=None,
                        error="WhatsApp agent not responding"
                    )
                    
        except Exception as e:
            return ToolResponse(
                success=False,
                result=None,
                error=f"WhatsApp agent not available: {str(e)}"
            )
    
    async def _get_contacts(self) -> ToolResponse:
        """Get available contacts from WhatsApp agent"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.agent_url}/contacts",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return ToolResponse(success=True, result=result)
                else:
                    return ToolResponse(
                        success=False,
                        result=None,
                        error="Could not get contacts from WhatsApp agent"
                    )
                    
        except Exception as e:
            return ToolResponse(
                success=False,
                result=None,
                error=f"Failed to get contacts: {str(e)}"
            )