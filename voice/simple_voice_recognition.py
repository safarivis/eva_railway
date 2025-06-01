#!/usr/bin/env python3

"""
Simple voice recognition using SpeechRecognition library
Alternative to RealtimeSTT that doesn't require torch
"""

import speech_recognition as sr
import time
from threading import Thread
import sys

class SimpleVoiceRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listening = False
        
        # Adjust for ambient noise
        print("Adjusting for ambient noise... Please be quiet.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        print("Ready for voice input!")
    
    def listen_continuously(self, callback):
        """Listen continuously for voice input"""
        self.listening = True
        
        def listen_loop():
            while self.listening:
                try:
                    # Listen for audio with a short timeout
                    with self.microphone as source:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    # Try to recognize speech
                    try:
                        text = self.recognizer.recognize_google(audio)
                        if text.strip():
                            callback(text)
                    except sr.UnknownValueError:
                        # Speech was unintelligible
                        pass
                    except sr.RequestError as e:
                        print(f"Could not request results from Google Speech Recognition service; {e}")
                        
                except sr.WaitTimeoutError:
                    # No speech detected within timeout, continue listening
                    pass
                except Exception as e:
                    print(f"Error in listen loop: {e}")
                    time.sleep(1)
        
        # Start listening in a separate thread
        listen_thread = Thread(target=listen_loop, daemon=True)
        listen_thread.start()
        return listen_thread
    
    def stop_listening(self):
        """Stop continuous listening"""
        self.listening = False
    
    def listen_once(self):
        """Listen for a single phrase and return the text"""
        try:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("Recognizing...")
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Error with recognition service: {e}")
            return None
        except sr.WaitTimeoutError:
            print("No speech detected")
            return None

def main():
    """Test the simple voice recognizer"""
    recognizer = SimpleVoiceRecognizer()
    
    def on_speech(text):
        print(f"You said: {text}")
        if "stop" in text.lower() or "quit" in text.lower():
            recognizer.stop_listening()
            print("Stopping...")
            sys.exit(0)
    
    print("Starting continuous listening. Say 'stop' or 'quit' to exit.")
    print("Press Ctrl+C to force exit.")
    
    try:
        thread = recognizer.listen_continuously(on_speech)
        
        # Keep the main thread alive
        while recognizer.listening:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping...")
        recognizer.stop_listening()

if __name__ == "__main__":
    main()