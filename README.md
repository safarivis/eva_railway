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
- 📧 **Email Integration** with Resend API for sending emails
- 🛠️ **Tool System** with file operations and web search capabilities
- 🔐 Secure voice recording storage
- 🌐 Web interface
- 🤖 Multiple personality modes (friend|assistant|coach|tutor)
- 🎯 Context switching (work|personal|creative|research)

## Tool Integration

EVA now includes a powerful tool system for enhanced functionality:

### Email Tool (✅ Working)
- **Send emails** via Resend API
- **Usage**: Ask Eva to "send an email" or "use the email tool"
- **Configuration**: Requires `RESEND_API_KEY` environment variable
- **From address**: Uses Resend's verified domain (`onboarding@resend.dev`)
- **Supported recipients**: Any valid email address

### File Tool (✅ Available)
- **Read/write files** with security restrictions
- **List directories** within allowed paths
- **Security**: Limited to current working directory and subdirectories

### Web Search Tool (🔄 Placeholder)
- **Search capability** framework ready
- **Status**: Awaiting search API integration

## Tool Usage Examples

```bash
# Test email functionality
curl -X POST http://localhost:8000/api/chat-simple \
  -H "Content-Type: application/json" \
  -d '{"message": "use the email tool to send me a test email", "user_id": "test", "context": "general", "mode": "friend"}'

# File operations
curl -X POST http://localhost:8000/api/chat-simple \
  -H "Content-Type: application/json" \
  -d '{"message": "read the README.md file", "user_id": "test", "context": "general", "mode": "assistant"}'
```

## Environment Variables

```bash
# Required for email functionality
RESEND_API_KEY=your_resend_api_key

# Required for core functionality  
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4.1

# Optional for enhanced memory
ZEP_API_KEY=your_zep_api_key
ZEP_ENABLED=true

# Optional for voice features
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

## Documentation

See the `docs/` directory for detailed documentation.
