#!/bin/bash

echo "🎤 Voice Dictation Test"
echo "======================"
echo ""
echo "This will open a text editor to test voice input"
echo ""
echo "Instructions:"
echo "1. A text editor will open"
echo "2. Tap RIGHT CTRL to start voice dictation"
echo "3. Speak clearly (e.g., 'Hello world, this is a test')"
echo "4. Tap RIGHT CTRL again to stop"
echo "5. Your words should appear in the editor"
echo ""
echo "Press ENTER to start the test..."
read

# Open a simple text editor
if command -v gedit &> /dev/null; then
    gedit --new-window &
elif command -v kate &> /dev/null; then
    kate --new &
elif command -v mousepad &> /dev/null; then
    mousepad &
elif command -v leafpad &> /dev/null; then
    leafpad &
else
    # Fallback to terminal editor
    echo "TEST YOUR VOICE HERE:" > /tmp/voice_test.txt
    echo "" >> /tmp/voice_test.txt
    nano /tmp/voice_test.txt
fi

echo ""
echo "💡 Quick test phrases to try:"
echo "- 'Create a Python function that calculates fibonacci numbers'"
echo "- 'Add a new React component for user authentication'"
echo "- 'Write a bash script to backup my documents'"