#!/usr/bin/env python3
"""
Eva Logger - Comprehensive logging system with audit trails
Tracks all requests, responses, errors, and tool executions
"""

import os
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import asyncio
from collections import deque

class EvaLogger:
    """Centralized logging system for Eva with audit trails"""
    
    def __init__(self, log_dir: str = "logs/eva"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Different log files for different purposes
        self.files = {
            "requests": self.log_dir / f"requests_{datetime.now().strftime('%Y%m%d')}.log",
            "errors": self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log",
            "tools": self.log_dir / f"tools_{datetime.now().strftime('%Y%m%d')}.log",
            "audit": self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log",
            "performance": self.log_dir / f"performance_{datetime.now().strftime('%Y%m%d')}.log"
        }
        
        # Setup formatters
        self.setup_loggers()
        
        # In-memory buffer for recent logs (last 1000 entries)
        self.recent_logs = deque(maxlen=1000)
        
        # Session tracking
        self.active_sessions = {}
        
    def setup_loggers(self):
        """Setup different loggers for different purposes"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Request logger
        self.request_logger = logging.getLogger('eva.requests')
        self.request_logger.setLevel(logging.INFO)
        request_handler = logging.FileHandler(self.files['requests'])
        request_handler.setFormatter(formatter)
        self.request_logger.addHandler(request_handler)
        
        # Error logger
        self.error_logger = logging.getLogger('eva.errors')
        self.error_logger.setLevel(logging.ERROR)
        error_handler = logging.FileHandler(self.files['errors'])
        error_handler.setFormatter(formatter)
        self.error_logger.addHandler(error_handler)
        
        # Tool logger
        self.tool_logger = logging.getLogger('eva.tools')
        self.tool_logger.setLevel(logging.DEBUG)
        tool_handler = logging.FileHandler(self.files['tools'])
        tool_handler.setFormatter(formatter)
        self.tool_logger.addHandler(tool_handler)
        
        # Audit logger
        self.audit_logger = logging.getLogger('eva.audit')
        self.audit_logger.setLevel(logging.INFO)
        audit_handler = logging.FileHandler(self.files['audit'])
        audit_handler.setFormatter(formatter)
        self.audit_logger.addHandler(audit_handler)
        
        # Performance logger
        self.perf_logger = logging.getLogger('eva.performance')
        self.perf_logger.setLevel(logging.INFO)
        perf_handler = logging.FileHandler(self.files['performance'])
        perf_handler.setFormatter(formatter)
        self.perf_logger.addHandler(perf_handler)
    
    def log_request(self, session_id: str, user_message: str, context: Dict[str, Any] = None):
        """Log incoming user request"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "type": "user_request",
            "message": user_message,
            "context": context or {}
        }
        
        self.request_logger.info(json.dumps(log_entry))
        self.recent_logs.append(log_entry)
        self._write_audit_log("USER_REQUEST", session_id, {"message": user_message})
        
    def log_response(self, session_id: str, response: str, metadata: Dict[str, Any] = None):
        """Log Eva's response"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "type": "eva_response",
            "response": response,
            "metadata": metadata or {}
        }
        
        self.request_logger.info(json.dumps(log_entry))
        self.recent_logs.append(log_entry)
        self._write_audit_log("EVA_RESPONSE", session_id, {"response_length": len(response)})
        
    def log_tool_call(self, session_id: str, tool_name: str, action: str, parameters: Dict[str, Any], result: Any):
        """Log tool executions"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "type": "tool_call",
            "tool": tool_name,
            "action": action,
            "parameters": parameters,
            "result": str(result)[:500],  # Truncate large results
            "success": bool(result and hasattr(result, 'success') and result.success)
        }
        
        self.tool_logger.debug(json.dumps(log_entry))
        self.recent_logs.append(log_entry)
        self._write_audit_log("TOOL_CALL", session_id, {
            "tool": tool_name,
            "action": action,
            "success": log_entry["success"]
        })
        
    def log_error(self, session_id: str, error: Exception, context: Dict[str, Any] = None):
        """Log errors with full traceback"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {}
        }
        
        self.error_logger.error(json.dumps(log_entry))
        self.recent_logs.append(log_entry)
        self._write_audit_log("ERROR", session_id, {
            "error_type": log_entry["error_type"],
            "error_message": log_entry["error_message"]
        })
        
    def log_performance(self, session_id: str, operation: str, duration_ms: float, metadata: Dict[str, Any] = None):
        """Log performance metrics"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "type": "performance",
            "operation": operation,
            "duration_ms": duration_ms,
            "metadata": metadata or {}
        }
        
        self.perf_logger.info(json.dumps(log_entry))
        
        # Alert on slow operations
        if duration_ms > 5000:  # 5 seconds
            self._write_audit_log("SLOW_OPERATION", session_id, {
                "operation": operation,
                "duration_ms": duration_ms
            })
    
    def log_connection_error(self, session_id: str, error_details: str, context: Dict[str, Any] = None):
        """Specifically log connection errors"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "type": "connection_error",
            "error_details": error_details,
            "context": context or {}
        }
        
        self.error_logger.error(json.dumps(log_entry))
        self.recent_logs.append(log_entry)
        self._write_audit_log("CONNECTION_ERROR", session_id, {"details": error_details})
    
    def _write_audit_log(self, event_type: str, session_id: str, data: Dict[str, Any]):
        """Write to audit trail"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "session_id": session_id,
            "data": data
        }
        self.audit_logger.info(json.dumps(audit_entry))
    
    def get_recent_logs(self, count: int = 50, log_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent logs from memory buffer"""
        logs = list(self.recent_logs)
        
        if log_type:
            logs = [log for log in logs if log.get("type") == log_type]
        
        return logs[-count:]
    
    def get_session_logs(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all logs for a specific session"""
        return [log for log in self.recent_logs if log.get("session_id") == session_id]
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of recent errors"""
        recent_errors = [
            log for log in self.recent_logs 
            if log.get("type") in ["error", "connection_error"]
        ]
        
        error_types = {}
        for error in recent_errors:
            error_type = error.get("error_type", "connection_error")
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "total_errors": len(recent_errors),
            "error_types": error_types,
            "recent_errors": recent_errors[-10:]  # Last 10 errors
        }
    
    def search_logs(self, query: str, log_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search logs for specific content"""
        results = []
        for log in self.recent_logs:
            if log_type and log.get("type") != log_type:
                continue
            
            # Search in log content
            log_str = json.dumps(log).lower()
            if query.lower() in log_str:
                results.append(log)
        
        return results
    
    def export_logs(self, session_id: Optional[str] = None, export_path: Optional[str] = None) -> str:
        """Export logs to a file"""
        if not export_path:
            export_path = self.log_dir / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        logs_to_export = self.get_session_logs(session_id) if session_id else list(self.recent_logs)
        
        with open(export_path, 'w') as f:
            json.dump({
                "export_date": datetime.now().isoformat(),
                "session_id": session_id,
                "log_count": len(logs_to_export),
                "logs": logs_to_export
            }, f, indent=2)
        
        return str(export_path)

# Singleton instance
_eva_logger = None

def get_eva_logger() -> EvaLogger:
    """Get or create the Eva logger instance"""
    global _eva_logger
    if _eva_logger is None:
        _eva_logger = EvaLogger()
    return _eva_logger