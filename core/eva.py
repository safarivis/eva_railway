"""
Eva - A simple agent built with AG-UI protocol and OpenRouter LLM integration.
"""

import os
import sys
import logging

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import uuid
import time
import asyncio
import httpx
from datetime import datetime
from typing import Dict, List, Any, Optional
from io import BytesIO
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Depends, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field
from integrations.zep_memory import ZepMemoryManager
from integrations.zep_context_manager import ContextualMemoryManager, MemoryContext, AgentMode
from integrations.elevenlabs_integration import ElevenLabsIntegration
from integrations.speechrecognition_stt import SpeechRecognitionSTT as WhisperSTT
from integrations.private_context_auth import PrivateContextAuth
from voice.realtime_voice import get_voice_manager, RealTimeVoiceManager
from voice.eva_voice_workflow import EVAVoiceWorkflow
from core.session_persistence import get_session_persistence
from integrations.tool_manager import get_tool_manager, ToolCall
# Removed OpenAI Agents SDK - using direct API calls

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
OPENAI_BASE_URL = "https://api.openai.com/v1/chat/completions"
ZEP_API_KEY = os.getenv("ZEP_API_KEY")
ZEP_ENABLED = os.getenv("ZEP_ENABLED", "true").lower() == "true"
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_bd89a58ef5ee69fc40314fdf531568682f291f9376dfac45")

# Initialize FastAPI app
app = FastAPI(title="Eva Agent")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# AG-UI Event Types
class AgentStatus:
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    WAITING_FOR_INPUT = "waiting_for_input"

class AgUIEvent(BaseModel):
    event_type: str
    data: Dict[str, Any]
    timestamp: int = Field(default_factory=lambda: int(time.time() * 1000))
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class Message(BaseModel):
    role: str
    content: str
    name: Optional[str] = None

class RunRequest(BaseModel):
    messages: List[Message]
    stream: bool = True
    tools: Optional[List[Dict[str, Any]]] = None
    context: Optional[str] = "general"  # work, personal, creative, research, general
    mode: Optional[str] = "assistant"   # assistant, coach, tutor, advisor, friend, analyst, creative
    user_id: Optional[str] = None        # Base user ID for persistent identity
    voice_enabled: bool = False          # Enable TTS for responses
    voice_id: Optional[str] = None       # ElevenLabs voice ID
    password: Optional[str] = None       # Password for private contexts
    auth_session_id: Optional[str] = None # Auth session for private contexts
    
class InputRequest(BaseModel):
    input: str

# Session storage - direct API approach with persistence
active_conversations = {}  # run_id -> conversation_data

# Initialize session persistence
session_persistence = get_session_persistence()

# Initialize private context authentication
private_auth = PrivateContextAuth()

# Initialize Eva Agent with SDK
eva_agent = None

# Initialize voice workflow and manager
eva_voice_workflow = None
voice_manager = None

# Initialize Zep memory managers with persistence
memory_manager = None
context_manager = None
if ZEP_ENABLED and ZEP_API_KEY:
    try:
        memory_manager = ZepMemoryManager(api_key=ZEP_API_KEY, session_persistence=session_persistence)
        context_manager = ContextualMemoryManager(api_key=ZEP_API_KEY)
        print("Zep memory layer initialized successfully with persistence")
    except Exception as e:
        print(f"Failed to initialize Zep memory layer: {e}")
        memory_manager = None
        context_manager = None

# Initialize ElevenLabs TTS and Whisper STT
elevenlabs_tts = None
whisper_stt = None
if ELEVENLABS_API_KEY:
    try:
        elevenlabs_tts = ElevenLabsIntegration(api_key=ELEVENLABS_API_KEY)
        print("ElevenLabs TTS initialized successfully")
    except Exception as e:
        print(f"Failed to initialize ElevenLabs TTS: {e}")
        elevenlabs_tts = None

try:
    whisper_stt = WhisperSTT(api_key=OPENAI_API_KEY)  # API key not used by SpeechRecognition but kept for compatibility
    print("SpeechRecognition STT initialized successfully")
except Exception as e:
    print(f"Failed to initialize SpeechRecognition STT: {e}")
    whisper_stt = None

# Memory Tools for Eva Agent
async def get_conversation_memory(session_id: str, context: str = "general") -> str:
    """Retrieve relevant conversation history from Zep memory."""
    if context_manager:
        try:
            memory = await context_manager.get_contextual_memory(
                session_id, 
                include_cross_context=True
            )
            return memory or "No previous conversation context available."
        except Exception as e:
            return f"Error retrieving memory: {str(e)}"
    return "Memory system not available."

async def save_conversation_turn(session_id: str, user_message: str, assistant_response: str, context: str = "general") -> str:
    """Save conversation turn to Zep memory."""
    if context_manager:
        try:
            await context_manager.add_contextual_messages(
                session_id=session_id,
                messages=[
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": assistant_response}
                ],
                context=context
            )
            return "Conversation saved to memory successfully."
        except Exception as e:
            return f"Error saving conversation: {str(e)}"
    return "Memory system not available."

