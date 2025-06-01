# EVA Agent Project

An intelligent AI assistant with voice capabilities and contextual memory.

## Project Structure

```
eva_agent/
├── core/               # Core EVA agent files
├── voice/              # Voice interface scripts  
├── integrations/       # External service integrations
├── utils/              # Utility scripts and helpers
├── scripts/            # Standalone scripts and tools
├── tests/              # Test files
├── docs/               # Documentation
├── configs/            # Configuration files
├── logs/               # Log files
├── static/             # Web interface files
├── voice_recordings/   # Secure voice recordings (private)
└── venv/               # Python virtual environment
```

## Quick Start

1. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Start EVA server:
   ```bash
   python core/eva.py
   ```

3. **Text Chat Options:**
   ```bash
   # Pure text chat (fastest)
   python eva_chat.py
   
   # Text chat + TTS (voice responses)
   python eva_chat_tts.py
   ```

4. Alternative interfaces:
   - **CLI Client:** `python utils/cli_client.py`
   - **Web Interface:** Open `http://localhost:8000` in browser
   - **Voice Interface:** `python voice/claude_voice_direct_fixed.py`

## Key Features

- 💬 **Working Text Chat** with GPT-4.1 (eva_chat.py)
- 🔊 **Text Chat + TTS** with ElevenLabs voices (eva_chat_tts.py) 
- 🎤 Voice interaction with speech recognition
- 🧠 Contextual memory with Zep integration
- 🔐 Secure voice recording storage
- 🌐 Web interface
- 🤖 Multiple personality modes (friend|assistant|coach|tutor)
- 🎯 Context switching (work|personal|creative|research)

## Documentation

See the `docs/` directory for detailed documentation.
