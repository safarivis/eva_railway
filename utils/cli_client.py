"""
Simple CLI client for interacting with Eva agent.
"""

import sys
import json
import uuid
import asyncio
import aiohttp
from typing import List, Dict, Any
import argparse

BASE_URL = "http://localhost:8000"  # Update if your server is on a different URL

async def start_conversation(initial_message: str) -> str:
    """Start a new conversation with Eva and return the run_id."""
    async with aiohttp.ClientSession() as session:
        payload = {
            "messages": [
                {"role": "user", "content": initial_message}
            ],
            "stream": True
        }
        
        async with session.post(f"{BASE_URL}/agents/eva/runs", json=payload) as response:
            if response.status != 200:
                print(f"Error starting conversation: {await response.text()}")
                sys.exit(1)
                
            data = await response.json()
            return data["run_id"]

async def stream_events(run_id: str):
    """Stream events from the Eva agent and print them."""
    print("\nEva is thinking...\n")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/agents/eva/runs/{run_id}/events") as response:
            if response.status != 200:
                print(f"Error streaming events: {await response.text()}")
                return
            
            current_status = None
            full_message = ""
            
            # Process the event stream
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if not line:
                    continue
                
                try:
                    # Parse the event data
                    event_data = json.loads(line)
                    event_type = event_data.get("event_type")
                    data = event_data.get("data", {})
                    
                    # Handle different event types
                    if event_type == "agent.status":
                        new_status = data.get("status")
                        if new_status != current_status:
                            current_status = new_status
                    
                    elif event_type == "agent.thinking":
                        # Just show the thinking indicator
                        pass
                    
                    elif event_type == "agent.message":
                        message = data.get("message", {})
                        content = message.get("content", "")
                        is_partial = message.get("is_partial", False)
                        
                        if is_partial:
                            # For partial messages, print without newline
                            print(content, end="", flush=True)
                            full_message += content
                        else:
                            # For complete messages, print the whole thing
                            if not full_message:
                                print(content)
                            full_message = content
                    
                    elif event_type == "agent.error":
                        error = data.get("error", "Unknown error")
                        print(f"\nError: {error}")
                
                except json.JSONDecodeError:
                    continue
                
                # If we're done processing (waiting for input or completed)
                if current_status == "waiting_for_input" or current_status == "succeeded":
                    break
            
            print("\n")  # Add a newline after Eva's response
            return current_status

async def send_message(run_id: str, message: str):
    """Send a message to an ongoing conversation."""
    async with aiohttp.ClientSession() as session:
        payload = {"input": message}
        
        async with session.post(f"{BASE_URL}/agents/eva/runs/{run_id}/input", json=payload) as response:
            if response.status != 200:
                print(f"Error sending message: {await response.text()}")
                return False
                
            return True

async def interactive_session(initial_message: str = None):
    """Run an interactive session with the Eva agent."""
    print("Welcome to Eva Agent CLI")
    print("Type 'exit' or 'quit' to end the conversation")
    
    if initial_message:
        user_input = initial_message
    else:
        user_input = input("\nYou: ")
    
    if user_input.lower() in ["exit", "quit"]:
        return
    
    # Start the conversation
    run_id = await start_conversation(user_input)
    
    # Stream initial response
    status = await stream_events(run_id)
    
    # Continue conversation until user exits
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ["exit", "quit"]:
            break
        
        # Send the message
        success = await send_message(run_id, user_input)
        
        if success:
            # Stream the response
            status = await stream_events(run_id)
        else:
            print("Failed to send message. Starting a new conversation.")
            run_id = await start_conversation(user_input)
            status = await stream_events(run_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI client for Eva agent")
    parser.add_argument("--message", "-m", help="Initial message to send to Eva")
    args = parser.parse_args()
    
    try:
        asyncio.run(interactive_session(args.message))
    except KeyboardInterrupt:
        print("\nExiting Eva CLI...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")