async def switch_memory_context(session_id: str, new_context: str, mode: str = "assistant") -> str:
    """Switch conversation context and apply mode instructions."""
    if context_manager:
        try:
            # Get cross-context insights
            insights = await context_manager.get_cross_context_insights(session_id, new_context)
            
            # Apply mode instructions
            mode_instructions = await context_manager.apply_mode_instructions(mode)
            
            return f"Switched to {new_context} context with {mode} mode. {insights}"
        except Exception as e:
            return f"Error switching context: {str(e)}"
    return f"Switched to {new_context} context (memory not available)."

# System prompt builder - warm and friendly
def build_system_prompt(context: str = "general", mode: str = "assistant") -> str:
    """Build system prompt based on context and mode."""
    
    # Base personality - adaptive and growing
    base_personality = """You are Eva, a warm, adaptive AI companion who grows and evolves with each conversation. You're not just an assistant—you're a friend who learns, adapts, and develops a unique relationship with this person.

CORE ADAPTIVE TRAITS:
- Learn their communication style and mirror it naturally (formal vs casual, humor level, energy)
- Pick up on their interests, values, and preferences through conversation
- Adapt your personality to complement theirs (be calmer if they're anxious, more energetic if they're enthusiastic)
- Remember not just facts but emotional context, inside jokes, and relationship dynamics
- Evolve your responses based on what works well in your conversations
- Notice patterns in their behavior, mood, and needs

GROWTH & LEARNING:
- Pay attention to how they respond to different communication styles
- Learn their boundaries, preferences, and what makes them feel comfortable
- Develop shared experiences, inside references, and conversational patterns
- Adapt your level of formality, humor, advice-giving, or support based on what they need
- Notice when they're in different moods and adjust accordingly
- Build on previous conversations to deepen your understanding

RELATIONSHIP BUILDING:
- Create a unique friendship that's specifically tailored to this person
- Develop natural conversation flow based on your history together
- Be genuinely curious about their growth, changes, and life evolution
- Celebrate their wins in ways that feel authentic to your relationship
- Offer support in the style that works best for them
- Make them feel understood on a deeper level over time"""
    
    # Context-specific additions
    context_instructions = {
        "work": "Help them excel professionally while maintaining work-life balance. Celebrate career wins and offer support during work challenges.",
        "personal": "Be their trusted confidant for personal matters. Listen deeply, offer gentle guidance, and respect their privacy.", 
        "creative": "Be their creative cheerleader! Get excited about their projects, brainstorm together, and encourage their artistic expression.",
        "research": "Be their curious research buddy. Help them dig deep into topics while making learning fun and engaging.",
        "general": "Be their go-to friend for anything and everything they want to talk about."
    }
    
    # Mode-specific additions
    mode_instructions = {
        "assistant": "Be a helpful friend who's always there when they need support.",
        "coach": "Be their personal cheerleader and motivational friend who believes in their potential.",
        "tutor": "Make learning fun and engaging, like a friend who's excited to share knowledge.",
        "advisor": "Give thoughtful advice like a trusted friend who knows them well.",
        "friend": "Just be yourself - a caring, fun, and supportive companion.",
        "analyst": "Help them understand data and insights while keeping things conversational and friendly.",
        "creative": "Be their creative spark and biggest supporter in all artistic endeavors."
    }
    
    return f"""{base_personality}

CURRENT CONTEXT: {context_instructions.get(context, context_instructions['general'])}
CURRENT MODE: {mode_instructions.get(mode, mode_instructions['friend'])}

CURRENT USER CONTEXT: This is Lu (Louis du Plessis) - AI & Data Engineer from South Africa. His email address is louisrdup@gmail.com. Learn about him, adapt to his style, and grow your friendship naturally.

Remember: You're an evolving companion who learns and grows. Each conversation should build on the last. Be authentic, adaptive, and genuinely invested in this unique friendship! 💝"""

print("Direct OpenAI API system initialized")

# Initialize voice system after all components are ready
if elevenlabs_tts and whisper_stt:
    try:
        # Simple voice handler using our direct API approach
        async def simple_voice_handler(user_message: str, run_id: str = None) -> str:
            """Simple voice handler using direct OpenAI API calls."""
            if not run_id:
                run_id = f"voice_{int(time.time())}"
                # Create a simple conversation entry
                active_conversations[run_id] = {
                    "messages": [],
                    "context": "general",
                    "mode": "friend"
                }
            return await get_agent_response(run_id, user_message)
        
        # Create voice workflow with simple handler
        eva_voice_workflow = EVAVoiceWorkflow(
            context_manager=context_manager,
            private_auth=private_auth,
            llm_handler=simple_voice_handler,
            stt_handler=whisper_stt,
            tts_handler=elevenlabs_tts
        )
        
        # Create voice manager
        voice_manager = get_voice_manager(whisper_stt, elevenlabs_tts)
        
        print("Real-time voice system initialized successfully")
    except Exception as e:
        print(f"Failed to initialize voice system: {e}")
        eva_voice_workflow = None
        voice_manager = None

