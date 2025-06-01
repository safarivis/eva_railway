# Voice Coding Integration for Claude Code

This document explains how to implement Speech-to-Text (STT) and Text-to-Speech (TTS) for natural language coding with Claude Code, based on research and the existing EVA agent voice architecture.

## Overview

The integration enables developers to:
- Use voice commands to write code
- Get spoken feedback from Claude
- Stay in the terminal while coding by voice
- Switch between different coding modes (command, explain, refactor, debug)

## Architecture

### Core Components

1. **Speech Recognition (STT)**
   - Google Speech Recognition for quick, accurate transcription
   - OpenAI Whisper API for advanced transcription
   - Voice Activity Detection (VAD) for automatic speech segmentation

2. **Text-to-Speech (TTS)**
   - ElevenLabs for natural voice synthesis
   - pyttsx3 as offline fallback
   - First-sentence speaking for quick feedback

3. **Command Processing**
   - Natural language parser to identify intent
   - Context-aware command interpretation
   - Mode-based processing (command/explain/refactor/debug/review)

4. **Claude Integration**
   - Direct API calls to Claude for code generation
   - Conversation history for context
   - Project and file context awareness

## Implementation

### Terminal Interface (`claude_code_terminal_voice.py`)

The terminal interface provides two modes:

1. **Push-to-Talk (Default)**
   ```bash
   python claude_code_terminal_voice.py
   # Hold CTRL and speak your command
   ```

2. **Wake Word Mode**
   ```bash
   python claude_code_terminal_voice.py --wake-word
   # Say "hey claude" followed by your command
   ```

### Voice Commands Examples

#### Code Generation
- "Create a function to validate email addresses"
- "Create a class for managing database connections"
- "Add a method to calculate total price"

#### Code Modification
- "Refactor this to use async await"
- "Rename user_data to user_profile"
- "Extract the validation logic into a separate method"

#### Testing & Debugging
- "Write unit tests for the authentication module"
- "Debug why this function returns null"
- "Add error handling to this function"

#### Documentation
- "Add documentation to all public methods"
- "Explain what this recursive function does"
- "Generate a README for this project"

### Integration with Claude Code

The voice interface can be integrated into Claude Code's workflow:

```python
# In Claude Code's main loop
from claude_code_terminal_voice import ClaudeCodeTerminalVoice

# Initialize voice interface
voice = ClaudeCodeTerminalVoice()

# Process voice command
command = voice.listen_command()
response = await voice.process_command(command)

# Execute the generated code or action
```

## Setup

### Requirements

```bash
pip install speech_recognition
pip install pyttsx3
pip install pygame
pip install sounddevice
pip install pynput
pip install anthropic
```

### Environment Variables

```bash
export ANTHROPIC_API_KEY="your-api-key"
export OPENAI_API_KEY="your-api-key"  # Optional, for Whisper
```

### Audio Setup

1. Ensure microphone permissions are granted
2. Test audio input: `python -m speech_recognition`
3. Adjust energy threshold if needed in the config

## Advanced Features

### Custom Wake Words
```python
config = TerminalVoiceConfig(
    use_wake_word=True,
    wake_word="hey claude"  # Customize this
)
```

### Context Injection
```python
# Set current file context
voice.set_file_context("/path/to/file.py", file_content)

# Update project context
voice.current_context["project"] = {
    "name": "my-project",
    "language": "python",
    "framework": "fastapi"
}
```

### Command Chaining
Voice commands can be chained for complex operations:
- "Create a FastAPI endpoint for user registration and add input validation"
- "Refactor this function to be async and add error handling"

## Integration Patterns

### 1. Direct Integration
```python
# Add to Claude Code's command processor
if command.startswith("voice:"):
    voice_command = command[6:]
    response = await voice.process_command(voice_command)
    return response
```

### 2. Plugin Architecture
```python
# Create a voice plugin for Claude Code
class VoicePlugin:
    def __init__(self, claude_code_instance):
        self.claude = claude_code_instance
        self.voice = ClaudeCodeTerminalVoice()
    
    async def handle_voice_input(self):
        command = self.voice.listen_command()
        code = await self.voice.process_command(command)
        return self.claude.execute_code(code)
```

### 3. Daemon Mode
Run voice interface as a background service that sends commands to Claude Code:
```bash
# Start voice daemon
python claude_code_voice_daemon.py &

# Commands are automatically sent to Claude Code
```

## Best Practices

1. **Clear Commands**: Use specific, action-oriented language
2. **Context First**: Set file/project context before complex commands
3. **Incremental Changes**: Make small, focused changes with each command
4. **Verify Output**: Always review generated code before execution
5. **Use Modes**: Switch modes based on task (explain vs. refactor)

## Troubleshooting

### Common Issues

1. **Microphone Not Detected**
   ```bash
   # List audio devices
   python -c "import sounddevice; print(sounddevice.query_devices())"
   ```

2. **Recognition Errors**
   - Adjust energy_threshold in config
   - Speak clearly and avoid background noise
   - Use push-to-talk for better control

3. **TTS Not Working**
   - Install system TTS: `sudo apt-get install espeak`
   - Disable TTS: `--no-tts` flag

## Future Enhancements

1. **Multi-language Support**: Detect and generate code in multiple programming languages
2. **Voice Shortcuts**: Custom voice commands for frequent operations
3. **Collaborative Mode**: Multiple developers using voice in same session
4. **IDE Integration**: Direct integration with VS Code, IntelliJ, etc.
5. **Continuous Mode**: Always-listening mode with smart activation

## Conclusion

Voice coding with Claude Code enables a more natural and efficient coding experience. The terminal-based approach keeps developers in their preferred environment while adding powerful voice capabilities. The modular architecture allows for easy customization and extension based on specific needs.