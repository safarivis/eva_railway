#!/usr/bin/env python3

"""
Test script to check if RealtimeSTT works with our current setup
"""

try:
    from RealtimeSTT import AudioToTextRecorder
    print("✓ RealtimeSTT imported successfully")
    
    # Try to create recorder instance
    recorder = AudioToTextRecorder()
    print("✓ AudioToTextRecorder created successfully")
    
    print("RealtimeSTT is ready to use!")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error creating recorder: {e}")
    print("This might be due to missing torch dependency")