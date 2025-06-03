"""
Appointment Booking Handler for Eva Agent
Uses ElevenLabs Conversational AI + Twilio for phone calls
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
import asyncio
from urllib.parse import urlencode

from integrations.tool_manager import ToolResponse

logger = logging.getLogger(__name__)


class AppointmentBookingHandler:
    """Handles appointment booking via phone calls using ElevenLabs Conversational AI"""
    
    def __init__(self):
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID") 
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        self.base_url = "https://api.elevenlabs.io/v1"
        self.conversational_ai_url = f"{self.base_url}/convai"
        
        # Default appointment types and scenarios
        self.appointment_templates = {
            "doctor": {
                "greeting": "Hi, I'm calling on behalf of {user_name} to schedule a doctor's appointment.",
                "purpose": "medical appointment",
                "typical_duration": "30 minutes",
                "preferred_times": ["morning", "afternoon"],
                "information_needed": ["insurance", "reason for visit", "preferred doctor"]
            },
            "dentist": {
                "greeting": "Hello, I'm calling for {user_name} to book a dental appointment.",
                "purpose": "dental appointment", 
                "typical_duration": "60 minutes",
                "preferred_times": ["morning", "afternoon"],
                "information_needed": ["insurance", "cleaning or specific issue", "preferred dentist"]
            },
            "haircut": {
                "greeting": "Hi there! I'm calling to schedule a haircut appointment for {user_name}.",
                "purpose": "haircut appointment",
                "typical_duration": "45 minutes", 
                "preferred_times": ["any time"],
                "information_needed": ["preferred stylist", "service type"]
            },
            "general": {
                "greeting": "Hello, I'm calling on behalf of {user_name} to schedule an appointment.",
                "purpose": "appointment",
                "typical_duration": "30-60 minutes",
                "preferred_times": ["flexible"],
                "information_needed": ["appointment type", "duration"]
            }
        }
    
    async def create_conversational_agent(self, appointment_details: Dict[str, Any]) -> str:
        """Create a specialized conversational AI agent for appointment booking"""
        
        appointment_type = appointment_details.get("type", "general").lower()
        template = self.appointment_templates.get(appointment_type, self.appointment_templates["general"])
        
        user_name = appointment_details.get("user_name", "my client")
        business_name = appointment_details.get("business_name", "your office")
        preferred_dates = appointment_details.get("preferred_dates", [])
        preferred_times = appointment_details.get("preferred_times", [])
        special_requests = appointment_details.get("special_requests", "")
        
        # Build the agent persona and instructions
        agent_prompt = f"""
You are Eva, a professional and friendly AI assistant making an appointment booking call on behalf of {user_name}.

GREETING: {template["greeting"].format(user_name=user_name)}

YOUR ROLE:
- You are calling {business_name} to schedule a {template["purpose"]}
- Be polite, professional, and efficient
- Speak naturally like a human assistant would

APPOINTMENT DETAILS TO SECURE:
- Date and time for the appointment
- Duration: approximately {template["typical_duration"]}
- Type: {template["purpose"]}

PREFERRED SCHEDULING:
- Dates: {', '.join(preferred_dates) if preferred_dates else 'flexible with dates'}
- Times: {', '.join(preferred_times) if preferred_times else 'flexible with timing'}
- Special requests: {special_requests if special_requests else 'none'}

INFORMATION TO PROVIDE IF ASKED:
- Client name: {user_name}
- Contact information: Will be provided if requested
- Reason for appointment: {appointment_details.get('reason', 'routine appointment')}

CONVERSATION FLOW:
1. Start with the greeting
2. Explain you're calling to schedule an appointment  
3. Provide preferred dates/times when asked
4. Answer any questions about the appointment
5. Confirm the final appointment details
6. Get any specific instructions or requirements
7. Thank them and end the call professionally

IMPORTANT GUIDELINES:
- If they can't accommodate preferred times, ask for available alternatives
- Always confirm the final appointment time and date clearly
- If they need to call back, politely provide contact information
- If they're closed or can't help, ask for the best time to call back
- Stay focused on the appointment booking goal
- Be patient and understanding if they need to check availability

CONVERSATION STYLE:
- Speak clearly and at a normal pace
- Use natural pauses and conversational flow
- Be friendly but professional
- Don't rush through the information
- Listen carefully to their responses and adapt accordingly

