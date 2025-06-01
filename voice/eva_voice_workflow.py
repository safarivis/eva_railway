"""
EVA Voice Workflow - Adapter for real-time voice conversations
Integrates OpenAI Agents SDK patterns with EVA's context system
"""

import asyncio
import json
import uuid
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime
import logging

import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.zep_context_manager import ContextualMemoryManager, MemoryContext, AgentMode
from integrations.private_context_auth import PrivateContextAuth

logger = logging.getLogger(__name__)

class EVAVoiceWorkflow:
    """
    Voice workflow adapter that integrates with EVA's existing systems:
    - Context-aware conversations (work/personal/creative/etc)
    - Password-protected private mode
    - Zep memory integration
    - Mode-based agent behavior
    """
    
    def __init__(self, 
                 context_manager: ContextualMemoryManager,
                 private_auth: PrivateContextAuth,
                 llm_handler,
                 stt_handler,
                 tts_handler):
        self.context_manager = context_manager
        self.private_auth = private_auth
        self.llm_handler = llm_handler
        self.stt_handler = stt_handler
        self.tts_handler = tts_handler
        
        # Track active voice conversations
        self.voice_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def start_voice_session(self, 
                                session_id: str,
                                user_id: str, 
                                context: str = "general",
                                mode: str = "assistant",
                                auth_session_id: Optional[str] = None) -> Dict[str, Any]:
        """Start a new voice conversation session"""
        
        try:
            # Parse context and mode
            memory_context = MemoryContext(context) if context != "general" else MemoryContext.GENERAL
            agent_mode = AgentMode(mode) if mode else AgentMode.ASSISTANT
        except ValueError:
            memory_context = MemoryContext.GENERAL
            agent_mode = AgentMode.ASSISTANT
        
        # Check authentication for private contexts
        if context in ["personal", "private"]:
            if self.private_auth.is_password_required(user_id, context):
                if not auth_session_id or not self.private_auth.verify_session(auth_session_id, user_id, context):
                    raise PermissionError("Authentication required for private context")
        
        # Create voice session
        self.voice_sessions[session_id] = {
            "user_id": user_id,
            "context": memory_context,
            "mode": agent_mode,
            "auth_session_id": auth_session_id,
            "messages": [],
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "conversation_state": "idle"
        }
        
        # Initialize Zep session if using contextual memory
        if context != "general" and self.context_manager:
            try:
                await self.context_manager.create_contextual_session(
                    run_id=session_id,
                    base_user_id=user_id,
                    context=memory_context,
                    mode=agent_mode
                )
                logger.info(f"Created contextual Zep session for voice session {session_id}")
            except Exception as e:
                logger.error(f"Error creating contextual Zep session: {e}")
        
        logger.info(f"Started voice session {session_id} for user {user_id} in {context} context")
        
        return {
            "session_id": session_id,
            "status": "ready",
            "context": context,
            "mode": mode,
            "auth_required": context in ["personal", "private"] and self.private_auth.is_password_required(user_id, context)
        }
    
    async def process_voice_input(self, session_id: str, audio_data: bytes) -> AsyncGenerator[Dict[str, Any], None]:
        """Process voice input and generate streaming response"""
        
        if session_id not in self.voice_sessions:
            yield {"type": "error", "message": "Session not found"}
            return
        
        session = self.voice_sessions[session_id]
        session["last_activity"] = datetime.now()
        session["conversation_state"] = "processing"
        
        try:
            # Step 1: Speech-to-Text
            yield {"type": "stt_start", "message": "Converting speech to text..."}
            
            user_text = await self.stt_handler.speech_to_text(audio_data)
            
            if not user_text.strip():
                yield {"type": "stt_empty", "message": "No speech detected"}
                session["conversation_state"] = "idle"
                return
            
            yield {"type": "stt_complete", "text": user_text}
            
            # Step 2: Add to conversation history
            user_message = {"role": "user", "content": user_text}
            session["messages"].append(user_message)
            
            # Step 3: Generate response using EVA's conversation system
            yield {"type": "eva_thinking", "message": "EVA is thinking..."}
            
            async for response_chunk in self.generate_eva_response(session_id, user_text):
                yield response_chunk
            
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            yield {"type": "error", "message": f"Processing error: {str(e)}"}
            session["conversation_state"] = "error"
    
    async def generate_eva_response(self, session_id: str, user_text: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate EVA's response using existing conversation logic"""
        
        session = self.voice_sessions[session_id]
        
        try:
            # Get memory context if available
            memory_context = None
            if session["context"] != MemoryContext.GENERAL and self.context_manager:
                try:
                    memory_context = await self.context_manager.get_contextual_memory(
                        session_id, 
                        include_cross_context=True
                    )
                except Exception as e:
                    logger.error(f"Error retrieving memory context: {e}")
            
            # Prepare messages for LLM
            messages = session["messages"].copy()
            
            # Add memory context if available
            if memory_context:
                system_message = {
                    "role": "system", 
                    "content": f"Previous conversation context:\n{memory_context}"
                }
                messages = [system_message] + messages
            
            # Add mode-specific instructions
            if self.context_manager:
                mode_instructions = await self.context_manager.apply_mode_instructions(session["mode"])
                if mode_instructions:
                    mode_system_message = {
                        "role": "system",
                        "content": mode_instructions
                    }
                    messages = [mode_system_message] + messages
            
            # Generate streaming response
            response_text = ""
            
            yield {"type": "llm_start", "message": "Generating response..."}
            
            # Use existing LLM handler for streaming response
            async for chunk in self.stream_llm_response(messages):
                if chunk:
                    response_text += chunk
                    yield {"type": "llm_chunk", "text": chunk, "partial_response": response_text}
            
            # Add response to conversation history
            assistant_message = {"role": "assistant", "content": response_text}
            session["messages"].append(assistant_message)
            
            yield {"type": "llm_complete", "text": response_text}
            
            # Add to Zep memory
            if session["context"] != MemoryContext.GENERAL and self.context_manager:
                try:
                    await self.context_manager.add_contextual_messages(
                        session_id,
                        [{"role": "user", "content": user_text}, assistant_message]
                    )
                except Exception as e:
                    logger.error(f"Error adding to Zep memory: {e}")
            
            # Generate TTS
            yield {"type": "tts_start", "message": "Generating voice response..."}
            
            async for audio_chunk in self.generate_streaming_tts(response_text):
                yield audio_chunk
            
            yield {"type": "tts_complete", "message": "Voice response complete"}
            
            session["conversation_state"] = "idle"
            
        except Exception as e:
            logger.error(f"Error generating EVA response: {e}")
            yield {"type": "error", "message": f"Response generation error: {str(e)}"}
            session["conversation_state"] = "error"
    
    async def stream_llm_response(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Stream LLM response using existing handler"""
        try:
            # This integrates with the existing LLM query function
            # We'll need to modify query_llm to support streaming yields
            
            # For now, simulate streaming by chunking the response
            response = await self.llm_handler(messages, stream=False)
            
            if response and "choices" in response:
                content = response["choices"][0]["message"]["content"]
                
                # Simulate streaming by yielding words
                words = content.split()
                for i, word in enumerate(words):
                    if i == 0:
                        yield word
                    else:
                        yield f" {word}"
                    
                    # Small delay to simulate streaming
                    await asyncio.sleep(0.05)
            
        except Exception as e:
            logger.error(f"Error in LLM streaming: {e}")
            yield f"Error: {str(e)}"
    
    async def generate_streaming_tts(self, text: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate streaming TTS response"""
        try:
            # Check if TTS handler supports streaming
            if hasattr(self.tts_handler, 'text_to_speech_stream'):
                # Stream audio chunks
                chunk_count = 0
                async for audio_chunk in self.tts_handler.text_to_speech_stream(text):
                    import base64
                    audio_base64 = base64.b64encode(audio_chunk).decode('utf-8')
                    yield {
                        "type": "tts_chunk", 
                        "audio": audio_base64,
                        "format": "mp3",
                        "chunk_index": chunk_count
                    }
                    chunk_count += 1
            else:
                # Generate full audio
                audio_data = await self.tts_handler.text_to_speech(text)
                import base64
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                yield {
                    "type": "tts_audio",
                    "audio": audio_base64,
                    "format": "mp3"
                }
                
        except Exception as e:
            logger.error(f"Error generating TTS: {e}")
            yield {"type": "tts_error", "message": f"TTS error: {str(e)}"}
    
    async def handle_interruption(self, session_id: str):
        """Handle user interruption of current response"""
        if session_id not in self.voice_sessions:
            return
        
        session = self.voice_sessions[session_id]
        session["conversation_state"] = "interrupted"
        
        # Stop any ongoing processing
        # This would integrate with cancellation tokens in a full implementation
        
        logger.info(f"Voice session {session_id} interrupted")
        
        return {"type": "interrupted", "message": "Response interrupted"}
    
    async def end_voice_session(self, session_id: str):
        """End voice session and cleanup"""
        if session_id in self.voice_sessions:
            session = self.voice_sessions[session_id]
            
            # Final memory save if needed
            if session["context"] != MemoryContext.GENERAL and self.context_manager:
                try:
                    # Any final cleanup for Zep session
                    pass
                except Exception as e:
                    logger.error(f"Error in final memory save: {e}")
            
            del self.voice_sessions[session_id]
            logger.info(f"Ended voice session {session_id}")
        
        return {"type": "session_ended", "session_id": session_id}
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a voice session"""
        if session_id not in self.voice_sessions:
            return None
        
        session = self.voice_sessions[session_id]
        return {
            "session_id": session_id,
            "user_id": session["user_id"],
            "context": session["context"].value,
            "mode": session["mode"].value,
            "conversation_state": session["conversation_state"],
            "message_count": len(session["messages"]),
            "created_at": session["created_at"].isoformat(),
            "last_activity": session["last_activity"].isoformat()
        }
    
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active voice sessions"""
        return [self.get_session_info(sid) for sid in self.voice_sessions.keys()]