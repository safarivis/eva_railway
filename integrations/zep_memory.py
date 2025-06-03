import os
import uuid
from typing import Optional, List, Dict, Any
from zep_cloud.client import AsyncZep
from zep_cloud.types import Message
import logging

logger = logging.getLogger(__name__)


class ZepMemoryManager:
    """Manages conversation memory using Zep's temporal knowledge graph."""
    
    def __init__(self, api_key: Optional[str] = None, session_persistence=None):
        """Initialize Zep client with API key from environment or parameter."""
        self.api_key = api_key or os.environ.get('ZEP_API_KEY')
        if not self.api_key:
            raise ValueError("ZEP_API_KEY must be provided or set in environment")
        
        self.client = AsyncZep(api_key=self.api_key)
        self.sessions: Dict[str, str] = {}  # run_id -> session_id mapping
        self.session_persistence = session_persistence
        
        # Load persisted session mappings if available
        if self.session_persistence:
            self._load_persisted_sessions()
    
    async def create_or_get_user(self, user_id: str, email: Optional[str] = None,
                                first_name: Optional[str] = None, 
                                last_name: Optional[str] = None) -> str:
        """Create or retrieve a user in Zep."""
        try:
            # Try to get existing user
            user = await self.client.user.get(user_id)
            logger.info(f"Retrieved existing user: {user_id}")
            return user_id
        except Exception:
            # Create new user if doesn't exist
            try:
                # Set default details for Lu if not provided
                if user_id == "lu_ldp_main" and not email:
                    email = "louisrdup@gmail.com"
                    first_name = "Louis"
                    last_name = "du Plessis"
                
                await self.client.user.add(
                    user_id=user_id,
                    email=email or f"{user_id}@example.com",
                    first_name=first_name or "User",
                    last_name=last_name or user_id
                )
                logger.info(f"Created new user: {user_id}")
                return user_id
            except Exception as e:
                logger.error(f"Error creating user: {e}")
                raise
    
    def _load_persisted_sessions(self):
        """Load persisted session mappings from storage."""
        if self.session_persistence:
            # This will be populated by the persistence layer
            logger.info("Session persistence enabled for Zep memory manager")
    
    async def create_or_get_session(self, run_id: str, user_id: str) -> str:
        """Create a new Zep session or get existing one for a conversation run."""
        # Check if we have a persisted session mapping
        if self.session_persistence:
            existing_session_id = self.session_persistence.get_zep_session_id(run_id)
            if existing_session_id:
                self.sessions[run_id] = existing_session_id
                logger.info(f"Restored existing Zep session {existing_session_id} for run {run_id}")
                return existing_session_id
        
        # Check in-memory cache
        if run_id in self.sessions:
            return self.sessions[run_id]
        
        # Create new session
        return await self.create_session(run_id, user_id)
    
    async def create_session(self, run_id: str, user_id: str) -> str:
        """Create a new Zep session for a conversation run."""
        session_id = uuid.uuid4().hex
        
        try:
            # Ensure user exists
            await self.create_or_get_user(user_id)
            
            # Create session
            await self.client.memory.add_session(
                session_id=session_id,
                user_id=user_id,
                metadata={"run_id": run_id}
            )
            
            self.sessions[run_id] = session_id
            logger.info(f"Created session {session_id} for run {run_id}")
            
            # Persist the mapping if persistence is enabled
            if self.session_persistence:
                self.session_persistence.save_zep_mapping(run_id, session_id)
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    async def add_messages(self, run_id: str, messages: List[Dict[str, str]]):
        """Add messages to a session's memory."""
        session_id = self.sessions.get(run_id)
        if not session_id:
            logger.error(f"No session found for run_id: {run_id}")
            return
        
        try:
            zep_messages = []
            for msg in messages:
                role = msg.get("role", "assistant")
                content = msg.get("content", "")
                
                # Map roles to Zep format
                if role == "user":
                    role_type = "user"
                    role_name = "User"
                else:
                    role_type = "assistant"
                    role_name = "EVA"
                
                zep_messages.append(Message(
                    role=role_name,
                    content=content,
                    role_type=role_type
                ))
            
            # Use add_memory instead of add
            await self.client.memory.add_memory(session_id, messages=zep_messages)
            logger.info(f"Added {len(zep_messages)} messages to session {session_id}")
            
        except Exception as e:
            logger.error(f"Error adding messages: {e}")
    
    async def get_memory_context(self, run_id: str) -> Optional[str]:
        """Retrieve memory context for a session."""
        session_id = self.sessions.get(run_id)
        if not session_id:
            logger.error(f"No session found for run_id: {run_id}")
            return None
        
        try:
            memory = await self.client.memory.get(session_id=session_id)
            if memory and memory.context:
                logger.info(f"Retrieved memory context for session {session_id}")
                return memory.context
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}")
            return None
    
    async def search_memory(self, run_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memory for relevant information."""
        session_id = self.sessions.get(run_id)
        if not session_id:
            logger.error(f"No session found for run_id: {run_id}")
            return []
        
        try:
            results = await self.client.memory.search_sessions(
                text=query,
                session_ids=[session_id],
                limit=limit
            )
            
            if results:
                logger.info(f"Found {len(results)} memory search results")
                return [
                    {
                        "content": r.content,
                        "score": r.score,
                        "metadata": r.metadata
                    }
                    for r in results
                ]
            return []
            
        except Exception as e:
            logger.error(f"Error searching memory: {e}")
            return []
    
    async def close(self):
        """Close the Zep client connection."""
        if hasattr(self.client, 'close'):
            await self.client.close()