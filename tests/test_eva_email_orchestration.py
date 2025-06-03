"""
Test script for Eva's email orchestration capabilities
Demonstrates how Eva can handle email requests through tool calls
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Eva's tool manager
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integrations.tool_manager import get_tool_manager, ToolCall, ToolType


async def test_email_operations():
    """Test various email operations through Eva's tool manager"""
    
    print("🤖 Eva Email Orchestration Test\n")
    
    # Get the tool manager
    tool_manager = get_tool_manager()
    
    print("Available tools:")
    for tool_name, tool_desc in tool_manager.tool_descriptions.items():
        print(f"  - {tool_name}: {tool_desc['description']}")
        for action, desc in tool_desc['actions'].items():
            print(f"    • {action}: {desc}")
    print()
    
    # Test 1: List emails
    print("📧 Test 1: List inbox emails")
    list_response = await tool_manager.call_tool(
        ToolCall(
            tool=ToolType.EMAIL.value,
            action="list",
            parameters={"limit": 5}
        )
    )
    print(f"Result: {list_response.success}")
    if list_response.success:
        print(f"Response: {list_response.result}")
    else:
        print(f"Error: {list_response.error}")
    print()
    
    # Test 2: Send email (will use Resend)
    print("📨 Test 2: Send email using Resend")
    send_response = await tool_manager.call_tool(
        ToolCall(
            tool=ToolType.EMAIL.value,
            action="send",
            parameters={
                "to": ["test@example.com"],
                "subject": "Test from Eva Agent",
                "body": "This is a test email sent by Eva using Resend API.",
                "from": "Eva Agent <eva@yourdomain.com>"
            }
        )
    )
    print(f"Result: {send_response.success}")
    if send_response.success:
        print(f"Response: {send_response.result}")
    else:
        print(f"Error: {send_response.error}")
    print()
    
    # Test 3: Search emails
    print("🔍 Test 3: Search emails")
    search_response = await tool_manager.call_tool(
        ToolCall(
            tool=ToolType.EMAIL.value,
            action="search",
            parameters={
                "query": "invoice",
                "limit": 3
            }
        )
    )
    print(f"Result: {search_response.success}")
    if search_response.success:
        print(f"Response: {search_response.result}")
    else:
        print(f"Error: {search_response.error}")
    print()
    
    # Test 4: Natural language processing simulation
    print("🗣️ Test 4: Simulating natural language request processing")
    nl_request = "Send an email to john@example.com about the meeting tomorrow"
    print(f"User request: '{nl_request}'")
    
    # In real Eva, this would use the LLM to parse the request
    # Here we're simulating what Eva would do
    parsed_calls = await tool_manager.process_natural_language_request(nl_request)
    print(f"Parsed tool calls: {parsed_calls}")
    print()
    
    # Test 5: File operations
    print("📁 Test 5: File operations")
    file_response = await tool_manager.call_tool(
        ToolCall(
            tool=ToolType.FILE.value,
            action="list",
            parameters={"path": "."}
        )
    )
    print(f"Result: {file_response.success}")
    if file_response.success:
        files = file_response.result.get("files", [])[:5]
        print(f"Files in current directory: {files}")
    else:
        print(f"Error: {file_response.error}")


async def test_eva_conversation():
    """Simulate a conversation with Eva that triggers tool calls"""
    
    print("\n💬 Simulating Eva Conversation with Tool Calls\n")
    
    # This shows how Eva would handle various user requests
    user_requests = [
        "Check my inbox for recent emails",
        "Send an email to team@company.com saying the project is complete",
        "Search for emails about invoices",
        "List files in the current directory"
    ]
    
    tool_manager = get_tool_manager()
    
    for request in user_requests:
        print(f"User: {request}")
        
        # In real Eva, the LLM would determine which tool to call
        # Here we're showing the expected behavior
        if "inbox" in request.lower():
            response = await tool_manager.call_tool(
                ToolCall(tool=ToolType.EMAIL.value, action="list", parameters={"limit": 5})
            )
            print(f"Eva: I'll check your inbox for you...")
            print(f"     {response.result if response.success else response.error}")
            
        elif "send" in request.lower() and "email" in request.lower():
            # Extract details (in real Eva, LLM would do this)
            response = await tool_manager.call_tool(
                ToolCall(
                    tool=ToolType.EMAIL.value,
                    action="send",
                    parameters={
                        "to": ["team@company.com"],
                        "subject": "Project Update",
                        "body": "The project is complete."
                    }
                )
            )
            print(f"Eva: I'll send that email for you...")
            print(f"     {response.result if response.success else response.error}")
            
        elif "search" in request.lower() and "email" in request.lower():
            response = await tool_manager.call_tool(
                ToolCall(
                    tool=ToolType.EMAIL.value,
                    action="search",
                    parameters={"query": "invoices", "limit": 5}
                )
            )
            print(f"Eva: I'll search for emails about invoices...")
            print(f"     {response.result if response.success else response.error}")
            
        elif "list files" in request.lower():
            response = await tool_manager.call_tool(
                ToolCall(
                    tool=ToolType.FILE.value,
                    action="list",
                    parameters={"path": "."}
                )
            )
            print(f"Eva: Here are the files in the current directory...")
            print(f"     {response.result if response.success else response.error}")
            
        print()


if __name__ == "__main__":
    print("=" * 60)
    print("Eva Agent - Email Orchestration Test")
    print("=" * 60)
    
    # Run tests
    asyncio.run(test_email_operations())
    asyncio.run(test_eva_conversation())
    
    print("\n✅ Tests complete!")
    print("\nNote: For production use, make sure to:")
    print("1. Set up RESEND_API_KEY in your .env file")
    print("2. Configure Gmail service URL (GMAIL_SERVICE_URL)")
    print("3. Run the Gmail agent service for non-send operations")
    print("4. Update email 'from' address to your verified domain")