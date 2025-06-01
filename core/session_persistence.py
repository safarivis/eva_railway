"""
Session persistence module for Eva Agent.
Handles saving and restoring session data between restarts.
"""

import json
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SessionPersistence:
    """Manages persistent storage of Eva's conversation sessions and Zep mappings."""
    
    def __init__(self, storage_dir: str = "data/sessions"):
        """Initialize session persistence with storage directory."""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.sessions_file = self.storage_dir / "active_sessions.json"
        self.zep_mappings_file = self.storage_dir / "zep_mappings.json"
        self.conversation_history_dir = self.storage_dir / "conversations"
        self.conversation_history_dir.mkdir(exist_ok=True)
        
        # In-memory caches
        self.sessions_cache: Dict[str, Dict[str, Any]] = {}
        self.zep_mappings_cache: Dict[str, str] = {}  # run_id -> zep_session_id
        
        # Load existing data on initialization
        self._load_sessions()
        self._load_zep_mappings()
    
    def _load_sessions(self):
        """Load active sessions from disk."""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r') as f:
                    data = json.load(f)
                    self.sessions_cache = data.get("sessions", {})
                    logger.info(f"Loaded {len(self.sessions_cache)} sessions from disk")
            except Exception as e:
                logger.error(f"Error loading sessions: {e}")
                self.sessions_cache = {}
    
    def _load_zep_mappings(self):
        """Load Zep session mappings from disk."""
        if self.zep_mappings_file.exists():
            try:
                with open(self.zep_mappings_file, 'r') as f:
                    self.zep_mappings_cache = json.load(f)
                    logger.info(f"Loaded {len(self.zep_mappings_cache)} Zep mappings from disk")
            except Exception as e:
                logger.error(f"Error loading Zep mappings: {e}")
                self.zep_mappings_cache = {}
    
    def save_session(self, session_id: str, session_data: Dict[str, Any]):
        """Save a session to persistent storage."""
        try:
            # Update cache
            self.sessions_cache[session_id] = {
                **session_data,
                "last_saved": datetime.now().isoformat()
            }
            
            # Save to disk
            self._persist_sessions()
            
            # Save conversation history separately for large conversations
            if "messages" in session_data and len(session_data["messages"]) > 10:
                self._save_conversation_history(session_id, session_data["messages"])
                
            logger.info(f"Saved session {session_id}")
        except Exception as e:
            logger.error(f"Error saving session {session_id}: {e}")
    
    def save_zep_mapping(self, run_id: str, zep_session_id: str):
        """Save Zep session mapping."""
        try:
            self.zep_mappings_cache[run_id] = zep_session_id
            self._persist_zep_mappings()
            logger.info(f"Saved Zep mapping: {run_id} -> {zep_session_id}")
        except Exception as e:
            logger.error(f"Error saving Zep mapping: {e}")
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a session from storage."""
        session = self.sessions_cache.get(session_id)
        
        # Load full conversation history if needed
        if session and "messages" not in session:
            messages = self._load_conversation_history(session_id)
            if messages:
                session["messages"] = messages
                
        return session
    
    def get_zep_session_id(self, run_id: str) -> Optional[str]:
        """Get Zep session ID for a run ID."""
        return self.zep_mappings_cache.get(run_id)
    
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a specific user."""
        user_sessions = []
        for session_id, session_data in self.sessions_cache.items():
            if session_data.get("base_user_id") == user_id or session_data.get("user_id") == user_id:
                user_sessions.append({
                    "session_id": session_id,
                    "context": session_data.get("context", "general"),
                    "mode": session_data.get("mode", "assistant"),
                    "created_at": session_data.get("created_at"),
                    "last_activity": session_data.get("last_saved"),
                    "message_count": len(session_data.get("messages", []))
                })
        return sorted(user_sessions, key=lambda x: x.get("last_activity", ""), reverse=True)
    
    def restore_recent_sessions(self, hours: int = 24) -> Dict[str, Dict[str, Any]]:
        """Restore sessions that were active within the specified hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        restored_sessions = {}
        
        for session_id, session_data in self.sessions_cache.items():
            last_saved = session_data.get("last_saved")
            if last_saved:
                try:
                    last_saved_dt = datetime.fromisoformat(last_saved)
                    if last_saved_dt > cutoff_time:
                        restored_sessions[session_id] = session_data
                        logger.info(f"Restored recent session: {session_id}")
                except Exception as e:
                    logger.error(f"Error parsing timestamp for session {session_id}: {e}")
                    
        return restored_sessions
    
    def cleanup_old_sessions(self, days: int = 30):
        """Remove sessions older than specified days."""
        cutoff_time = datetime.now() - timedelta(days=days)
        sessions_to_remove = []
        
        for session_id, session_data in self.sessions_cache.items():
            last_saved = session_data.get("last_saved")
            if last_saved:
                try:
                    last_saved_dt = datetime.fromisoformat(last_saved)
                    if last_saved_dt < cutoff_time:
                        sessions_to_remove.append(session_id)
                except Exception:
                    pass
        
        for session_id in sessions_to_remove:
            del self.sessions_cache[session_id]
            # Also remove conversation history
            history_file = self.conversation_history_dir / f"{session_id}.json"
            if history_file.exists():
                history_file.unlink()
                
        if sessions_to_remove:
            self._persist_sessions()
            logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")
    
    def _persist_sessions(self):
        """Save sessions cache to disk."""
        try:
            # Don't save full messages in main file for performance
            sessions_to_save = {}
            for session_id, session_data in self.sessions_cache.items():
                session_copy = session_data.copy()
                if "messages" in session_copy and len(session_copy["messages"]) > 10:
                    # Only keep last 10 messages in main file
                    session_copy["messages"] = session_copy["messages"][-10:]
                    session_copy["full_history_available"] = True
                sessions_to_save[session_id] = session_copy
                
            with open(self.sessions_file, 'w') as f:
                json.dump({"sessions": sessions_to_save}, f, indent=2)
        except Exception as e:
            logger.error(f"Error persisting sessions: {e}")
    
    def _persist_zep_mappings(self):
        """Save Zep mappings to disk."""
        try:
            with open(self.zep_mappings_file, 'w') as f:
                json.dump(self.zep_mappings_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error persisting Zep mappings: {e}")
    
    def _save_conversation_history(self, session_id: str, messages: List[Dict[str, str]]):
        """Save full conversation history to separate file."""
        try:
            history_file = self.conversation_history_dir / f"{session_id}.json"
            with open(history_file, 'w') as f:
                json.dump({"messages": messages}, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving conversation history for {session_id}: {e}")
    
    def _load_conversation_history(self, session_id: str) -> Optional[List[Dict[str, str]]]:
        """Load full conversation history from separate file."""
        try:
            history_file = self.conversation_history_dir / f"{session_id}.json"
            if history_file.exists():
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    return data.get("messages", [])
        except Exception as e:
            logger.error(f"Error loading conversation history for {session_id}: {e}")
        return None
    
    def export_user_data(self, user_id: str, export_dir: str):
        """Export all data for a specific user."""
        export_path = Path(export_dir) / f"eva_export_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        export_path.mkdir(parents=True, exist_ok=True)
        
        user_data = {
            "user_id": user_id,
            "export_date": datetime.now().isoformat(),
            "sessions": []
        }
        
        for session_id, session_data in self.sessions_cache.items():
            if session_data.get("base_user_id") == user_id or session_data.get("user_id") == user_id:
                # Get full conversation history
                messages = self._load_conversation_history(session_id) or session_data.get("messages", [])
                
                user_data["sessions"].append({
                    "session_id": session_id,
                    "context": session_data.get("context"),
                    "mode": session_data.get("mode"),
                    "created_at": session_data.get("created_at"),
                    "messages": messages
                })
        
        # Save export
        with open(export_path / "eva_conversations.json", 'w') as f:
            json.dump(user_data, f, indent=2)
            
        logger.info(f"Exported data for user {user_id} to {export_path}")
        return str(export_path)


# Singleton instance
_session_persistence = None

def get_session_persistence() -> SessionPersistence:
    """Get the singleton SessionPersistence instance."""
    global _session_persistence
    if _session_persistence is None:
        _session_persistence = SessionPersistence()
    return _session_persistence