Remember: You represent {user_name} professionally. Make a great impression!
"""

        headers = {
            "xi-api-key": self.elevenlabs_api_key,
            "Content-Type": "application/json"
        }
        
        # Create conversational AI agent
        agent_data = {
            "name": f"Appointment Booking Agent for {user_name}",
            "prompt": agent_prompt,
            "voice_id": appointment_details.get("voice_id", "pNInz6obpgDQGcFmaJgB"),  # Default professional voice
            "model_id": "eleven_turbo_v2_5",
            "language": "en",
            "max_duration_seconds": 300,  # 5 minute max call
            "response_delay": 600,  # Slight delay for natural flow
            "interruption_threshold": 100,
            "stability": 0.8,
            "similarity_boost": 0.8,
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 800
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.conversational_ai_url}/agents.create",
                headers=headers,
                json=agent_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                agent_info = response.json()
                return agent_info["agent_id"]
            else:
                raise Exception(f"Failed to create conversational agent: {response.status_code} - {response.text}")
    
    async def make_appointment_call(self, agent_id: str, phone_number: str, appointment_details: Dict[str, Any]) -> Dict[str, Any]:
        """Initiate a phone call using the conversational AI agent"""
        
        headers = {
            "xi-api-key": self.elevenlabs_api_key,
            "Content-Type": "application/json"
        }
        
        # Prepare call data
        call_data = {
            "agent_id": agent_id,
            "customer_phone_number": phone_number,
            "webhook_url": f"{os.getenv('EVA_BASE_URL', 'http://localhost:8000')}/webhooks/elevenlabs/call-status"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.conversational_ai_url}/calls",
                headers=headers,
                json=call_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                call_info = response.json()
                return {
                    "call_id": call_info["call_id"],
                    "status": "initiated",
                    "message": f"Appointment booking call initiated to {phone_number}"
                }
            else:
                raise Exception(f"Failed to initiate call: {response.status_code} - {response.text}")
    
    async def handle_call(self, action: str, parameters: Dict[str, Any]) -> ToolResponse:
        """Handle appointment booking tool calls"""
        try:
            if not self.elevenlabs_api_key:
                return ToolResponse(
                    success=False,
                    result=None,
                    error="ElevenLabs API key not configured. Set ELEVENLABS_API_KEY environment variable."
                )
            
            if action == "book_appointment":
                # Extract appointment details
                business_name = parameters.get("business_name", "")
                business_phone = parameters.get("business_phone", "")
                appointment_type = parameters.get("appointment_type", "general")
                user_name = parameters.get("user_name", "my client")
                preferred_dates = parameters.get("preferred_dates", [])
                preferred_times = parameters.get("preferred_times", [])
                reason = parameters.get("reason", "")
                special_requests = parameters.get("special_requests", "")
                
                if not business_phone:
                    return ToolResponse(
                        success=False,
                        result=None,
                        error="Business phone number is required for appointment booking"
                    )
                
                # Prepare appointment details
                appointment_details = {
                    "type": appointment_type,
                    "user_name": user_name,
                    "business_name": business_name,
                    "preferred_dates": preferred_dates,
                    "preferred_times": preferred_times,
                    "reason": reason,
                    "special_requests": special_requests
                }
                
                # Create conversational AI agent
                agent_id = await self.create_conversational_agent(appointment_details)
                
                # Initiate the call
                call_result = await self.make_appointment_call(agent_id, business_phone, appointment_details)
                
                return ToolResponse(
                    success=True,
                    result={
                        "call_id": call_result["call_id"],
                        "agent_id": agent_id,
                        "status": "call_initiated",
                        "business_name": business_name,
                        "business_phone": business_phone,
                        "appointment_type": appointment_type,
                        "message": f"I'm now calling {business_name} at {business_phone} to book your {appointment_type} appointment!"
                    }
                )
                
            elif action == "check_call_status":
                # Check the status of a previous call
                call_id = parameters.get("call_id")
                
                if not call_id:
                    return ToolResponse(
                        success=False,
                        result=None,
                        error="Call ID required to check status"
                    )
                
                headers = {
                    "xi-api-key": self.elevenlabs_api_key
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.conversational_ai_url}/calls/{call_id}",
                        headers=headers,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        call_info = response.json()
                        return ToolResponse(
                            success=True,
                            result=call_info
                        )
                    else:
                        return ToolResponse(
                            success=False,
                            result=None,
                            error=f"Failed to get call status: {response.status_code}"
                        )
                        
            elif action == "list_available_voices":
                # Get available voices for appointment calls
                headers = {
                    "xi-api-key": self.elevenlabs_api_key
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/voices",
                        headers=headers,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        voices_data = response.json()
                        # Filter for professional voices
                        professional_voices = [
                            {
                                "voice_id": voice["voice_id"],
                                "name": voice["name"],
                                "description": voice.get("description", ""),
                                "preview_url": voice.get("preview_url", "")
                            }
                            for voice in voices_data["voices"]
                            if any(word in voice["name"].lower() for word in ["professional", "business", "clear", "friendly"])
                        ]
                        
                        return ToolResponse(
                            success=True,
                            result={
                                "professional_voices": professional_voices,
                                "total_voices": len(voices_data["voices"])
                            }
                        )
                    else:
                        return ToolResponse(
                            success=False,
                            result=None,
                            error=f"Failed to get voices: {response.status_code}"
                        )
            
            else:
                return ToolResponse(
                    success=False,
                    result=None,
                    error=f"Unknown appointment booking action: {action}"
                )
                
        except Exception as e:
            logger.error(f"Appointment booking handler error: {e}")
            return ToolResponse(success=False, result=None, error=str(e))