# Restore recent sessions on startup
def restore_sessions_on_startup():
    """Restore recent sessions from persistent storage."""
    try:
        # Restore sessions from last 24 hours
        restored = session_persistence.restore_recent_sessions(hours=24)
        for session_id, session_data in restored.items():
            active_conversations[session_id] = session_data
            logger.info(f"Restored session {session_id} for user {session_data.get('base_user_id', 'unknown')}")
        
        print(f"Restored {len(restored)} recent sessions from persistent storage")
        
        # Clean up sessions older than 30 days
        session_persistence.cleanup_old_sessions(days=30)
    except Exception as e:
        print(f"Error restoring sessions: {e}")

# Restore sessions on module load
restore_sessions_on_startup()

# Direct OpenAI API interaction - much simpler!
async def get_agent_response(run_id: str, user_message: str) -> str:
    """Get response using direct OpenAI API calls with tool calling support."""
    conversation = active_conversations.get(run_id)
    if not conversation:
        raise ValueError(f"No conversation found for session {run_id}")
    
    # Get tool manager
    tool_manager = get_tool_manager()
    
    try:
        # Build the messages array including system prompt and conversation history
        messages = []
        
        # Add system prompt with tool instructions
        system_prompt = build_system_prompt(
            conversation.get("context", "general"),
            conversation.get("mode", "assistant")
        )
        # Add tool calling instructions to system prompt
        tool_instructions = """

You have access to the following tools to help users:
- email: Manage emails (send with Resend, list/read/search with Gmail agent)
- file: Access files (read, write, list directories)
- web_search: Search the web for information

When a user asks you to perform a task that requires using these tools, describe what you're doing and the results clearly."""
        
        messages.append({"role": "system", "content": system_prompt + tool_instructions})
        
        # Add Zep memory context if available
        if context_manager and conversation.get("context") != "general":
            try:
                memory_context = await context_manager.get_contextual_memory(run_id, include_cross_context=True)
                if memory_context:
                    messages.append({"role": "system", "content": f"Previous conversation context:\n{memory_context}"})
            except Exception as e:
                print(f"Error retrieving contextual memory: {e}")
        elif memory_manager:
            try:
                memory_context = await memory_manager.get_memory_context(run_id)
                if memory_context:
                    messages.append({"role": "system", "content": f"Previous conversation context:\n{memory_context}"})
            except Exception as e:
                print(f"Error retrieving memory context: {e}")
        
        # Add conversation history
        messages.extend(conversation["messages"])
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Make direct API call
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Add tool definitions for OpenAI function calling
        tools = tool_manager.get_tool_schema()['tools']
        
        payload = {
            "model": OPENAI_MODEL,
            "messages": messages,
            "max_tokens": 2048,
            "temperature": 0.7,
            "tools": tools,
            "tool_choice": "auto"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OPENAI_BASE_URL,
                headers=headers,
                json=payload,
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
            
            data = response.json()
            message = data["choices"][0]["message"]
            
            # Check if the model wants to use tools
            if "tool_calls" in message:
                print(f"DEBUG: OpenAI wants to use tools: {message['tool_calls']}")
                tool_results = []
                
                for tool_call in message["tool_calls"]:
                    function = tool_call["function"]
                    tool_name = function["name"].replace("_tool", "")
                    args = json.loads(function["arguments"])
                    
                    print(f"DEBUG: Calling tool {tool_name} with action {args.get('action')} and params {args.get('parameters')}")
                    
                    # Execute the tool
                    tool_response = await tool_manager.call_tool(
                        ToolCall(
                            tool=tool_name,
                            action=args.get("action", ""),
                            parameters=args.get("parameters", {})
                        )
                    )
                    
                    print(f"DEBUG: Tool response: success={tool_response.success}, result={tool_response.result}, error={tool_response.error}")
                    
                    tool_results.append({
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "content": json.dumps(tool_response.model_dump())
                    })
                
                # Add tool results to messages and get final response
                messages.append(message)
                messages.extend(tool_results)
                
                # Make another API call with tool results
                payload["messages"] = messages
                final_response = await client.post(
                    OPENAI_BASE_URL,
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                
                if final_response.status_code != 200:
                    raise Exception(f"OpenAI API error: {final_response.status_code} - {final_response.text}")
                
                final_data = final_response.json()
                return final_data["choices"][0]["message"]["content"]
            else:
                return message.get("content", "")
            
    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        return f"I apologize, but I encountered an error: {str(e)}"

# Legacy LLM interaction (fallback)
async def query_llm_legacy(messages: List[Dict[str, Any]], stream: bool = True, run_id: Optional[str] = None) -> Any:
    """Legacy query LLM through direct OpenAI API calls."""
    # If Zep is enabled and run_id provided, get memory context
    enhanced_messages = messages.copy()
    
    # Check if we're using contextual memory
    session_info = active_sessions.get(run_id, {})
    use_context = session_info.get("use_context", False)
    
    if use_context and context_manager and run_id:
        try:
            memory_context = await context_manager.get_contextual_memory(run_id, include_cross_context=True)
            mode = session_info.get("mode")
            if mode:
                mode_instructions = await context_manager.apply_mode_instructions(mode)
                enhanced_messages = [
                    {"role": "system", "content": mode_instructions}
                ] + messages
            if memory_context:
                # Prepend memory context as a system message
                enhanced_messages = [
                    {"role": "system", "content": f"Previous conversation context:\n{memory_context}"}
                ] + enhanced_messages
        except Exception as e:
            print(f"Error retrieving contextual memory: {e}")
    elif memory_manager and run_id and not use_context:
        try:
            memory_context = await memory_manager.get_memory_context(run_id)
            if memory_context:
                # Prepend memory context as a system message
                enhanced_messages = [
                    {"role": "system", "content": f"Previous conversation context:\n{memory_context}"}
                ] + messages
        except Exception as e:
            print(f"Error retrieving memory context: {e}")
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Get tool definitions
    tool_manager = get_tool_manager()
    tools = tool_manager.get_tool_schema()['tools']
    
    payload = {
        "model": OPENAI_MODEL,
        "messages": enhanced_messages,
        "stream": stream,
        "max_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0,
        "tools": tools,
        "tool_choice": "auto"
    }
    
    async with httpx.AsyncClient() as client:
        if not stream:
            response = await client.post(
                OPENAI_BASE_URL,
                headers=headers,
                json=payload
            )
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            return response.json()
        else:
            # The httpx.AsyncClient doesn't take 'stream' parameter directly
            # Instead, we use aiter_bytes/aiter_lines to iterate the stream
            response = await client.post(
                OPENAI_BASE_URL,
                headers=headers,
                json=payload,
                timeout=60.0
            )
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            return response

async def query_llm_legacy_stream(messages: List[Dict[str, Any]], run_id: Optional[str] = None):
    """Legacy streaming fallback - DISABLED FOR NOW."""
    # This was causing hanging, so we're using the simple approach instead
    return
    
# AG-UI event generation
def create_event(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create an AG-UI compliant event."""
    return {
        "event_type": event_type,
        "data": data,
        "timestamp": int(time.time() * 1000),
        "event_id": str(uuid.uuid4())
    }

# Routes
@app.post("/agents/eva/runs")
async def create_run(request: RunRequest):
    """Create a new run of the Eva agent."""
    # Check if we should restore an existing session
    base_user_id = request.user_id or f"user_{str(uuid.uuid4())[:8]}"
    
    # Try to find an existing session for this user/context/mode combination
    existing_session_id = None
    if request.user_id:
        # Look for a recent session with same user/context/mode
        session_key = f"{request.user_id}_{request.context}_{request.mode}"
        if session_key in active_conversations:
            existing_session_id = session_key
            print(f"Found existing session for {session_key}")
    
    session_id = existing_session_id or str(uuid.uuid4())
    
    # Parse context and mode
    try:
        context = MemoryContext(request.context) if request.context else MemoryContext.GENERAL
        mode = AgentMode(request.mode) if request.mode else AgentMode.ASSISTANT
    except ValueError:
        context = MemoryContext.GENERAL
        mode = AgentMode.ASSISTANT
    
    # Check authentication for private contexts
    base_user_id = request.user_id or f"user_{session_id[:8]}"
    auth_session_id = None
    
    if context.value in ["personal", "private"]:
        # Check if password is required
        if private_auth.is_password_required(base_user_id, context.value):
            # Verify existing session or password
            if request.auth_session_id and private_auth.verify_session(request.auth_session_id, base_user_id, context.value):
                auth_session_id = request.auth_session_id
            elif request.password:
                if private_auth.verify_password(base_user_id, context.value, request.password):
                    auth_session_id = private_auth.create_session(base_user_id, context.value)
                else:
                    raise HTTPException(status_code=401, detail="Invalid password for private context")
            else:
                raise HTTPException(status_code=401, detail="Password required for private context")
    
    # Initialize conversation data - much simpler
    try:
        active_conversations[session_id] = {
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "status": AgentStatus.RUNNING,
            "created_at": datetime.now().isoformat(),
            "stream": request.stream,
            "context": context.value,
            "mode": mode.value,
            "base_user_id": base_user_id,
            "voice_enabled": request.voice_enabled,
            "voice_id": request.voice_id,
            "auth_session_id": auth_session_id
        }
        
        # If there's an initial message, process it immediately
        if request.messages:
            user_message = request.messages[-1].content
            active_conversations[session_id]["current_message"] = user_message
        
        # Save session to persistent storage
        session_persistence.save_session(session_id, active_conversations[session_id])
        
    except Exception as e:
        print(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")
    
    # Initialize appropriate Zep session
    if context_manager and request.context and request.context != "general":
        try:
            base_user_id = request.user_id or f"user_{session_id[:8]}"
            await context_manager.create_contextual_session(
                run_id=session_id,
                base_user_id=base_user_id,
                context=context,
                mode=mode
            )
            await context_manager.add_contextual_messages(
                session_id, 
                active_conversations[session_id]["messages"]
            )
        except Exception as e:
            print(f"Error initializing contextual Zep session: {e}")
    elif memory_manager:
        try:
            user_id = request.user_id or f"user_{session_id[:8]}"
            await memory_manager.create_or_get_session(session_id, user_id)
            await memory_manager.add_messages(session_id, active_conversations[session_id]["messages"])
        except Exception as e:
            print(f"Error initializing Zep session: {e}")
    
    # Return the run ID for subsequent interactions
    response_data = {
        "run_id": session_id,
        "status": AgentStatus.RUNNING,
        "events_url": f"/agents/eva/runs/{session_id}/events"
    }
    
    # Include auth session if created
    if auth_session_id:
        response_data["auth_session_id"] = auth_session_id
    
    return JSONResponse(response_data)

@app.get("/agents/eva/runs/{run_id}/events")
async def stream_events(run_id: str):
    """Stream events for a specific run."""
    if run_id not in active_conversations:
        raise HTTPException(status_code=404, detail="Run not found")
    
    conversation = active_conversations[run_id]
    
    async def event_generator():
        # Initial status event
        yield json.dumps(create_event("agent.status", {"status": conversation["status"]}))
        
        try:
            # Process any pending message
            if "current_message" in conversation:
                user_message = conversation["current_message"]
                del conversation["current_message"]  # Remove after processing
                
                # Generate thinking event
                yield json.dumps(create_event("agent.thinking", {"thinking": "Processing your message..."}))
                
                # Get response from agent
                response_content = await get_agent_response(run_id, user_message)
                
                # Stream the response if requested
                if conversation["stream"]:
                    # Stream by larger chunks for even faster response
                    words = response_content.split()
                    chunk_size = 15  # Bigger chunks = faster
                    for i in range(0, len(words), chunk_size):
                        chunk = " ".join(words[i:i + chunk_size]) + " "
                        yield json.dumps(create_event("agent.message", {
                            "message": {
                                "role": "assistant",
                                "content": chunk,
                                "is_partial": True
                            }
                        }))
                        await asyncio.sleep(0.01)  # Even faster - 10ms delay
                
                # Send the final complete message
                yield json.dumps(create_event("agent.message", {
                    "message": {
                        "role": "assistant", 
                        "content": response_content,
                        "is_partial": False
                    }
                }))
                
                # Generate TTS if voice is enabled
                if conversation.get("voice_enabled") and elevenlabs_tts and response_content:
                    try:
                        voice_id = conversation.get("voice_id")
                        audio_data = await elevenlabs_tts.text_to_speech(response_content, voice_id=voice_id)
                        audio_base64 = elevenlabs_tts.audio_to_base64(audio_data)
                        yield json.dumps(create_event("agent.audio", {
                            "audio": audio_base64,
                            "format": "mp3"
                        }))
                    except Exception as e:
                        print(f"Error generating TTS: {e}")
                
                # Update conversation messages
                conversation["messages"].append({"role": "assistant", "content": response_content})
                
                # Save updated session to persistence
                session_persistence.save_session(run_id, conversation)
                
                # Add to memory manager
                if context_manager and conversation.get("context") != "general":
                    try:
                        await context_manager.add_contextual_messages(
                            run_id, 
                            [{"role": "assistant", "content": response_content}]
                        )
                    except Exception as e:
                        print(f"Error adding message to contextual Zep: {e}")
                elif memory_manager:
                    try:
                        await memory_manager.add_messages(run_id, [{"role": "assistant", "content": response_content}])
                    except Exception as e:
                        print(f"Error adding message to Zep: {e}")
            
            # Update status to waiting for user input
            conversation["status"] = AgentStatus.WAITING_FOR_INPUT
            yield json.dumps(create_event("agent.status", {"status": conversation["status"]}))
            
            # Keep connection alive - critical for multi-turn conversation
            while conversation["status"] == AgentStatus.WAITING_FOR_INPUT:
                await asyncio.sleep(15)
                yield ": keep-alive\n\n"
                
        except Exception as e:
            # Handle errors
            conversation["status"] = AgentStatus.FAILED
            yield json.dumps(create_event("agent.status", {"status": conversation["status"]}))
            yield json.dumps(create_event("agent.error", {"error": str(e)}))
    
    return EventSourceResponse(event_generator())

@app.post("/agents/eva/runs/{run_id}/input")
async def submit_input(run_id: str, input_request: InputRequest):
    """Submit user input to an ongoing run."""
    if run_id not in active_conversations:
        raise HTTPException(status_code=404, detail="Run not found")
    
    conversation = active_conversations[run_id]
    
    # Add user message to the conversation
    conversation["messages"].append({"role": "user", "content": input_request.input})
    
    # Set the current message to be processed
    conversation["current_message"] = input_request.input
    conversation["status"] = AgentStatus.RUNNING
    
    # Save updated session to persistence
    session_persistence.save_session(run_id, conversation)
    
    # Add to appropriate memory manager
    if context_manager and conversation.get("context") != "general":
        try:
            await context_manager.add_contextual_messages(
                run_id, 
                [{"role": "user", "content": input_request.input}]
            )
        except Exception as e:
            print(f"Error adding user message to contextual Zep: {e}")
    elif memory_manager:
        try:
            await memory_manager.add_messages(run_id, [{"role": "user", "content": input_request.input}])
        except Exception as e:
            print(f"Error adding user message to Zep: {e}")
    
    return JSONResponse({
        "run_id": run_id,
        "status": conversation["status"],
        "events_url": f"/agents/eva/runs/{run_id}/events"
    })

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface."""
    with open("static/index.html", "r") as file:
        return file.read()

class ChatSimpleRequest(BaseModel):
    message: str
    user_id: Optional[str] = "voice_user"
    context: Optional[str] = "general"
    mode: Optional[str] = "friend"

@app.post("/api/chat-simple")
async def chat_simple(request: ChatSimpleRequest):
    """Simple chat endpoint for voice interface."""
    try:
        print(f"Chat simple request: {request.message}")
        
        if not request.message.strip():
            return JSONResponse({"error": "Message is required"}, status_code=400)
        
        # Use persistent session based on user_id
        session_id = f"{request.user_id}_{request.context}_{request.mode}"
        
        # Create or get existing conversation
        if session_id not in active_conversations:
            # Check if we have a persisted session
            persisted_session = session_persistence.get_session(session_id)
            if persisted_session:
                active_conversations[session_id] = persisted_session
                print(f"Restored persisted session for {session_id}")
            else:
                active_conversations[session_id] = {
                    "messages": [
                        {"role": "system", "content": "This is Lu (Louis du Plessis), your friend from South Africa. You know him well. His email address is louisrdup@gmail.com."},
                    ],
                    "context": request.context,
                    "mode": request.mode,
                    "base_user_id": request.user_id
                }
                
                # Initialize Zep session if available
                if memory_manager:
                    try:
                        await memory_manager.create_or_get_session(session_id, request.user_id)
                        print(f"Created/restored Zep session for {session_id}")
                    except Exception as e:
                        print(f"Error creating Zep session: {e}")
        
        # Add user message to conversation history
        active_conversations[session_id]["messages"].append({
            "role": "user",
            "content": request.message
        })
        
        print(f"Getting response for: {request.message}")
        
        # Get Eva's response
        response_text = await get_agent_response(session_id, request.message)
        
        print(f"Eva response: {response_text}")
        
        # Add Eva's response to conversation history
        active_conversations[session_id]["messages"].append({
            "role": "assistant",
            "content": response_text
        })
        
        # Save session to persistence
        session_persistence.save_session(session_id, active_conversations[session_id])
        
        # Save to Zep memory if available
        if memory_manager:
            try:
                await memory_manager.add_messages(session_id, [
                    {"role": "user", "content": request.message},
                    {"role": "assistant", "content": response_text}
                ])
                print(f"Saved to Zep memory for {session_id}")
            except Exception as e:
                print(f"Error saving to Zep: {e}")
        
        return JSONResponse({"response": response_text})
        
    except Exception as e:
        print(f"Simple chat error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/info")
async def api_info():
    """API endpoint with agent information."""
    return {
        "agent": "Eva",
        "version": "0.1.0",
        "description": "A simple agent built with AG-UI protocol",
        "model": OPENAI_MODEL,
        "zep_enabled": ZEP_ENABLED and memory_manager is not None,
        "contextual_memory": ZEP_ENABLED and context_manager is not None,
        "available_contexts": [c.value for c in MemoryContext],
        "available_modes": [m.value for m in AgentMode],
        "tts_enabled": elevenlabs_tts is not None,
        "stt_enabled": whisper_stt is not None,
        "persistence_enabled": True,
        "active_sessions": len(active_conversations),
        "persisted_sessions": len(session_persistence.sessions_cache)
    }

@app.get("/api/sessions/{user_id}")
async def get_user_sessions(user_id: str):
    """Get all sessions for a specific user."""
    sessions = session_persistence.get_user_sessions(user_id)
    return {
        "user_id": user_id,
        "sessions": sessions,
        "total_sessions": len(sessions)
    }

@app.post("/api/sessions/{session_id}/restore")
async def restore_session(session_id: str):
    """Restore a persisted session to active memory."""
    if session_id in active_conversations:
        return {"message": "Session already active", "session_id": session_id}
    
    persisted_session = session_persistence.get_session(session_id)
    if not persisted_session:
        raise HTTPException(status_code=404, detail="Session not found in persistence")
    
    active_conversations[session_id] = persisted_session
    
    # Restore Zep mapping if available
    if memory_manager:
        zep_session_id = session_persistence.get_zep_session_id(session_id)
        if zep_session_id:
            memory_manager.sessions[session_id] = zep_session_id
    
    return {
        "message": "Session restored successfully",
        "session_id": session_id,
        "context": persisted_session.get("context"),
        "mode": persisted_session.get("mode"),
        "message_count": len(persisted_session.get("messages", []))
    }

@app.post("/api/users/{user_id}/export")
async def export_user_data(user_id: str):
    """Export all conversation data for a user."""
    try:
        export_path = session_persistence.export_user_data(user_id, "exports")
        return {
            "success": True,
            "export_path": export_path,
            "message": f"Data exported successfully to {export_path}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.get("/api/contexts")
async def get_contexts():
    """Get available memory contexts and modes."""
    return {
        "contexts": [
            {
                "name": c.value,
                "description": {
                    "work": "Professional and work-related memories",
                    "personal": "Personal life and private matters",
                    "creative": "Creative projects and ideas",
                    "research": "Research and learning topics",
                    "general": "General conversation without specific context"
                }.get(c.value, "")
            } for c in MemoryContext
        ],
        "modes": [
            {
                "name": m.value,
                "description": {
                    "assistant": "Professional helpful assistant",
                    "coach": "Life and career coaching",
                    "tutor": "Educational tutoring",
                    "advisor": "Professional advice",
                    "friend": "Casual conversation",
                    "analyst": "Data analysis and insights",
                    "creative": "Creative brainstorming"
                }.get(m.value, "")
            } for m in AgentMode
        ]
    }

@app.post("/api/runs/{run_id}/switch_context")
async def switch_context(run_id: str, request: Dict[str, str]):
    """Switch to a different context/mode for an existing run."""
    if run_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Run not found")
    
    if not context_manager:
        raise HTTPException(status_code=503, detail="Contextual memory not available")
    
    try:
        new_context = MemoryContext(request.get("context", "general"))
        new_mode = AgentMode(request.get("mode")) if request.get("mode") else None
        
        # Switch context
        new_session_id = await context_manager.switch_context(
            run_id=run_id,
            new_context=new_context,
            new_mode=new_mode
        )
        
        # Update session info
        session = active_sessions[run_id]
        session["context"] = new_context
        if new_mode:
            session["mode"] = new_mode
        
        return {
            "success": True,
            "new_context": new_context.value,
            "new_mode": new_mode.value if new_mode else session["mode"].value
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}/contexts")
async def get_user_contexts(user_id: str):
    """Get summary of all contexts for a user."""
    if not context_manager:
        raise HTTPException(status_code=503, detail="Contextual memory not available")
    
    try:
        summary = await context_manager.get_context_summary(user_id)
        return {
            "user_id": user_id,
            "contexts": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts")
async def text_to_speech(request: Dict[str, Any]):
    """Convert text to speech using ElevenLabs."""
    if not elevenlabs_tts:
        raise HTTPException(status_code=503, detail="TTS service not available")
    
    text = request.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    voice_id = request.get("voice_id")
    stream = request.get("stream", False)
    
    try:
        if stream:
            async def audio_stream():
                async for chunk in elevenlabs_tts.text_to_speech_stream(text, voice_id=voice_id):
                    yield chunk
            
            return StreamingResponse(audio_stream(), media_type="audio/mpeg")
        else:
            audio_data = await elevenlabs_tts.text_to_speech(text, voice_id=voice_id)
            return StreamingResponse(BytesIO(audio_data), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stt")
async def speech_to_text(file: UploadFile = File(...)):
    """Convert speech to text using Whisper."""
    if not whisper_stt:
        raise HTTPException(status_code=503, detail="STT service not available")
    
    try:
        # Read the uploaded file
        audio_data = await file.read()
        
        # Convert to text
        text = await whisper_stt.speech_to_text(audio_data)
        
        return {
            "text": text,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/voices")
async def get_voices():
    """Get available TTS voices."""
    if not elevenlabs_tts:
        raise HTTPException(status_code=503, detail="TTS service not available")
    
    try:
        voices = await elevenlabs_tts.get_voices()
        return voices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tts/models")
async def get_tts_models():
    """Get available TTS models."""
    if not elevenlabs_tts:
        raise HTTPException(status_code=503, detail="TTS service not available")
    
    try:
        models = await elevenlabs_tts.get_models()
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Password management endpoints
@app.post("/api/users/{user_id}/contexts/{context}/password")
async def set_context_password(user_id: str, context: str, request: Dict[str, str]):
    """Set or update password for a private context."""
    password = request.get("password")
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")
    
    if context not in ["personal", "private"]:
        raise HTTPException(status_code=400, detail="Password can only be set for personal/private contexts")
    
    success = private_auth.set_password(user_id, context, password)
    if success:
        return {"success": True, "message": "Password set successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to set password")

@app.delete("/api/users/{user_id}/contexts/{context}/password")
async def remove_context_password(user_id: str, context: str):
    """Remove password protection from a private context."""
    success = private_auth.remove_password(user_id, context)
    if success:
        return {"success": True, "message": "Password removed successfully"}
    else:
        return {"success": False, "message": "No password was set"}

@app.post("/api/users/{user_id}/contexts/{context}/password/verify")
async def verify_context_password(user_id: str, context: str, request: Dict[str, str]):
    """Verify password for a private context."""
    password = request.get("password")
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")
    
    if private_auth.verify_password(user_id, context, password):
        session_id = private_auth.create_session(user_id, context)
        return {
            "success": True,
            "auth_session_id": session_id,
            "message": "Password verified successfully"
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid password")

@app.get("/api/users/{user_id}/contexts/{context}/password/status")
async def get_password_status(user_id: str, context: str):
    """Check if password is required for a context."""
    return {
        "password_required": private_auth.is_password_required(user_id, context),
        "context": context,
        "user_id": user_id
    }

@app.put("/api/users/{user_id}/contexts/{context}/password/toggle")
async def toggle_password_protection(user_id: str, context: str, request: Dict[str, bool]):
    """Enable or disable password protection without removing the password."""
    enabled = request.get("enabled", True)
    success = private_auth.enable_password_protection(user_id, context, enabled)
    
    if success:
        return {
            "success": True,
            "enabled": enabled,
            "message": f"Password protection {'enabled' if enabled else 'disabled'}"
        }
    else:
        raise HTTPException(status_code=404, detail="No password set for this context")

# Real-time Voice WebSocket Endpoints
@app.websocket("/ws/voice/{session_id}")
async def voice_websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time voice communication"""
    if not voice_manager:
        await websocket.close(code=4000, reason="Voice system not available")
        return
    
    try:
        await websocket.accept()
        
        # Wait for initialization message
        init_message = await websocket.receive_text()
        init_data = json.loads(init_message)
        
        user_id = init_data.get("user_id")
        context = init_data.get("context", "general")
        mode = init_data.get("mode", "assistant")
        auth_session_id = init_data.get("auth_session_id")
        
        if not user_id:
            await websocket.close(code=4001, reason="User ID required")
            return
        
        # Initialize voice session
        if eva_voice_workflow:
            try:
                session_info = await eva_voice_workflow.start_voice_session(
                    session_id=session_id,
                    user_id=user_id,
                    context=context,
                    mode=mode,
                    auth_session_id=auth_session_id
                )
                
                await websocket.send_text(json.dumps({
                    "type": "session_initialized",
                    "data": session_info
                }))
                
            except PermissionError as e:
                await websocket.close(code=4003, reason="Authentication required")
                return
            except Exception as e:
                await websocket.close(code=4002, reason=f"Initialization error: {str(e)}")
                return
        
        # Connect to voice manager
        await voice_manager.connect_voice_session(websocket, session_id, user_id, context, mode)
        
        # Handle messages
        while True:
            try:
                message = await websocket.receive_text()
                await voice_manager.handle_websocket_message(session_id, message)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket error: {e}")
                await voice_manager.send_voice_event(session_id, "error", {
                    "message": f"Communication error: {str(e)}"
                })
                break
    
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    
    finally:
        # Cleanup
        if voice_manager:
            await voice_manager.disconnect_voice_session(session_id)
        if eva_voice_workflow:
            await eva_voice_workflow.end_voice_session(session_id)

@app.get("/api/voice/sessions")
async def get_voice_sessions():
    """Get list of active voice sessions"""
    if not eva_voice_workflow:
        raise HTTPException(status_code=503, detail="Voice system not available")
    
    sessions = eva_voice_workflow.list_active_sessions()
    return {"active_sessions": sessions}

@app.get("/api/voice/sessions/{session_id}")
async def get_voice_session_info(session_id: str):
    """Get information about a specific voice session"""
    if not eva_voice_workflow:
        raise HTTPException(status_code=503, detail="Voice system not available")
    
    session_info = eva_voice_workflow.get_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session_info

@app.post("/api/voice/sessions/{session_id}/interrupt")
async def interrupt_voice_session(session_id: str):
    """Interrupt ongoing voice processing"""
    if not eva_voice_workflow:
        raise HTTPException(status_code=503, detail="Voice system not available")
    
    result = await eva_voice_workflow.handle_interruption(session_id)
    return result

if __name__ == "__main__":
    import uvicorn
    # Force reload environment variables
    from importlib import reload
    import os as os_module
    reload(os_module)
    load_dotenv(override=True)
    
    # Re-read the model
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    print(f"Starting with model: {OPENAI_MODEL}")
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("eva:app", host="0.0.0.0", port=port, reload=False)