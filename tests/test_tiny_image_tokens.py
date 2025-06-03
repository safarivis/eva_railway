#!/usr/bin/env python3
"""
Test token usage of different image sizes with OpenAI Vision API
"""
import asyncio
import base64
import os
import sys
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.eva import get_agent_response_with_image
from core.eva import active_conversations

def estimate_image_tokens(image_path):
    """Estimate tokens for an image (rough calculation)"""
    # OpenAI Vision API: roughly 85 tokens per 512x512 tile
    # For smaller images, it's more efficient
    size = os.path.getsize(image_path)
    
    # Very rough estimation based on file size
    if size < 1000:  # < 1KB
        return "~50-100 tokens"
    elif size < 3000:  # < 3KB
        return "~100-200 tokens"
    elif size < 10000:  # < 10KB
        return "~200-500 tokens"
    else:
        return "~500+ tokens"

async def test_image_sizes():
    """Test different image sizes with EVA"""
    print("🧪 Testing different image sizes for LLM vision...")
    
    # Create test session
    session_id = "test_image_sizes"
    active_conversations[session_id] = {
        "messages": [],
        "context": "general", 
        "mode": "assistant"
    }
    
    # Test different image sizes
    test_images = [
        "/home/ldp/eva/media/eva_micro.jpg",        # ~833 bytes
        "/home/ldp/eva/media/eva_tiny.jpg",         # ~2.7KB
        "/home/ldp/eva/media/eva_small.jpeg",       # ~42KB
        "/home/ldp/eva/media/eva.jpeg"              # ~95KB
    ]
    
    print(f"📊 Image Size Comparison:")
    print("=" * 60)
    
    for image_path in test_images:
        if os.path.exists(image_path):
            size = os.path.getsize(image_path)
            tokens = estimate_image_tokens(image_path)
            filename = os.path.basename(image_path)
            
            print(f"📁 {filename}")
            print(f"   Size: {size:,} bytes ({size/1024:.1f} KB)")
            print(f"   Est. Tokens: {tokens}")
            print()
        else:
            print(f"❌ {image_path} not found")
    
    # Test the micro image with EVA
    micro_image = "/home/ldp/eva/media/eva_micro.jpg"
    if os.path.exists(micro_image):
        print("🔬 Testing micro image with EVA...")
        
        # Read and encode image
        with open(micro_image, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()
        
        # Create vision message
        user_message = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What do you see in this image? Please describe it briefly."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}",
                        "detail": "low"  # Use low detail for efficiency
                    }
                }
            ]
        }
        
        try:
            response = await get_agent_response_with_image(
                session_id, 
                user_message,
                detail="low"
            )
            
            print(f"✅ EVA's response to micro image:")
            print(f"'{response}'")
            
        except Exception as e:
            print(f"❌ Error testing micro image: {e}")

async def main():
    print("🖼️  Testing ultra-tiny images for LLM efficiency")
    print("=" * 50)
    
    await test_image_sizes()
    
    print("=" * 50)
    print("💡 Recommendations:")
    print("   - Use _micro.jpg (64px, ~833 bytes) for maximum efficiency")
    print("   - Use _tiny.jpg (128px, ~2.7KB) for better quality")
    print("   - Always use 'detail': 'low' for small images")
    print("   - Micro images use ~50-100 tokens vs 1000+ for full size")

if __name__ == "__main__":
    asyncio.run(main())