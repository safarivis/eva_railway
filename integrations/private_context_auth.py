import hashlib
import secrets
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
from pathlib import Path

class PrivateContextAuth:
    """Manages password protection for private/personal contexts."""
    
    def __init__(self, auth_file: str = ".eva_private_auth.json"):
        """Initialize the authentication manager."""
        self.auth_file = Path(auth_file)
        self.auth_data: Dict[str, Any] = self._load_auth_data()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(hours=24)  # Sessions expire after 24 hours
        
    def _load_auth_data(self) -> Dict[str, Any]:
        """Load authentication data from file."""
        if self.auth_file.exists():
            try:
                with open(self.auth_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_auth_data(self):
        """Save authentication data to file."""
        try:
            with open(self.auth_file, 'w') as f:
                json.dump(self.auth_data, f, indent=2)
            # Set restrictive permissions (owner read/write only)
            os.chmod(self.auth_file, 0o600)
        except Exception as e:
            print(f"Error saving auth data: {e}")
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash a password with salt."""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Use PBKDF2 with SHA256
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        return key.hex(), salt
    
    def set_password(self, user_id: str, context: str, password: str) -> bool:
        """Set or update password for a user's private context."""
        if context not in ["personal", "private"]:
            return False
        
        key = f"{user_id}_{context}"
        hashed_password, salt = self._hash_password(password)
        
        self.auth_data[key] = {
            "password_hash": hashed_password,
            "salt": salt,
            "created_at": datetime.now().isoformat(),
            "enabled": True
        }
        
        self._save_auth_data()
        return True
    
    def verify_password(self, user_id: str, context: str, password: str) -> bool:
        """Verify password for a user's private context."""
        key = f"{user_id}_{context}"
        
        if key not in self.auth_data:
            return True  # No password set, allow access
        
        auth_info = self.auth_data[key]
        if not auth_info.get("enabled", True):
            return True  # Password protection disabled
        
        stored_hash = auth_info["password_hash"]
        salt = auth_info["salt"]
        
        provided_hash, _ = self._hash_password(password, salt)
        return provided_hash == stored_hash
    
    def create_session(self, user_id: str, context: str) -> str:
        """Create an authenticated session."""
        session_id = secrets.token_urlsafe(32)
        
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "context": context,
            "created_at": datetime.now(),
            "last_access": datetime.now()
        }
        
        # Clean up expired sessions
        self._cleanup_expired_sessions()
        
        return session_id
    
    def verify_session(self, session_id: str, user_id: str, context: str) -> bool:
        """Verify if a session is valid and active."""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        
        # Check if session matches user and context
        if session["user_id"] != user_id or session["context"] != context:
            return False
        
        # Check if session has expired
        if datetime.now() - session["created_at"] > self.session_timeout:
            del self.active_sessions[session_id]
            return False
        
        # Update last access time
        session["last_access"] = datetime.now()
        return True
    
    def invalidate_session(self, session_id: str):
        """Invalidate a session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions."""
        now = datetime.now()
        expired_sessions = [
            sid for sid, session in self.active_sessions.items()
            if now - session["created_at"] > self.session_timeout
        ]
        
        for sid in expired_sessions:
            del self.active_sessions[sid]
    
    def is_password_required(self, user_id: str, context: str) -> bool:
        """Check if password is required for a context."""
        if context not in ["personal", "private"]:
            return False
        
        key = f"{user_id}_{context}"
        if key not in self.auth_data:
            return False
        
        return self.auth_data[key].get("enabled", True)
    
    def enable_password_protection(self, user_id: str, context: str, enabled: bool = True) -> bool:
        """Enable or disable password protection."""
        key = f"{user_id}_{context}"
        
        if key not in self.auth_data:
            return False
        
        self.auth_data[key]["enabled"] = enabled
        self._save_auth_data()
        return True
    
    def remove_password(self, user_id: str, context: str) -> bool:
        """Remove password protection entirely."""
        key = f"{user_id}_{context}"
        
        if key in self.auth_data:
            del self.auth_data[key]
            self._save_auth_data()
            
            # Invalidate all sessions for this user/context
            sessions_to_remove = [
                sid for sid, session in self.active_sessions.items()
                if session["user_id"] == user_id and session["context"] == context
            ]
            for sid in sessions_to_remove:
                del self.active_sessions[sid]
            
            return True
        return False