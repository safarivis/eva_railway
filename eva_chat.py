#!/usr/bin/env python3
"""
EVA Chat - Simple text chat interface
No voice dependencies, just pure text chat with EVA
"""

import asyncio
import httpx
import sys
import base64
import os
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

async def chat_with_eva_image(image_data: str, context="general", mode="friend", message="What do you see in this image?", is_url=False, detail="auto"):
    """Send image to EVA and get response"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EVA_SERVER_URL}/api/chat-image",
                json={
                    "image_data": image_data,
                    "user_id": USER_ID,
                    "context": context,
                    "mode": mode,
                    "message": message,
                    "is_url": is_url,
                    "detail": detail
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "Sorry, I couldn't process that image.")
            else:
                return f"Error: {response.status_code}"
                
    except Exception as e:
        return f"Connection error: {e}"

async def main():
    print(f"{Colors.PURPLE}🤖 EVA Text Chat{Colors.RESET}")
    print(f"{Colors.YELLOW}Type 'exit' to quit{Colors.RESET}")
    print(f"{Colors.YELLOW}Type '/help' for all commands{Colors.RESET}\n")
    
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
            if user_input == '/help':
                print(f"\n{Colors.CYAN}📚 Available Commands:{Colors.RESET}")
                print(f"{Colors.GREEN}/context [work|personal|creative|research|general]{Colors.RESET} - Switch context")
                print(f"{Colors.GREEN}/mode [friend|assistant|coach|tutor|advisor|analyst|creative]{Colors.RESET} - Switch mode")
                print(f"{Colors.GREEN}/image <path_or_url> [message] [detail:low|high|auto]{Colors.RESET} - Analyze image")
                print(f"  Examples:")
                print(f"    /image photo.jpg")
                print(f"    /image https://example.com/photo.jpg What is this?")
                print(f"    /image photo.jpg 'Describe in detail' detail:high")
                print(f"{Colors.GREEN}exit, quit, bye{Colors.RESET} - Exit the chat\n")
                continue
                
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
            
            if user_input.startswith('/image '):
                parts = user_input.split(' ', 1)
                if len(parts) < 2:
                    print(f"{Colors.RED}Usage: /image <path_or_url> [message] [detail:low|high|auto]{Colors.RESET}")
                    print(f"{Colors.YELLOW}Examples:{Colors.RESET}")
                    print(f"  /image photo.jpg")
                    print(f"  /image https://example.com/photo.jpg What is this?")
                    print(f"  /image photo.jpg 'Describe in detail' detail:high")
                    continue
                    
                # Parse input
                remaining = parts[1]
                image_path = ""
                message = "What do you see in this image?"
                detail = "auto"
                is_url = False
                
                # Extract detail parameter if present
                if "detail:" in remaining:
                    detail_match = remaining.rfind("detail:")
                    detail_part = remaining[detail_match:].split()[0]
                    detail = detail_part.split(':')[1]
                    remaining = remaining[:detail_match].strip()
                
                # Parse path/URL and message
                if '"' in remaining:
                    # Handle quoted paths
                    if remaining.startswith('"'):
                        end_quote = remaining.find('"', 1)
                        if end_quote != -1:
                            image_path = remaining[1:end_quote]
                            message = remaining[end_quote+1:].strip() or message
                        else:
                            image_path = remaining.strip('"')
                    else:
                        image_path = remaining.split()[0]
                        message = ' '.join(remaining.split()[1:]) or message
                else:
                    # Simple path without quotes
                    path_parts = remaining.split(' ', 1)
                    image_path = path_parts[0]
                    message = path_parts[1] if len(path_parts) > 1 else message
                
                # Check if it's a URL
                if image_path.startswith(('http://', 'https://')):
                    is_url = True
                    print(f"{Colors.CYAN}Analyzing URL: {image_path}{Colors.RESET}")
                    print(f"{Colors.CYAN}Message: {message}{Colors.RESET}")
                    print(f"{Colors.CYAN}Detail level: {detail}{Colors.RESET}")
                    print(f"{Colors.GREEN}Eva: {Colors.RESET}", end="", flush=True)
                    
                    response = await chat_with_eva_image(image_path, context, mode, message, is_url=True, detail=detail)
                    print(response)
                    print()
                else:
                    # Local file
                    if not os.path.exists(image_path):
                        print(f"{Colors.RED}Image file not found: {image_path}{Colors.RESET}")
                        print(f"{Colors.YELLOW}Tip: Use absolute paths or relative paths from current directory{Colors.RESET}")
                        continue
                    
                    # Check if it's actually an image file
                    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
                    file_ext = os.path.splitext(image_path)[1].lower()
                    if file_ext not in valid_extensions:
                        print(f"{Colors.YELLOW}Warning: {file_ext} may not be a supported image format{Colors.RESET}")
                    
                    try:
                        with open(image_path, 'rb') as img_file:
                            img_data = base64.b64encode(img_file.read()).decode('utf-8')
                        
                        print(f"{Colors.CYAN}Analyzing image: {image_path}{Colors.RESET}")
                        print(f"{Colors.CYAN}Message: {message}{Colors.RESET}")
                        print(f"{Colors.CYAN}Detail level: {detail}{Colors.RESET}")
                        print(f"{Colors.GREEN}Eva: {Colors.RESET}", end="", flush=True)
                        
                        response = await chat_with_eva_image(img_data, context, mode, message, is_url=False, detail=detail)
                        print(response)
                        print()
                    except Exception as e:
                        print(f"{Colors.RED}Error reading image: {e}{Colors.RESET}")
                        import traceback
                        traceback.print_exc()
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