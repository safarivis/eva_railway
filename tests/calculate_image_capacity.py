#!/usr/bin/env python3
"""
Calculate how many tiny images EVA can process at once based on token limits
"""
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def estimate_image_tokens(image_size_bytes, detail="low"):
    """
    Estimate tokens for an image based on OpenAI Vision API pricing
    
    OpenAI Vision token calculation:
    - Base cost: 85 tokens
    - For images <= 512x512 with detail="low": ~85 tokens
    - For tiny images (64px): even less, approximately 50-100 tokens
    """
    if detail == "low":
        # Low detail images use fewer tokens
        if image_size_bytes < 1000:  # < 1KB (our micro images)
            return 50  # Very conservative estimate for micro images
        elif image_size_bytes < 3000:  # < 3KB 
            return 85  # Standard low-detail cost
        else:
            return 170  # Larger images with low detail
    else:
        # High detail images use more tokens based on 512x512 tiles
        return 170 + (image_size_bytes // 10000) * 85  # Rough estimate

def calculate_capacity():
    """Calculate EVA's image processing capacity"""
    
    # EVA's context limits
    model_limits = {
        "gpt-4.1": {
            "context_window": 128000,  # 128k tokens
            "practical_limit": 100000,  # Leave room for response and system prompt
        },
        "gpt-4o": {
            "context_window": 128000,
            "practical_limit": 100000,
        },
        "gpt-4-turbo": {
            "context_window": 128000,
            "practical_limit": 100000,
        }
    }
    
    # System prompt and conversation overhead
    system_prompt_tokens = 1500  # Eva's personality + tool instructions
    conversation_overhead = 500   # Previous messages, formatting, etc.
    response_buffer = 2000       # Space for Eva's response
    
    available_tokens = model_limits["gpt-4.1"]["practical_limit"] - system_prompt_tokens - conversation_overhead - response_buffer
    
    print("🧠 EVA's Token Capacity Analysis")
    print("=" * 50)
    print(f"Model: gpt-4.1")
    print(f"Total context window: {model_limits['gpt-4.1']['context_window']:,} tokens")
    print(f"System prompt: ~{system_prompt_tokens:,} tokens")
    print(f"Conversation overhead: ~{conversation_overhead:,} tokens")
    print(f"Response buffer: ~{response_buffer:,} tokens")
    print(f"Available for images: ~{available_tokens:,} tokens")
    print()
    
    # Check tiny images folder
    tiny_images_dir = "/home/ldp/eva/media/eva/tiny_images"
    if os.path.exists(tiny_images_dir):
        images = [f for f in os.listdir(tiny_images_dir) if f.endswith('.jpg')]
        total_images = len(images)
        
        # Calculate average size
        total_size = 0
        for img in images[:10]:  # Sample first 10
            img_path = os.path.join(tiny_images_dir, img)
            total_size += os.path.getsize(img_path)
        
        avg_size = total_size // min(10, len(images))
        
        print("📁 Tiny Images Analysis")
        print(f"Total tiny images: {total_images}")
        print(f"Average size: {avg_size:,} bytes ({avg_size/1024:.1f} KB)")
        print()
        
        # Token calculations for different scenarios
        scenarios = [
            {"detail": "low", "tokens_per_image": 50, "name": "Ultra-efficient (micro images, low detail)"},
            {"detail": "low", "tokens_per_image": 85, "name": "Conservative (low detail standard)"},
            {"detail": "auto", "tokens_per_image": 120, "name": "Balanced (auto detail)"},
        ]
        
        print("🖼️  Image Capacity Scenarios")
        print("-" * 50)
        
        for scenario in scenarios:
            tokens_per_image = scenario["tokens_per_image"]
            max_images = available_tokens // tokens_per_image
            percentage = (max_images / total_images) * 100 if total_images > 0 else 0
            
            print(f"\n{scenario['name']}:")
            print(f"  Tokens per image: {tokens_per_image}")
            print(f"  Max images at once: {max_images}")
            print(f"  Percentage of collection: {percentage:.1f}%")
            
            if max_images < total_images:
                batches_needed = (total_images + max_images - 1) // max_images
                print(f"  Batches needed for all images: {batches_needed}")
        
        print()
        print("💡 Recommendations:")
        print(f"  • Use detail='low' for maximum capacity")
        print(f"  • Process in batches of ~{available_tokens // 50} images for ultra-efficiency")
        print(f"  • Can analyze entire collection in ~{(total_images + (available_tokens // 50) - 1) // (available_tokens // 50)} batches")
        print(f"  • Perfect for bulk image analysis and comparison tasks!")
        
    else:
        print("❌ Tiny images folder not found")

if __name__ == "__main__":
    calculate_capacity()