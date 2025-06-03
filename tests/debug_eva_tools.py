"""
Debug Eva's tool calling
"""
import asyncio
from integrations.tool_manager import get_tool_manager, ToolCall

async def test_direct_tool_call():
    """Test calling the email tool directly"""
    
    print("🔍 Testing direct tool call to email service\n")
    
    tool_manager = get_tool_manager()
    
    # Test sending email
    print("1. Testing email send with Resend:")
    result = await tool_manager.call_tool(
        ToolCall(
            tool="email",
            action="send",
            parameters={
                "to": ["louisrdup@gmail.com"],
                "subject": "Test from Eva - Direct Tool Call",
                "body": "This is a test email sent directly through Eva's tool manager.",
                "from": "Eva Agent <onboarding@resend.dev>"
            }
        )
    )
    
    print(f"Success: {result.success}")
    print(f"Result: {result.result}")
    if result.error:
        print(f"Error: {result.error}")

if __name__ == "__main__":
    asyncio.run(test_direct_tool_call())