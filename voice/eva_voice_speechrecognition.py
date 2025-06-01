#!/usr/bin/env python3

"""
EVA Voice Agent using SpeechRecognition instead of RealtimeSTT
Enhanced voice assistant with Claude integration
"""

import speech_recognition as sr
import pyttsx3
import threading
import time
import sys
import os
from datetime import datetime
import requests
import json

class EVAVoiceAgent:
    def __init__(self):
        # Speech recognition setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Text-to-speech setup
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Speed
        self.tts_engine.setProperty('volume', 0.9)  # Volume
        
        # Control flags
        self.listening = False
        self.wake_word = "eva"
        self.exit_phrases = ["goodbye eva", "exit", "quit", "stop listening"]
        
        # Initialize microphone
        self.initialize_microphone()
        
    def initialize_microphone(self):
        """Initialize and calibrate microphone"""
        print("Initializing microphone...")
        try:
            with self.microphone as source:
                print("Calibrating for ambient noise... Please be quiet for 2 seconds.")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print("Microphone ready!")
        except Exception as e:
            print(f"Error initializing microphone: {e}")
            sys.exit(1)
    
    def speak(self, text):
        """Convert text to speech"""
        print(f"EVA: {text}")
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")
    
    def listen_for_wake_word(self):
        """Listen for the wake word continuously"""
        print(f"Listening for wake word '{self.wake_word}'...")
        
        while True:
            try:
                with self.microphone as source:
                    # Listen with short timeout to avoid blocking
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                try:
                    text = self.recognizer.recognize_google(audio, language='en-US').lower()
                    if self.wake_word in text:
                        print(f"Wake word detected: {text}")
                        self.speak("Yes? How can I help you?")
                        return True
                        
                except sr.UnknownValueError:
                    # Speech was unintelligible, continue listening
                    pass
                except sr.RequestError as e:
                    print(f"Recognition service error: {e}")
                    time.sleep(1)
                    
            except sr.WaitTimeoutError:
                # No audio detected, continue
                pass
            except KeyboardInterrupt:
                print("\nShutting down...")
                return False
            except Exception as e:
                print(f"Unexpected error: {e}")
                time.sleep(1)
    
    def listen_for_command(self):
        """Listen for a command after wake word"""
        try:
            with self.microphone as source:
                print("Listening for command...")
                # Longer timeout for commands
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            text = self.recognizer.recognize_google(audio, language='en-US')
            print(f"Command received: {text}")
            return text
            
        except sr.UnknownValueError:
            self.speak("Sorry, I didn't understand that. Could you repeat?")
            return None
        except sr.RequestError as e:
            self.speak("Sorry, there was an error with the speech recognition service.")
            print(f"Recognition error: {e}")
            return None
        except sr.WaitTimeoutError:
            self.speak("I didn't hear anything. Try saying my name again.")
            return None
    
    def process_command(self, command):
        """Process the voice command"""
        if not command:
            return True
            
        command_lower = command.lower()
        
        # Check for exit phrases
        if any(phrase in command_lower for phrase in self.exit_phrases):
            self.speak("Goodbye! Have a great day!")
            return False
        
        # Time queries
        if "time" in command_lower:
            current_time = datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {current_time}")
            return True
        
        # Date queries
        if "date" in command_lower:
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            self.speak(f"Today is {current_date}")
            return True
        
        # Weather (mock response - you can integrate with weather API)
        if "weather" in command_lower:
            self.speak("I'm not connected to a weather service yet, but I can help you with other tasks.")
            return True
        
        # Calculator
        if any(word in command_lower for word in ["calculate", "math", "plus", "minus", "times", "divided"]):
            result = self.simple_calculator(command_lower)
            if result:
                self.speak(f"The answer is {result}")
            else:
                self.speak("I couldn't understand that calculation.")
            return True
        
        # Default response
        self.speak("I heard you say: " + command + ". I'm still learning new commands. Is there anything else I can help you with?")
        return True
    
    def simple_calculator(self, command):
        """Simple calculator functionality"""
        try:
            # Basic math operations
            if "plus" in command or "add" in command:
                numbers = [int(s) for s in command.split() if s.isdigit()]
                if len(numbers) >= 2:
                    return sum(numbers)
            
            elif "minus" in command or "subtract" in command:
                numbers = [int(s) for s in command.split() if s.isdigit()]
                if len(numbers) >= 2:
                    return numbers[0] - sum(numbers[1:])
            
            elif "times" in command or "multiply" in command:
                numbers = [int(s) for s in command.split() if s.isdigit()]
                if len(numbers) >= 2:
                    result = 1
                    for num in numbers:
                        result *= num
                    return result
            
            elif "divided" in command or "divide" in command:
                numbers = [int(s) for s in command.split() if s.isdigit()]
                if len(numbers) >= 2 and numbers[1] != 0:
                    return numbers[0] / numbers[1]
                    
        except Exception:
            pass
        return None
    
    def run(self):
        """Main run loop"""
        self.speak("Hello! I'm EVA, your voice assistant. Say my name to get started.")
        
        try:
            while True:
                # Listen for wake word
                if self.listen_for_wake_word():
                    # Listen for command
                    command = self.listen_for_command()
                    
                    # Process command
                    if not self.process_command(command):
                        break
                else:
                    break
                    
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.speak("Goodbye!")

def main():
    """Main function"""
    print("Starting EVA Voice Assistant with SpeechRecognition...")
    print("Press Ctrl+C to exit")
    
    eva = EVAVoiceAgent()
    eva.run()

if __name__ == "__main__":
    main()