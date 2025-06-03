#!/usr/bin/env python3
"""
Test image generation fix - verify images are saved locally instead of blob URLs
"""
import asyncio
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.tool_manager import get_tool_manager, ToolCall

async def test_image_generation():
    """Test that image generation saves files locally"""
    print("🧪 Testing image generation fix...")
    
    # Get tool manager
    tool_manager = get_tool_manager()
    
    # Test image generation
    try:
        tool_call = ToolCall(
            tool="image",
            action="generate",
            parameters={
                "prompt": "A simple red circle on white background",
                "model": "dall-e-3",
                "n": 1,
                "size": "1024x1024",
                "quality": "standard"
            }
        )
        
        print(f"📤 Calling image tool with prompt: '{tool_call.parameters['prompt']}'")
        
        response = await tool_manager.call_tool(tool_call)
        
        print(f"✅ Tool response success: {response.success}")
        
        if response.success:
            result = response.result
            print(f"📊 Generated images: {result.get('count', 0)}")
            print(f"📂 Model used: {result.get('model', 'unknown')}")
            print(f"💬 Message: {result.get('message', '')}")
            
            # Check if images were saved locally
            images = result.get('images', [])
            for i, image in enumerate(images):
                if 'filepath' in image:
                    filepath = image['filepath']
                    print(f"📁 Image {i+1} saved to: {filepath}")
                    
                    # Check if file exists
                    if os.path.exists(filepath):
                        size_bytes = os.path.getsize(filepath)
                        print(f"✅ File exists and is {size_bytes} bytes")
                    else:
                        print(f"❌ File not found at {filepath}")
                elif 'url' in image:
                    print(f"⚠️  Image {i+1} still using URL: {image['url']}")
        else:
            print(f"❌ Tool call failed: {response.error}")
            
    except Exception as e:
        print(f"❌ Error testing image generation: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function"""
    print("🔧 Testing EVA image generation fix")
    print("=" * 50)
    
    await test_image_generation()
    
    print("=" * 50)
    print("✅ Test completed")

if __name__ == "__main__":
    asyncio.run(main())