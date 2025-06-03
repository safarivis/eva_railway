"""
Email Manager Integration for Eva Agent
Provides email orchestration capabilities using multiple backends
"""
import asyncio
import json
import logging
from typing import List, Dict, Optional, Any
from enum import Enum
import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class EmailBackend(Enum):
    GMAIL_API = "gmail_api"
    EMAIL_GATEWAY = "email_gateway"
    MCP_GMAIL = "mcp_gmail"

class EmailMessage(BaseModel):
    id: str
    subject: str
    from_email: str
    to_email: List[str]
    body: str
    timestamp: str
    is_read: bool = False
    labels: List[str] = []

class EmailManager:
    """Orchestrates email operations across different email services"""
    
    def __init__(self, backend: EmailBackend = EmailBackend.EMAIL_GATEWAY):
        self.backend = backend
        self.email_gateway_url = "http://localhost:3000"  # Email gateway agent URL
        self.mcp_gmail_url = "http://localhost:8080"  # MCP Gmail service URL
        
    async def list_inbox(self, limit: int = 10) -> List[EmailMessage]:
        """List emails from inbox"""
        if self.backend == EmailBackend.EMAIL_GATEWAY:
            return await self._list_inbox_gateway(limit)
        elif self.backend == EmailBackend.GMAIL_API:
            return await self._list_inbox_gmail_api(limit)
        elif self.backend == EmailBackend.MCP_GMAIL:
            return await self._list_inbox_mcp(limit)
            
    async def send_email(self, to: List[str], subject: str, body: str, 
                        cc: List[str] = None, bcc: List[str] = None) -> Dict[str, Any]:
        """Send an email"""
        if self.backend == EmailBackend.EMAIL_GATEWAY:
            return await self._send_email_gateway(to, subject, body, cc, bcc)
        elif self.backend == EmailBackend.GMAIL_API:
            return await self._send_email_gmail_api(to, subject, body, cc, bcc)
        elif self.backend == EmailBackend.MCP_GMAIL:
            return await self._send_email_mcp(to, subject, body, cc, bcc)
            
    async def read_email(self, email_id: str) -> EmailMessage:
        """Read a specific email"""
        if self.backend == EmailBackend.EMAIL_GATEWAY:
            return await self._read_email_gateway(email_id)
        elif self.backend == EmailBackend.GMAIL_API:
            return await self._read_email_gmail_api(email_id)
        elif self.backend == EmailBackend.MCP_GMAIL:
            return await self._read_email_mcp(email_id)
            
    async def search_emails(self, query: str, limit: int = 10) -> List[EmailMessage]:
        """Search emails with query"""
        if self.backend == EmailBackend.EMAIL_GATEWAY:
            return await self._search_emails_gateway(query, limit)
        elif self.backend == EmailBackend.GMAIL_API:
            return await self._search_emails_gmail_api(query, limit)
        elif self.backend == EmailBackend.MCP_GMAIL:
            return await self._search_emails_mcp(query, limit)
            
    # Email Gateway Agent Implementation
    async def _list_inbox_gateway(self, limit: int) -> List[EmailMessage]:
        """List emails using email gateway agent"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.email_gateway_url}/api/emails",
                    params={"limit": limit}
                )
                response.raise_for_status()
                emails = response.json()
                return [EmailMessage(**email) for email in emails]
            except Exception as e:
                logger.error(f"Error listing emails via gateway: {e}")
                return []
                
    async def _send_email_gateway(self, to: List[str], subject: str, body: str,
                                 cc: List[str] = None, bcc: List[str] = None) -> Dict[str, Any]:
        """Send email using email gateway agent"""
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "to": to,
                    "subject": subject,
                    "body": body,
                    "cc": cc or [],
                    "bcc": bcc or []
                }
                response = await client.post(
                    f"{self.email_gateway_url}/api/send",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error sending email via gateway: {e}")
                return {"error": str(e)}
                
    async def _read_email_gateway(self, email_id: str) -> Optional[EmailMessage]:
        """Read email using email gateway agent"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.email_gateway_url}/api/emails/{email_id}"
                )
                response.raise_for_status()
                return EmailMessage(**response.json())
            except Exception as e:
                logger.error(f"Error reading email via gateway: {e}")
                return None
                
    async def _search_emails_gateway(self, query: str, limit: int) -> List[EmailMessage]:
        """Search emails using email gateway agent"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.email_gateway_url}/api/search",
                    params={"q": query, "limit": limit}
                )
                response.raise_for_status()
                emails = response.json()
                return [EmailMessage(**email) for email in emails]
            except Exception as e:
                logger.error(f"Error searching emails via gateway: {e}")
                return []
                
    # Gmail API Implementation (placeholder for direct integration)
    async def _list_inbox_gmail_api(self, limit: int) -> List[EmailMessage]:
        """List emails using Gmail API directly"""
        # TODO: Implement direct Gmail API integration
        logger.info("Gmail API direct integration not yet implemented")
        return []
        
    async def _send_email_gmail_api(self, to: List[str], subject: str, body: str,
                                   cc: List[str] = None, bcc: List[str] = None) -> Dict[str, Any]:
        """Send email using Gmail API directly"""
        # TODO: Implement direct Gmail API integration
        logger.info("Gmail API direct integration not yet implemented")
        return {"error": "Not implemented"}
        
    async def _read_email_gmail_api(self, email_id: str) -> Optional[EmailMessage]:
        """Read email using Gmail API directly"""
        # TODO: Implement direct Gmail API integration
        logger.info("Gmail API direct integration not yet implemented")
        return None
        
    async def _search_emails_gmail_api(self, query: str, limit: int) -> List[EmailMessage]:
        """Search emails using Gmail API directly"""
        # TODO: Implement direct Gmail API integration
        logger.info("Gmail API direct integration not yet implemented")
        return []
        
    # MCP Gmail Implementation
    async def _list_inbox_mcp(self, limit: int) -> List[EmailMessage]:
        """List emails using MCP Gmail service"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.mcp_gmail_url}/tools/gmail_list_messages",
                    json={"max_results": limit}
                )
                response.raise_for_status()
                messages = response.json().get("messages", [])
                return [self._parse_mcp_message(msg) for msg in messages]
            except Exception as e:
                logger.error(f"Error listing emails via MCP: {e}")
                return []
                
    async def _send_email_mcp(self, to: List[str], subject: str, body: str,
                             cc: List[str] = None, bcc: List[str] = None) -> Dict[str, Any]:
        """Send email using MCP Gmail service"""
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "to": ", ".join(to),
                    "subject": subject,
                    "body": body
                }
                if cc:
                    payload["cc"] = ", ".join(cc)
                if bcc:
                    payload["bcc"] = ", ".join(bcc)
                    
                response = await client.post(
                    f"{self.mcp_gmail_url}/tools/gmail_send_email",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error sending email via MCP: {e}")
                return {"error": str(e)}
                
    async def _read_email_mcp(self, email_id: str) -> Optional[EmailMessage]:
        """Read email using MCP Gmail service"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.mcp_gmail_url}/tools/gmail_get_message",
                    json={"message_id": email_id}
                )
                response.raise_for_status()
                return self._parse_mcp_message(response.json())
            except Exception as e:
                logger.error(f"Error reading email via MCP: {e}")
                return None
                
    async def _search_emails_mcp(self, query: str, limit: int) -> List[EmailMessage]:
        """Search emails using MCP Gmail service"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.mcp_gmail_url}/tools/gmail_search_messages",
                    json={"query": query, "max_results": limit}
                )
                response.raise_for_status()
                messages = response.json().get("messages", [])
                return [self._parse_mcp_message(msg) for msg in messages]
            except Exception as e:
                logger.error(f"Error searching emails via MCP: {e}")
                return []
                
    def _parse_mcp_message(self, mcp_message: Dict[str, Any]) -> EmailMessage:
        """Parse MCP message format to EmailMessage"""
        return EmailMessage(
            id=mcp_message.get("id", ""),
            subject=mcp_message.get("subject", ""),
            from_email=mcp_message.get("from", ""),
            to_email=mcp_message.get("to", "").split(", "),
            body=mcp_message.get("body", ""),
            timestamp=mcp_message.get("timestamp", ""),
            is_read=mcp_message.get("is_read", False),
            labels=mcp_message.get("labels", [])
        )


