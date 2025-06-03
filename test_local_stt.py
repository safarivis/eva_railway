#!/usr/bin/env python3
"""
Test local STT with faster-whisper
"""
import io
import wave
from faster_whisper import WhisperModel

def test_faster_whisper():
    """Test faster-whisper STT"""
    print("🎤 Testing faster-whisper STT...")
    
    try:
        # Initialize model (tiny for testing)
        print("Loading Whisper tiny model...")
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        print("✅ Model loaded successfully!")
        
        # Test with a dummy audio file path
        print("Model info:")
        print(f"  Device: cpu")
        print(f"  Compute type: int8")
        print("  Available models: tiny, base, small, medium, large-v3")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_faster_whisper()