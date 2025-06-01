# EVA Voice Interface Guide

## Getting Started

### Prerequisites
- EVA server running on http://localhost:8000
- Python virtual environment activated
- Required packages installed (scipy, sounddevice, numpy, pygame, pynput)

### Available Voice Interfaces

EVA offers multiple voice interface options:

1. **Natural Voice Coding Interface** (Recommended)
   - Wake word activation ("Hey Eva")
   - Push-to-talk mode (Space key)
   - Seamless voice interaction for coding tasks
   - Run with: `python natural_voice_coding.py`

2. **Push-to-Talk Simplified**
   - Press Enter to start/stop recording
   - Simple and reliable
   - Run with: `python eva_ptt_simplified.py`

3. **Web-based Voice Interface**
   - Browser-based solution
   - Uses browser's speech recognition API
   - Access at: http://localhost:8000/static/voice_always_on.html
   - Alternative: http://localhost:8000/static/test_voice_simple.html

## Using the Natural Voice Coding Interface

### Starting the Interface
```bash
cd ~/louisdup/agents/eva_agent
source venv/bin/activate
python natural_voice_coding.py
```

### Wake Word Mode
1. Say "Hey Eva" to activate
2. Speak your question or command
3. The interface will automatically stop recording when you finish speaking
4. EVA will process your request and respond

### Push-to-Talk Mode
1. Press TAB to switch to push-to-talk mode
2. Press and hold SPACE while speaking
3. Release SPACE when done
4. EVA will process your request and respond

### Exiting the Interface
- Press ESC key to exit

## Tracking and Monitoring

### Terminal Output
The voice interface provides real-time feedback:
- "👂 Listening for wake word 'Hey Eva'..." - Waiting for activation
- "🎯 Wake word detected!" - When it hears "Hey Eva"
- "🎤 Recording..." - When it's capturing your voice
- "🔍 Transcribing audio..." - When processing your speech
- "💬 You: [transcription]" - Shows what it heard you say
- "📤 Sending to EVA: [message]" - Confirms sending to EVA
- "🤖 EVA: [response]" - Shows EVA's text response

### Log Files
- `eva.log` - Main EVA server log
- `eva_fixed.log` - Additional server log
- Audio recordings are saved as WAV files with timestamps

### Checking Server Status
```bash
# Check if EVA server is running
ps aux | grep "python eva.py" | grep -v grep

# Check if voice interface is running
ps aux | grep "natural_voice_coding.py" | grep -v grep
```

## Troubleshooting

### Audio Issues
1. **Microphone not detected**
   - Check system audio settings
   - Try a different microphone
   - Run `python -m sounddevice` to list available devices

2. **Wake word not detected**
   - Speak louder or closer to microphone
   - Switch to push-to-talk mode (press TAB)
   - Adjust microphone sensitivity in system settings

3. **Transcription errors**
   - Speak clearly and at a moderate pace
   - Use push-to-talk mode for more control
   - Check if Whisper is installed properly

### Connection Issues
1. **Cannot connect to EVA server**
   - Ensure EVA server is running (`python eva.py`)
   - Check server logs (`tail -f eva.log`)
   - Verify server is running on http://localhost:8000

2. **Slow responses**
   - Check network connection
   - Verify API keys are set correctly
   - Check server load and resources

## Example Voice Commands

### General Coding
- "Hey Eva, explain how to implement authentication in a Next.js app"
- "Hey Eva, write a Python function to sort a list of dictionaries by a specific key"
- "Hey Eva, create a React component for a responsive navigation bar"

### Debugging
- "Hey Eva, debug this error: TypeError cannot read property of undefined"
- "Hey Eva, what causes a segmentation fault in C++"
- "Hey Eva, how to fix CORS issues in a web application"

### Learning
- "Hey Eva, explain how async/await works in JavaScript"
- "Hey Eva, what are the best practices for React hooks"
- "Hey Eva, teach me about database indexing"

## Advanced Configuration

### Customizing the Voice Interface
Edit `natural_voice_coding.py` to change:
- Wake word sensitivity
- Silence detection parameters
- Audio recording quality
- Context and mode settings

### Using with Different LLMs
The voice interface works with any LLM supported by EVA:
- Claude (default)
- GPT-4
- Local models

### Adding Custom Commands
You can extend the voice interface with custom commands by modifying the code.

## Tips for Best Results

1. **Environment**
   - Use in a quiet environment
   - Position microphone properly
   - Close other audio applications

2. **Speaking Style**
   - Speak clearly and at a moderate pace
   - Use natural language
   - Be specific about programming languages and frameworks

3. **Command Structure**
   - Start with a clear action verb
   - Specify language/framework when relevant
   - Provide context for your question

4. **Follow-up Questions**
   - Reference previous questions when needed
   - Use pronouns naturally
   - Ask for clarification if needed