class EmailOrchestrator:
    """High-level email orchestration for Eva"""
    
    def __init__(self, email_manager: EmailManager):
        self.email_manager = email_manager
        
    async def process_email_request(self, intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process email-related requests from Eva"""
        try:
            if intent == "list_inbox":
                emails = await self.email_manager.list_inbox(
                    limit=params.get("limit", 10)
                )
                return {
                    "success": True,
                    "emails": [email.dict() for email in emails],
                    "count": len(emails)
                }
                
            elif intent == "send_email":
                result = await self.email_manager.send_email(
                    to=params.get("to", []),
                    subject=params.get("subject", ""),
                    body=params.get("body", ""),
                    cc=params.get("cc"),
                    bcc=params.get("bcc")
                )
                return {
                    "success": "error" not in result,
                    "result": result
                }
                
            elif intent == "read_email":
                email = await self.email_manager.read_email(
                    email_id=params.get("email_id")
                )
                return {
                    "success": email is not None,
                    "email": email.dict() if email else None
                }
                
            elif intent == "search_emails":
                emails = await self.email_manager.search_emails(
                    query=params.get("query", ""),
                    limit=params.get("limit", 10)
                )
                return {
                    "success": True,
                    "emails": [email.dict() for email in emails],
                    "count": len(emails)
                }
                
            else:
                return {
                    "success": False,
                    "error": f"Unknown email intent: {intent}"
                }
                
        except Exception as e:
            logger.error(f"Error processing email request: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def get_email_summary(self) -> str:
        """Get a summary of recent emails for context"""
        try:
            emails = await self.email_manager.list_inbox(limit=5)
            if not emails:
                return "No recent emails found."
                
            summary = "Recent emails:\n"
            for email in emails:
                read_status = "✓" if email.is_read else "•"
                summary += f"{read_status} From: {email.from_email} - {email.subject}\n"
                
            return summary
        except Exception as e:
            logger.error(f"Error getting email summary: {e}")
            return "Unable to retrieve email summary."