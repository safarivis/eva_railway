import os
import uuid
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
from datetime import datetime
from zep_cloud.client import AsyncZep
from zep_cloud.types import Message
import logging

logger = logging.getLogger(__name__)

class MemoryContext(Enum):
    """Memory context types for separation of concerns."""
    WORK = "work"
    PERSONAL = "personal"
    CREATIVE = "creative"
    RESEARCH = "research"
    GENERAL = "general"

class AgentMode(Enum):
    """Agent operation modes that affect behavior and memory usage."""
    ASSISTANT = "assistant"  # General helpful assistant
    COACH = "coach"         # Life/career coaching mode
    TUTOR = "tutor"         # Educational/learning mode
    ADVISOR = "advisor"     # Professional advice mode
    FRIEND = "friend"       # Casual conversation mode
    ANALYST = "analyst"     # Data analysis mode
    CREATIVE = "creative"   # Creative writing/brainstorming

class ContextualMemoryManager:
    """Enhanced memory manager with context and mode separation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Zep client with API key."""
        self.api_key = api_key or os.environ.get('ZEP_API_KEY')
        if not self.api_key:
            raise ValueError("ZEP_API_KEY must be provided or set in environment")
        
        self.client = AsyncZep(api_key=self.api_key)
        self.sessions: Dict[str, Dict[str, Any]] = {}  # Enhanced session storage
        
    async def create_contextual_user(self, 
                                   base_user_id: str,
                                   context: MemoryContext,
                                   email: Optional[str] = None,
                                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a context-specific user profile."""
        # Create context-specific user ID
        user_id = f"{base_user_id}_{context.value}"
        
        try:
            # Check if user exists
            user = await self.client.user.get(user_id)
            logger.info(f"Retrieved existing user: {user_id}")
            return user_id
        except Exception:
            # Create new user with context metadata
            try:
                user_metadata = {
                    "context": context.value,
                    "base_user_id": base_user_id,
                    "created_at": datetime.now().isoformat()
                }
                if metadata:
                    user_metadata.update(metadata)
                    
                await self.client.user.add(
                    user_id=user_id,
                    email=email,
                    metadata=user_metadata
                )
                logger.info(f"Created new contextual user: {user_id}")
                return user_id
            except Exception as e:
                logger.error(f"Error creating user: {e}")
                raise
    
    async def create_contextual_session(self, 
                                      run_id: str,
                                      base_user_id: str,
                                      context: MemoryContext,
                                      mode: AgentMode,
                                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a session with context and mode awareness."""
        session_id = uuid.uuid4().hex
        
        try:
            # Create context-specific user
            user_id = await self.create_contextual_user(base_user_id, context)
            
            # Create session with rich metadata
            session_metadata = {
                "run_id": run_id,
                "context": context.value,
                "mode": mode.value,
                "created_at": datetime.now().isoformat()
            }
            if metadata:
                session_metadata.update(metadata)
                
            await self.client.memory.add_session(
                session_id=session_id,
                user_id=user_id,
                metadata=session_metadata
            )
            
            # Store enhanced session info
            self.sessions[run_id] = {
                "session_id": session_id,
                "user_id": user_id,
                "context": context,
                "mode": mode,
                "metadata": session_metadata
            }
            
            logger.info(f"Created contextual session {session_id} for {context.value}/{mode.value}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    async def add_contextual_messages(self, 
                                    run_id: str,
                                    messages: List[Dict[str, str]],
                                    enrich_with_context: bool = True):
        """Add messages with context enrichment."""
        session_info = self.sessions.get(run_id)
        if not session_info:
            logger.error(f"No session found for run_id: {run_id}")
            return
        
        session_id = session_info["session_id"]
        context = session_info["context"]
        mode = session_info["mode"]
        
        try:
            zep_messages = []
            for msg in messages:
                role = msg.get("role", "assistant")
                content = msg.get("content", "")
                
                # Enrich message with context if requested
                if enrich_with_context and role == "assistant":
                    message_metadata = {
                        "context": context.value,
                        "mode": mode.value,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    message_metadata = None
                
                # Map roles to Zep format
                if role == "user":
                    role_type = "user"
                    role_name = "User"
                else:
                    role_type = "assistant"
                    role_name = f"EVA_{mode.value}"
                
                zep_messages.append(Message(
                    role=role_name,
                    content=content,
                    role_type=role_type,
                    metadata=message_metadata
                ))
            
            await self.client.memory.add(session_id, messages=zep_messages)
            logger.info(f"Added {len(zep_messages)} contextual messages to session {session_id}")
            
        except Exception as e:
            logger.error(f"Error adding messages: {e}")
    
    async def get_contextual_memory(self, 
                                  run_id: str,
                                  include_cross_context: bool = False) -> Optional[str]:
        """Retrieve memory with optional cross-context awareness."""
        session_info = self.sessions.get(run_id)
        if not session_info:
            logger.error(f"No session found for run_id: {run_id}")
            return None
        
        try:
            # Get primary context memory
            memory = await self.client.memory.get(session_id=session_info["session_id"])
            context_str = memory.context if memory else ""
            
            # Optionally include related contexts
            if include_cross_context and session_info["context"] == MemoryContext.WORK:
                # For work context, might include some research context
                base_user_id = session_info["user_id"].split("_")[0]
                research_user_id = f"{base_user_id}_{MemoryContext.RESEARCH.value}"
                
                try:
                    # Get research context sessions
                    research_memory = await self._get_user_latest_memory(research_user_id)
                    if research_memory:
                        context_str += f"\n\n[Related Research Context]:\n{research_memory}"
                except Exception:
                    pass
            
            return context_str
            
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}")
            return None
    
    async def _get_user_latest_memory(self, user_id: str) -> Optional[str]:
        """Get the latest memory for a specific user."""
        try:
            # This would need to be implemented based on Zep's API
            # For now, returning None
            return None
        except Exception:
            return None
    
    async def switch_context(self, 
                           run_id: str,
                           new_context: MemoryContext,
                           new_mode: Optional[AgentMode] = None) -> str:
        """Switch to a different context/mode while preserving base user."""
        session_info = self.sessions.get(run_id)
        if not session_info:
            raise ValueError(f"No session found for run_id: {run_id}")
        
        # Extract base user ID
        base_user_id = session_info["user_id"].split("_")[0]
        
        # Use existing mode if not specified
        if new_mode is None:
            new_mode = session_info["mode"]
        
        # Create new session in new context
        new_session_id = await self.create_contextual_session(
            run_id=f"{run_id}_switched",
            base_user_id=base_user_id,
            context=new_context,
            mode=new_mode,
            metadata={"switched_from": run_id}
        )
        
        return new_session_id
    
    async def get_context_summary(self, base_user_id: str) -> Dict[str, Any]:
        """Get a summary of all contexts for a user."""
        summary = {}
        
        for context in MemoryContext:
            user_id = f"{base_user_id}_{context.value}"
            try:
                user = await self.client.user.get(user_id)
                # Get user's session count and last activity
                summary[context.value] = {
                    "exists": True,
                    "metadata": user.metadata if hasattr(user, 'metadata') else {}
                }
            except Exception:
                summary[context.value] = {
                    "exists": False,
                    "metadata": {}
                }
        
        return summary
    
    async def apply_mode_instructions(self, mode: AgentMode) -> str:
        """Get mode-specific instructions for the LLM."""
        mode_instructions = {
            AgentMode.ASSISTANT: "You are a helpful, professional assistant. Provide clear, actionable responses.",
            AgentMode.COACH: "You are a supportive life and career coach. Focus on empowerment, goal-setting, and personal growth. Ask reflective questions.",
            AgentMode.TUTOR: "You are an educational tutor. Break down complex topics, provide examples, and check understanding. Encourage learning.",
            AgentMode.ADVISOR: "You are a professional advisor. Provide expert analysis, consider risks and benefits, and give balanced recommendations.",
            AgentMode.FRIEND: "You are a friendly companion. Be casual, empathetic, and engaging. Show genuine interest in the conversation.",
            AgentMode.ANALYST: "You are a data analyst. Focus on facts, patterns, and insights. Provide structured analysis with clear conclusions.",
            AgentMode.CREATIVE: "You are a creative collaborator. Think outside the box, suggest innovative ideas, and encourage experimentation."
        }
        
        return mode_instructions.get(mode, mode_instructions[AgentMode.ASSISTANT])
    
    async def close(self):
        """Close the Zep client connection."""
        if hasattr(self.client, 'close'):
            await self.client.close()