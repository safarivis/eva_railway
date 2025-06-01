#!/usr/bin/env python3
"""
EVA Chat - Simple text chat interface
No voice dependencies, just pure text chat with EVA
"""

import asyncio
import httpx
import sys
from datetime import datetime

# Configuration
EVA_SERVER_URL = "http://localhost:8000"
USER_ID = "text_user"

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

async def chat_with_eva(message: str, context="general", mode="friend"):
    """Send message to EVA and get response"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EVA_SERVER_URL}/api/chat-simple",
                json={
                    "message": message,
                    "user_id": USER_ID,
                    "context": context,
                    "mode": mode
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "Sorry, I couldn't process that.")
            else:
                return f"Error: {response.status_code}"
                
    except Exception as e:
        return f"Connection error: {e}"

async def main():
    print(f"{Colors.PURPLE}🤖 EVA Text Chat{Colors.RESET}")
    print(f"{Colors.YELLOW}Type 'exit' to quit{Colors.RESET}")
    print(f"{Colors.YELLOW}Type '/context work|personal|creative|research' to switch context{Colors.RESET}")
    print(f"{Colors.YELLOW}Type '/mode friend|assistant|coach|tutor' to switch mode{Colors.RESET}\n")
    
    # Test connection
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{EVA_SERVER_URL}/api/info", timeout=3.0)
            if resp.status_code == 200:
                info = resp.json()
                print(f"{Colors.GREEN}✅ Connected to EVA v{info['version']}{Colors.RESET}")
                print(f"{Colors.CYAN}Model: {info['model']}{Colors.RESET}\n")
    except:
        print(f"{Colors.RED}❌ Cannot connect to EVA!{Colors.RESET}")
        print(f"{Colors.YELLOW}Start EVA with: python core/eva.py{Colors.RESET}")
        return
    
    context = "general"
    mode = "friend"
    
    while True:
        try:
            # Get input
            user_input = input(f"{Colors.BLUE}You: {Colors.RESET}")
            
            # Check for exit
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print(f"{Colors.PURPLE}👋 Goodbye!{Colors.RESET}")
                break
            
            # Check for commands
            if user_input.startswith('/context '):
                new_context = user_input.split(' ', 1)[1]
                if new_context in ['work', 'personal', 'creative', 'research', 'general']:
                    context = new_context
                    print(f"{Colors.CYAN}Switched to {context} context{Colors.RESET}")
                continue
                
            if user_input.startswith('/mode '):
                new_mode = user_input.split(' ', 1)[1]
                if new_mode in ['friend', 'assistant', 'coach', 'tutor', 'advisor', 'analyst', 'creative']:
                    mode = new_mode
                    print(f"{Colors.CYAN}Switched to {mode} mode{Colors.RESET}")
                continue
            
            # Skip empty
            if not user_input.strip():
                continue
            
            # Send to EVA
            print(f"{Colors.GREEN}Eva: {Colors.RESET}", end="", flush=True)
            response = await chat_with_eva(user_input, context, mode)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print(f"\n{Colors.PURPLE}👋 Goodbye!{Colors.RESET}")
            break
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")

if __name__ == "__main__":
    asyncio.run(main())