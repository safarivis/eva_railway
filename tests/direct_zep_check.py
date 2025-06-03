#!/usr/bin/env python
"""
Direct Zep memory access script - uses the raw Zep API client
"""

import os
import asyncio
from dotenv import load_dotenv
from zep_cloud.client import AsyncZep

async def main():
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    zep_api_key = os.getenv("ZEP_API_KEY")
    if not zep_api_key:
        print("ZEP_API_KEY not found in environment variables")
        return
        
    # Create direct Zep client
    client = AsyncZep(api_key=zep_api_key)
    
    try:
        print("=== DIRECT ZEP MEMORY ACCESS ===")
        
        # List all sessions
        print("\nListing all sessions...")
        sessions_response = await client.memory.list_sessions()
        
        if hasattr(sessions_response, 'sessions') and sessions_response.sessions:
            sessions = sessions_response.sessions
            print(f"Found {len(sessions)} sessions in Zep:")
            
            for i, session in enumerate(sessions, 1):
                print(f"\n--- Session {i}: {session.session_id} ---")
                print(f"User ID: {session.user_id}")
                print(f"Created: {session.created_at}")
                print(f"Updated: {session.updated_at}")
                
                # Get memory for this session
                try:
                    memory = await client.memory.get(session.session_id)
                    if memory:
                        print(f"Summary: {memory.summary if hasattr(memory, 'summary') else 'No summary'}")
                        if hasattr(memory, 'context') and memory.context:
                            print(f"Context: {memory.context[:200]}..." if len(memory.context) > 200 else memory.context)
                        
                        # Get messages for this session using the correct method
                        try:
                            if hasattr(memory, 'messages') and memory.messages:
                                messages = memory.messages
                                print(f"Messages: {len(messages)} found")
                                for j, msg in enumerate(messages[:5], 1):  # Show first 5 messages
                                    print(f"  Message {j}:")
                                    print(f"    Role: {msg.role} ({msg.role_type})")
                                    print(f"    Content: {msg.content[:100]}..." if len(msg.content) > 100 else msg.content)
                            else:
                                print("No messages found in memory object")
                        except Exception as e:
                            print(f"Error getting messages: {e}")
                    else:
                        print("No memory found")
                except Exception as e:
                    print(f"Error getting memory: {e}")
                    
                # Try to search this session using correct method
                try:
                    search_results = await client.memory.search_sessions(
                        text="conversation",
                        session_ids=[session.session_id],
                        limit=3
                    )
                    if search_results:
                        print(f"Search results: {len(search_results)} found")
                        for j, result in enumerate(search_results, 1):
                            print(f"  Result {j}: {result.content[:100]}..." if len(result.content) > 100 else result.content)
                    else:
                        print("No search results found")
                except Exception as e:
                    print(f"Error searching: {e}")
        else:
            print("No sessions found in Zep")
            
    except Exception as e:
        print(f"Error accessing Zep API: {e}")
    finally:
        # Close the client
        if hasattr(client, 'close'):
            await client.close()

if __name__ == "__main__":
    asyncio.run(main())
