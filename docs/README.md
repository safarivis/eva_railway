# Eva Agent

EVA is an advanced AI assistant agent with real-time voice capabilities, contextual memory, and secure private mode.

## 🚀 Features

- 🎤 **Real-time Voice Conversations** - Continuous listening with voice activity detection
- 🧠 **Contextual Memory** - Persistent conversations with Zep temporal knowledge graphs  
- 🔒 **Private Mode** - Password-protected personal context (`eva2415!`)
- 🎭 **Multiple Modes** - Assistant, Coach, Tutor, Advisor, Friend, Analyst, Creative
- 📂 **Context Separation** - Work, Personal, Creative, Research contexts
- 🌐 **Multi-Interface** - Web-based with real-time WebSocket streaming
- ⚡ **Low Latency** - Sub-second response times with interruption support
- 🔊 **Voice I/O** - ElevenLabs TTS + OpenAI Whisper STT
- 🎯 **AG-UI Protocol** - Standards-compliant agent communication

## 🎬 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API Key (for GPT-4 and Whisper)
- ElevenLabs API Key (for TTS)
- Zep API Key (for memory)

### Installation

1. **Clone and setup**:
```bash
git clone <repository>
cd eva_agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment** (`.env`):
```env
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ZEP_API_KEY=your_zep_api_key
OPENAI_MODEL=gpt-4-turbo-preview
ZEP_ENABLED=true
```

3. **Start EVA**:
```bash
python eva.py
```

## 🌐 Web Interfaces

### Real-time Voice Mode (Recommended)
**URL**: `http://localhost:8000/static/index_realtime_voice.html`

**Features**:
- Continuous voice conversation
- Voice activity detection
- Real-time streaming responses
- Context-aware memory
- Private mode with password protection

### Standard Voice Mode
**URL**: `http://localhost:8000/static/index_private.html`

**Features**:
- Push-to-talk voice input
- Voice responses
- Context selection
- Password protection

### Basic Chat
**URL**: `http://localhost:8000/`

**Features**:
- Text-only interface
- Streaming responses
- Basic functionality

## 🎤 Voice Conversation Flow

1. **Connect**: Open real-time voice interface
2. **Configure**: Select context (work/personal/etc.) and mode
3. **Authenticate**: Enter password for private contexts
4. **Start**: Click "Connect Voice" → "Start Listening"
5. **Speak**: EVA automatically detects when you speak
6. **Respond**: EVA processes and responds with voice
7. **Continue**: Seamless back-and-forth conversation
8. **Interrupt**: Stop EVA mid-response if needed

## 🔐 Private Mode

### Enable Private Mode
```
Password: eva2415!
→ Personal context becomes password-protected
→ All conversations encrypted and isolated
→ 24-hour secure sessions
```

### Usage
1. Select "Personal" context
2. Enter password when prompted
3. Secure conversation with EVA
4. Memory isolated from other contexts

## 🧠 Memory & Context System

### Contexts
- **General**: Default conversations
- **Work**: Professional discussions  
- **Personal**: Private matters (password-protected)
- **Creative**: Artistic projects and brainstorming
- **Research**: Learning and academic topics

### Modes
- **Assistant**: Professional, helpful responses
- **Coach**: Life coaching and personal development
- **Tutor**: Educational explanations and teaching
- **Advisor**: Business advice and recommendations
- **Friend**: Casual, empathetic conversations
- **Analyst**: Data analysis and insights
- **Creative**: Innovative thinking and ideation

### Memory Features
- **Persistent**: Conversations saved across sessions
- **Temporal**: Knowledge graphs track changes over time
- **Contextual**: Separate memory per context
- **Cross-reference**: Work context can reference research (configurable)

## 🛠 API Reference

### WebSocket Voice API
```
WS /ws/voice/{session_id}
```

**Initialize**:
```json
{
  "user_id": "user123",
  "context": "personal", 
  "mode": "coach",
  "auth_session_id": "optional"
}
```

**Send Audio**:
```json
{
  "type": "audio_chunk",
  "audio": "base64_encoded_audio"
}
```

### REST API Endpoints

**Password Management**:
```bash
POST /api/users/{user_id}/contexts/personal/password
DELETE /api/users/{user_id}/contexts/personal/password
GET /api/users/{user_id}/contexts/personal/password/status
```

**Voice Sessions**:
```bash
GET /api/voice/sessions
GET /api/voice/sessions/{session_id}
POST /api/voice/sessions/{session_id}/interrupt
```

**System Info**:
```bash
GET /api/info
GET /api/contexts
GET /api/voices
```

## 🏗 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│                 │    │                  │    │                 │
│   Web Browser   │◄──►│   EVA Server     │◄──►│   OpenAI API    │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                        │                       │
        │                        │                       │
   ┌────▼────┐              ┌────▼────┐             ┌────▼────┐
   │         │              │         │             │         │
   │WebSocket│              │   Zep   │             │ElevenLab│
   │ Voice   │              │ Memory  │             │   TTS   │
   │         │              │         │             │         │
   └─────────┘              └─────────┘             └─────────┘
```

### Core Components

- **FastAPI Server**: Web framework and API endpoints
- **WebSocket Handler**: Real-time voice communication
- **Voice Workflow**: EVA conversation management
- **Memory Manager**: Zep integration for persistent memory
- **Authentication**: Secure private context access
- **Audio Pipeline**: STT/TTS processing

## 🔧 Advanced Configuration

### Audio Settings
```python
# Voice Activity Detection
aggressiveness = 2        # 0-3, higher = more aggressive
sample_rate = 16000      # Hz, required for WebRTC VAD
frame_duration = 30      # ms, audio frame size
```

### Memory Settings
```python
# Session timeout
session_timeout = 24    # hours
# Cross-context sharing
enable_cross_context = True
```

### Performance Tuning
```python
# WebSocket chunk size
audio_chunk_ms = 100    # milliseconds
# LLM streaming
stream_responses = True
# Audio buffer size
buffer_frames = 50      # ~1.5 seconds
```

## 📚 Documentation

- **[Hybrid Voice System](HYBRID_VOICE_SYSTEM.md)** - Complete technical documentation
- **[Private Voice Mode](PRIVATE_VOICE_MODE.md)** - Password protection and voice features
- **[Contextual Memory](CONTEXTUAL_MEMORY.md)** - Memory and context system
- **[Zep Integration](ZEP_INTEGRATION.md)** - Memory layer setup

## 🐛 Troubleshooting

### Voice Issues
- **No microphone**: Check browser permissions
- **Poor audio**: Reduce background noise, check microphone quality
- **Connection failed**: Verify server is running, check network

### Memory Issues  
- **Not remembering**: Check Zep API key, verify context selection
- **Private access**: Ensure password is `eva2415!`

### Performance Issues
- **High latency**: Check network connection, server resources
- **Audio choppy**: Reduce audio quality, check bandwidth

## 🚀 Future Enhancements

- **Multi-language Support**: Automatic language detection
- **Voice Cloning**: Personalized TTS voices  
- **WebRTC Integration**: Peer-to-peer audio
- **Mobile App**: Native mobile interface
- **Team Collaboration**: Multi-user conversations
- **Plugin System**: Custom voice skills

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgements

- **OpenAI**: GPT-4, Whisper STT
- **ElevenLabs**: High-quality TTS
- **Zep**: Temporal knowledge graphs
- **AG-UI Protocol**: Agent communication standards
- **WebRTC**: Voice activity detection