#!/usr/bin/env python
"""
Script to check Zep memories for EVA agent
"""

import os
import asyncio
import json
from dotenv import load_dotenv
from zep_memory import ZepMemoryManager
from zep_context_manager import ContextualMemoryManager, MemoryContext

async def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize Zep memory managers
    try:
        # Get API key from environment
        zep_api_key = os.getenv("ZEP_API_KEY")
        if not zep_api_key:
            print("ZEP_API_KEY not found in environment variables")
            return
            
        memory_manager = ZepMemoryManager(api_key=zep_api_key)
        context_manager = ContextualMemoryManager(api_key=zep_api_key)
        
        print("=== ZEP MEMORY SUMMARY ===")
        print(f"Active sessions in memory manager: {memory_manager.sessions}")
        
        # Check active conversations in EVA
        print("\n=== ACTIVE CONVERSATIONS ===")
        
        # Try to get memory for some common contexts and session IDs
        # Using some common session ID patterns that might exist
        session_ids = [
            "voice_1717336000",  # Recent timestamp-based ID
            "chat_1717336000",   # Chat-based ID
            "user_general",      # User context-based ID
            "user_personal",     # Personal context
            "user_work"         # Work context
        ]
        
        found_memories = False
        
        for session_id in session_ids:
            try:
                print(f"\nChecking session: {session_id}")
                
                # Try to get memory context
                memory = await memory_manager.get_memory_context(session_id)
                
                if memory:
                    found_memories = True
                    print(f"Found memory for session {session_id}:")
                    print(f"Memory summary: {memory[:200]}..." if len(memory) > 200 else memory)
                else:
                    print(f"No memory found for session {session_id}")
                    
                # Try to search memory
                search_results = await memory_manager.search_memory(session_id, "conversation")
                if search_results:
                    found_memories = True
                    print(f"Found {len(search_results)} search results for session {session_id}")
                    for i, result in enumerate(search_results[:3], 1):  # Show top 3
                        print(f"  Result {i}: {result['content'][:100]}..." if len(result['content']) > 100 else result['content'])
                
            except Exception as e:
                print(f"Error checking session {session_id}: {e}")
        
        # Try to access direct client API
        print("\n=== TRYING DIRECT ZEP API ACCESS ===")
        try:
            # List all sessions
            print("Attempting to list all sessions...")
            sessions = await memory_manager.client.memory.list_sessions()
            
            if sessions:
                found_memories = True
                print(f"Found {len(sessions)} sessions in Zep:")
                for i, session in enumerate(sessions[:5], 1):  # Show top 5
                    print(f"  Session {i}: {session.session_id} (User: {session.user_id})")
                    # Get memory for this session
                    try:
                        memory = await memory_manager.client.memory.get(session.session_id)
                        if memory and memory.context:
                            print(f"    Context: {memory.context[:150]}..." if len(memory.context) > 150 else memory.context)
                    except Exception as e:
                        print(f"    Error getting memory: {e}")
            else:
                print("No sessions found in Zep")
                
        except Exception as e:
            print(f"Error accessing Zep API directly: {e}")
        
        if not found_memories:
            print("\nNo memories found in any session")
            print("This could mean:")
            print("1. No conversations have been saved yet")
            print("2. The Zep memory system is not properly configured")
            print("3. The session IDs used for testing don't match actual sessions")
        
    except Exception as e:
        print(f"Error accessing Zep memory: {e}")
    
if __name__ == "__main__":
    asyncio.run(main())
