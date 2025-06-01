#!/usr/bin/env python3
"""
Test Voice Dictation - Simple GUI to test nerd-dictation
"""

import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import os

class VoiceDictationTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Voice Dictation Test")
        self.root.geometry("600x400")
        
        # Create GUI elements
        self.create_widgets()
        
        # Track dictation state
        self.is_dictating = False
        self.dictation_process = None
        
    def create_widgets(self):
        # Instructions
        instructions = tk.Label(
            self.root,
            text="Click 'Start' to begin voice dictation, 'Stop' to end",
            font=("Arial", 12)
        )
        instructions.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Start button
        self.start_btn = tk.Button(
            button_frame,
            text="🎤 Start Dictation",
            command=self.start_dictation,
            bg="green",
            fg="white",
            font=("Arial", 14),
            padx=20,
            pady=10
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # Stop button
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹ Stop Dictation",
            command=self.stop_dictation,
            bg="red",
            fg="white",
            font=("Arial", 14),
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            font=("Arial", 10),
            fg="gray"
        )
        self.status_label.pack()
        
        # Text area
        self.text_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            width=60,
            height=15,
            font=("Arial", 11)
        )
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Clear button
        clear_btn = tk.Button(
            self.root,
            text="Clear Text",
            command=lambda: self.text_area.delete(1.0, tk.END)
        )
        clear_btn.pack(pady=5)
        
    def start_dictation(self):
        """Start nerd-dictation"""
        model_path = os.path.expanduser("~/.config/nerd-dictation/vosk-model-small-en-us-0.15")
        
        if not os.path.exists(model_path):
            self.status_label.config(text="Error: Voice model not found. Run setup_voice_dictation.sh first!", fg="red")
            return
            
        self.is_dictating = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="🔴 Recording... Speak now!", fg="red")
        
        # Start nerd-dictation in a separate thread
        def run_dictation():
            try:
                cmd = ["nerd-dictation", "begin", "--vosk-model-dir", model_path]
                self.dictation_process = subprocess.Popen(cmd)
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Error: {str(e)}", fg="red"
                ))
                self.root.after(0, self.stop_dictation)
        
        thread = threading.Thread(target=run_dictation)
        thread.start()
        
    def stop_dictation(self):
        """Stop nerd-dictation"""
        self.is_dictating = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Ready", fg="gray")
        
        # Stop nerd-dictation
        try:
            subprocess.run(["nerd-dictation", "end"], check=True)
        except Exception as e:
            self.status_label.config(text=f"Error stopping: {str(e)}", fg="red")
            
        # Terminate the process if it's still running
        if self.dictation_process:
            self.dictation_process.terminate()
            self.dictation_process = None
            
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

def main():
    print("🎤 Voice Dictation Test")
    print("======================")
    print("This will test nerd-dictation with a simple GUI")
    print()
    print("Requirements:")
    print("1. nerd-dictation must be installed (yay -S nerd-dictation-git)")
    print("2. Voice model must be downloaded (run setup_voice_dictation.sh)")
    print()
    print("Starting GUI...")
    
    app = VoiceDictationTest()
    app.run()

if __name__ == "__main__":
    main()