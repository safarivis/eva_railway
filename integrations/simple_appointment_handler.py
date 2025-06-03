"""
Simple Appointment Booking Handler for Eva Agent
Uses existing ElevenLabs TTS + planning approach for appointment booking
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
import asyncio

from integrations.tool_manager import ToolResponse

logger = logging.getLogger(__name__)


class SimpleAppointmentHandler:
    """Handles appointment booking with intelligent planning and preparation"""
    
    def __init__(self):
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        
        # Appointment templates for different types
        self.appointment_templates = {
            "doctor": {
                "typical_questions": [
                    "What type of appointment would you like to schedule?",
                    "Do you have a preferred doctor?",
                    "What's your insurance information?",
                    "What's the reason for your visit?",
                    "What days/times work best for you?"
                ],
                "typical_duration": "30-60 minutes",
                "advance_booking": "1-2 weeks",
                "info_needed": ["name", "date of birth", "insurance", "reason"]
            },
            "dentist": {
                "typical_questions": [
                    "Is this for a cleaning or specific issue?",
                    "Do you have a preferred dentist or hygienist?",
                    "What's your insurance information?",
                    "When was your last visit?",
                    "What times work best for you?"
                ],
                "typical_duration": "30-90 minutes", 
                "advance_booking": "2-4 weeks",
                "info_needed": ["name", "insurance", "last visit", "service type"]
            },
            "haircut": {
                "typical_questions": [
                    "Do you have a preferred stylist?",
                    "What type of service? (cut, color, etc.)",
                    "What days/times work best?",
                    "Any specific requests or styles?"
                ],
                "typical_duration": "30-120 minutes",
                "advance_booking": "1-2 weeks", 
                "info_needed": ["name", "service type", "stylist preference"]
            },
            "general": {
                "typical_questions": [
                    "What type of appointment is this for?",
                    "How long do you expect it to take?",
                    "What days/times work best?",
                    "Any specific requirements?"
                ],
                "typical_duration": "30-60 minutes",
                "advance_booking": "1-2 weeks",
                "info_needed": ["name", "appointment type", "duration"]
            }
        }
    
    async def prepare_appointment_call(self, appointment_details: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare comprehensive call script and information for appointment booking"""
        
        appointment_type = appointment_details.get("appointment_type", "general").lower()
        template = self.appointment_templates.get(appointment_type, self.appointment_templates["general"])
        
        user_name = appointment_details.get("user_name", "the client")
        business_name = appointment_details.get("business_name", "your office")
        business_phone = appointment_details.get("business_phone", "")
        preferred_dates = appointment_details.get("preferred_dates", [])
        preferred_times = appointment_details.get("preferred_times", [])
        reason = appointment_details.get("reason", "")
        special_requests = appointment_details.get("special_requests", "")
        
        # Generate call script
        call_script = f"""
📞 APPOINTMENT BOOKING CALL SCRIPT FOR {business_name}
Phone: {business_phone}

=== OPENING ===
"Hi, good [morning/afternoon]! My name is Eva and I'm calling on behalf of {user_name} to schedule {' '.join(appointment_type.split('_'))} appointment."

=== APPOINTMENT DETAILS ===
• Client Name: {user_name}
• Appointment Type: {template['typical_duration']} {appointment_type} appointment
• Reason: {reason if reason else 'routine appointment'}
• Duration Needed: Approximately {template['typical_duration']}

=== PREFERRED SCHEDULING ===
• Preferred Dates: {', '.join(preferred_dates) if preferred_dates else 'Flexible with dates'}
• Preferred Times: {', '.join(preferred_times) if preferred_times else 'Flexible with timing'}
• Special Requests: {special_requests if special_requests else 'None'}

=== TYPICAL QUESTIONS THEY MIGHT ASK ===
{chr(10).join([f"• {q}" for q in template['typical_questions']])}

=== INFORMATION TO HAVE READY ===
{chr(10).join([f"• {info.replace('_', ' ').title()}" for info in template['info_needed']])}

=== BOOKING FLOW ===
1. Introduce yourself and state purpose
2. Provide client name and appointment type
3. Share preferred dates/times
4. Answer any questions about the appointment
5. Confirm final appointment details
6. Get any preparation instructions
7. Thank them and confirm contact information

=== BACKUP OPTIONS ===
• If no availability on preferred dates: "What's the earliest available appointment?"
• If they need to call back: "What's the best number for {user_name}?"
• If they're closed: "What are your regular business hours?"

=== CONTACT INFO FOR FOLLOW-UP ===
• Client Name: {user_name}
• Callback needed: Yes (provide user's preferred contact method)
"""

        return {
            "call_script": call_script,
            "appointment_summary": {
                "business_name": business_name,
                "business_phone": business_phone,
                "appointment_type": appointment_type,
                "user_name": user_name,
                "preferred_dates": preferred_dates,
                "preferred_times": preferred_times,
                "reason": reason,
                "typical_duration": template['typical_duration'],
                "advance_booking_time": template['advance_booking'],
                "questions_to_expect": template['typical_questions'],
                "info_needed": template['info_needed']
            }
        }
    
    async def generate_call_audio(self, call_script: str) -> Optional[str]:
        """Generate audio version of call script using ElevenLabs TTS"""
        
        if not self.elevenlabs_api_key:
            return None
            
        # Use your existing ElevenLabs integration
        try:
            from integrations.elevenlabs_integration import ElevenLabsTTS
            tts = ElevenLabsTTS()
            
            # Create a condensed audio version for reference
            audio_script = f"""
Here's your appointment booking preparation for {call_script.split('FOR ')[1].split('Phone:')[0].strip()}.

You're calling to book {call_script.split('appointment type: ')[1].split('Duration')[0].strip()}.

Key details: {call_script.split('Client Name: ')[1].split('=== PREFERRED')[0].strip()}

Remember to be polite, professional, and flexible with scheduling.
"""
            
            audio_file = await tts.generate_speech(audio_script, voice="professional")
            return audio_file
            
        except Exception as e:
            logger.warning(f"Could not generate audio script: {e}")
            return None
    
    async def handle_call(self, action: str, parameters: Dict[str, Any]) -> ToolResponse:
        """Handle appointment booking tool calls"""
        try:
            if action == "prepare_appointment":
                # Prepare comprehensive appointment booking information
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
                        error="Business phone number is required for appointment preparation"
                    )
                
                appointment_details = {
                    "appointment_type": appointment_type,
                    "user_name": user_name,
                    "business_name": business_name,
                    "business_phone": business_phone,
                    "preferred_dates": preferred_dates,
                    "preferred_times": preferred_times,
                    "reason": reason,
                    "special_requests": special_requests
                }
                
                # Prepare the call
                preparation = await self.prepare_appointment_call(appointment_details)
                
                # Try to generate audio version
                audio_file = await self.generate_call_audio(preparation["call_script"])
                
                return ToolResponse(
                    success=True,
                    result={
                        "call_script": preparation["call_script"],
                        "appointment_summary": preparation["appointment_summary"],
                        "audio_file": audio_file,
                        "next_steps": [
                            f"Call {business_name} at {business_phone}",
                            "Use the provided script as a guide",
                            "Be prepared to answer typical questions",
                            "Confirm appointment details clearly",
                            "Get any special instructions"
                        ],
                        "message": f"I've prepared everything you need to call {business_name} and book your {appointment_type} appointment!"
                    }
                )
                
            elif action == "quick_appointment_info":
                # Provide quick appointment booking guidance
                appointment_type = parameters.get("appointment_type", "general")
                template = self.appointment_templates.get(appointment_type, self.appointment_templates["general"])
                
                return ToolResponse(
                    success=True,
                    result={
                        "appointment_type": appointment_type,
                        "typical_duration": template["typical_duration"],
                        "advance_booking": template["advance_booking"],
                        "questions_to_expect": template["typical_questions"],
                        "info_to_prepare": template["info_needed"],
                        "tips": [
                            "Have your calendar ready with flexible dates/times",
                            "Prepare insurance information if applicable",
                            "Be ready to explain the reason for your appointment",
                            "Ask about preparation requirements",
                            "Confirm contact information for reminders"
                        ]
                    }
                )
                
            else:
                return ToolResponse(
                    success=False,
                    result=None,
                    error=f"Unknown appointment action: {action}"
                )
                
        except Exception as e:
            logger.error(f"Simple appointment handler error: {e}")
            return ToolResponse(success=False, result=None, error=str(e))