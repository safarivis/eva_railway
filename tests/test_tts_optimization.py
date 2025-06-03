#!/usr/bin/env python3
"""
Test TTS optimization and cost tracking
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.tts_cost_tracker import TTSCostTracker

async def test_tts_optimization():
    """Test TTS cost tracking and optimization"""
    print("💰 Testing TTS Cost Optimization...")
    
    # Initialize cost tracker
    tracker = TTSCostTracker()
    
    # Test 1: Track some sample TTS usage
    print("\n1️⃣ Testing cost tracking...")
    
    test_responses = [
        "Hey there! This is a short response.",  # ~40 chars
        "This is a longer response that goes into more detail about the topic and provides additional context that might be useful.",  # ~140 chars
        "This is an extremely long response that goes on and on with lots of details, explanations, and additional information that really should be shortened when TTS is enabled to save on ElevenLabs credits and keep costs down.",  # ~230 chars
    ]
    
    for i, response in enumerate(test_responses):
        usage = tracker.track_usage(response, f"test_session_{i}")
        print(f"Response {i+1}: {usage.character_count} chars, ${usage.estimated_cost:.4f}")
        print(f"  Preview: {usage.content_preview}")
    
    # Test 2: Check daily usage
    print("\n2️⃣ Testing daily usage tracking...")
    daily = tracker.get_daily_usage()
    print(f"Daily stats: {daily}")
    
    # Test 3: Check efficiency
    print("\n3️⃣ Testing efficiency analysis...")
    efficiency = tracker.get_character_efficiency_stats()
    print(f"Efficiency: {efficiency}")
    
    # Test 4: Check budget limits
    print("\n4️⃣ Testing budget limits...")
    limits = tracker.should_limit_tts()
    print(f"Budget status: {limits}")
    
    # Test 5: Test cost estimation
    print("\n5️⃣ Testing cost estimation...")
    
    voice_responses = [
        "Perfect!",  # Very short
        "Got it, working on that now.",  # Short
        "That's an interesting question. Let me think about it and get back to you with a detailed answer.",  # Long
    ]
    
    print("Cost estimates for different response lengths:")
    for response in voice_responses:
        cost = tracker.estimate_cost(response)
        print(f"  '{response[:50]}...' -> {len(response)} chars, ${cost:.4f}")
    
    # Test 6: Comprehensive summary
    print("\n6️⃣ Testing comprehensive summary...")
    summary = tracker.get_cost_summary()
    print(f"Cost summary: {summary}")
    
    print("\n✅ TTS optimization test completed!")
    
    # Recommendations
    print("\n💡 Recommendations for voice mode:")
    print("- Keep responses under 100 characters when possible")
    print("- Use punchy, direct language")
    print("- Avoid long explanations in voice mode")
    print("- Monitor daily budget usage via /api/tts/costs")

if __name__ == "__main__":
    asyncio.run(test_tts_optimization())