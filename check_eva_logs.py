#!/usr/bin/env python3
"""
Check Eva logs directly
"""

import httpx
import json
import sys
from datetime import datetime

def check_recent_logs(count=20, log_type=None):
    """Check recent logs"""
    url = "http://localhost:8000/api/logs/recent"
    params = {"count": count}
    if log_type:
        params["log_type"] = log_type
    
    try:
        response = httpx.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"\n📋 Recent Logs ({data['count']} entries):")
            print("=" * 80)
            
            for log in data['logs']:
                timestamp = log.get('timestamp', 'N/A')
                log_type = log.get('type', 'unknown')
                
                # Format based on log type
                if log_type == 'user_request':
                    print(f"\n🔵 USER REQUEST - {timestamp}")
                    print(f"   Session: {log.get('session_id', 'N/A')}")
                    print(f"   Message: {log.get('message', 'N/A')}")
                
                elif log_type == 'eva_response':
                    print(f"\n🟢 EVA RESPONSE - {timestamp}")
                    print(f"   Session: {log.get('session_id', 'N/A')}")
                    print(f"   Response: {log.get('response', 'N/A')[:100]}...")
                    if 'metadata' in log:
                        print(f"   Duration: {log['metadata'].get('duration_ms', 'N/A')}ms")
                
                elif log_type == 'tool_call':
                    print(f"\n🔧 TOOL CALL - {timestamp}")
                    print(f"   Tool: {log.get('tool', 'N/A')}")
                    print(f"   Action: {log.get('action', 'N/A')}")
                    print(f"   Success: {log.get('success', 'N/A')}")
                    if not log.get('success'):
                        print(f"   Result: {log.get('result', 'N/A')}")
                
                elif log_type in ['error', 'connection_error']:
                    print(f"\n🔴 ERROR - {timestamp}")
                    print(f"   Session: {log.get('session_id', 'N/A')}")
                    print(f"   Type: {log.get('error_type', log_type)}")
                    print(f"   Message: {log.get('error_message', log.get('error_details', 'N/A'))}")
                    if 'traceback' in log:
                        print(f"   Traceback: {log['traceback'][:200]}...")
                
                else:
                    print(f"\n⚫ {log_type.upper()} - {timestamp}")
                    print(f"   {json.dumps(log, indent=2)[:200]}...")
            
            print("\n" + "=" * 80)
        else:
            print(f"❌ Failed to get logs: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error connecting to Eva: {e}")
        print("Make sure Eva is running on http://localhost:8000")

def check_errors():
    """Check error summary"""
    url = "http://localhost:8000/api/logs/errors"
    
    try:
        response = httpx.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"\n🚨 Error Summary:")
            print("=" * 80)
            print(f"Total Errors: {data.get('total_errors', 0)}")
            
            error_types = data.get('error_types', {})
            if error_types:
                print("\nError Types:")
                for error_type, count in error_types.items():
                    print(f"  - {error_type}: {count}")
            
            recent_errors = data.get('recent_errors', [])
            if recent_errors:
                print(f"\nRecent Errors (last {len(recent_errors)}):")
                for error in recent_errors:
                    print(f"\n  🔴 {error.get('timestamp', 'N/A')}")
                    print(f"     Type: {error.get('error_type', 'N/A')}")
                    print(f"     Message: {error.get('error_message', 'N/A')}")
                    if 'context' in error:
                        print(f"     Context: {error['context']}")
            
            print("\n" + "=" * 80)
        else:
            print(f"❌ Failed to get error summary: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error connecting to Eva: {e}")

def search_logs(query):
    """Search logs for specific content"""
    url = "http://localhost:8000/api/logs/search"
    params = {"query": query}
    
    try:
        response = httpx.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"\n🔍 Search Results for '{query}':")
            print("=" * 80)
            print(f"Found {data['result_count']} matches")
            
            for log in data['results']:
                print(f"\n{log.get('type', 'unknown').upper()} - {log.get('timestamp', 'N/A')}")
                print(json.dumps(log, indent=2)[:300])
                print("...")
            
            print("\n" + "=" * 80)
        else:
            print(f"❌ Failed to search logs: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error connecting to Eva: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "errors":
            check_errors()
        elif command == "search" and len(sys.argv) > 2:
            search_logs(sys.argv[2])
        elif command == "tool":
            check_recent_logs(50, "tool_call")
        elif command == "connection":
            check_recent_logs(50, "connection_error")
        else:
            print(f"Unknown command: {command}")
            print("Usage:")
            print("  python check_eva_logs.py          # Show recent logs")
            print("  python check_eva_logs.py errors   # Show error summary")
            print("  python check_eva_logs.py tool     # Show tool calls")
            print("  python check_eva_logs.py connection # Show connection errors")
            print("  python check_eva_logs.py search 'query' # Search logs")
    else:
        # Default: show recent logs
        check_recent_logs()