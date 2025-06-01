#!/usr/bin/env python3

"""
Simple audio test to verify microphone works
"""

import speech_recognition as sr
import os

# Set audio device explicitly
os.environ['PULSE_RUNTIME_PATH'] = '/tmp/pulse'

def test_microphone():
    r = sr.Recognizer()
    
    print("Available microphones:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  {index}: {name}")
    
    # Try using the USB microphone (card 0)
    try:
        mic = sr.Microphone(device_index=0)  # USB Condenser Microphone
        print(f"\nUsing microphone: {sr.Microphone.list_microphone_names()[0]}")
        
        with mic as source:
            print("Adjusting for ambient noise... please wait")
            r.adjust_for_ambient_noise(source, duration=2)
            print("Say something!")
            
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            
        print("Attempting to recognize...")
        text = r.recognize_google(audio)
        print(f"You said: {text}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Trying default microphone...")
        
        # Fallback to default
        try:
            with sr.Microphone() as source:
                print("Using default microphone")
                r.adjust_for_ambient_noise(source, duration=1)
                print("Say something!")
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            
        except Exception as e2:
            print(f"Default microphone also failed: {e2}")

if __name__ == "__main__":
    test_microphone()