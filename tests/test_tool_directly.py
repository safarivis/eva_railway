#!/usr/bin/env python3
"""
Test the tool manager directly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from integrations.tool_manager import get_tool_manager, ToolCall

async def main():
    print("Testing tool manager directly...")
    
    tool_manager = get_tool_manager()
    
    # Test email send
    result = await tool_manager.call_tool(
        ToolCall(
            tool="email",
            action="send",
            parameters={
                "to": ["louisrdup@gmail.com"],
                "subject": "Test from Eva Tool Manager",
                "body": "This email was sent directly through the tool manager!"
            }
        )
    )
    
    print(f"\nResult: {result.success}")
    print(f"Details: {result.result if result.success else result.error}")

if __name__ == "__main__":
    asyncio.run(main())