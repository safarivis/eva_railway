# EVA Hybrid Voice System Documentation

## Overview

The EVA Hybrid Voice System combines the best of both worlds:
- **Web-based accessibility** with multi-user support
- **Real-time voice streaming** with OpenAI Agents SDK patterns
- **Context-aware conversations** with Zep memory integration
- **Password-protected private mode** for sensitive discussions

## Architecture

### Core Components

1. **WebSocket Infrastructure** (`realtime_voice.py`)
   - Real-time audio streaming via WebSocket
   - Voice Activity Detection (VAD) with WebRTC
   - Audio buffering and speech detection
   - Connection management

2. **Voice Workflow Adapter** (`eva_voice_workflow.py`)
   - Integrates with EVA's context system
   - Manages conversation flow
   - Handles authentication for private contexts
   - Streaming response generation

3. **Web Interface** (`index_realtime_voice.html`)
   - Real-time voice controls
   - Visual status indicators
   - Context and mode selection
   - Private mode management

4. **FastAPI Integration** (WebSocket endpoints in `eva.py`)
   - `/ws/voice/{session_id}` - Main voice WebSocket
   - `/api/voice/sessions` - Session management
   - `/api/voice/sessions/{session_id}/interrupt` - Interruption handling

## Features

### 🎯 Real-time Voice Pipeline

```
🎤 Audio Input → VAD → STT → EVA Processing → TTS → 🔊 Audio Output
```

1. **Voice Activity Detection**
   - Continuous audio monitoring
   - Automatic speech start/end detection
   - Noise filtering and echo cancellation

2. **Speech-to-Text (STT)**
   - OpenAI Whisper integration
   - Real-time transcription
   - Multiple language support

3. **EVA Processing**
   - Context-aware responses
   - Memory integration via Zep
   - Mode-specific behavior

4. **Text-to-Speech (TTS)**
   - ElevenLabs voice synthesis
   - Multiple voice options
   - Streaming audio response

### 🔒 Security & Privacy

- **Password Protection**: `eva2415!` enables/disables private mode
- **Session Authentication**: 24-hour secure sessions
- **Context Isolation**: Personal context completely separate
- **Encrypted Communication**: WebSocket with TLS support

### 🧠 Memory & Context

- **Persistent Memory**: Zep temporal knowledge graphs
- **Context Separation**: Work/Personal/Creative/Research/General
- **Mode-Based Behavior**: Assistant/Coach/Tutor/Advisor/Friend/Analyst/Creative
- **Cross-Context Awareness**: Optional memory sharing

### ⚡ Performance

- **Low Latency**: Direct WebSocket streaming
- **Voice Interruption**: Stop mid-response
- **Continuous Listening**: No push-to-talk needed
- **Real-time Processing**: Sub-second response times

## Usage

### 1. Access Interfaces

- **Real-time Voice**: http://localhost:8000/static/index_realtime_voice.html
- **Standard Voice**: http://localhost:8000/static/index_private.html
- **Basic Interface**: http://localhost:8000/

### 2. Setup Real-time Voice

1. **Grant Permissions**: Allow microphone access
2. **Configure Context**: Select work/personal/creative/etc.
3. **Choose Mode**: Pick assistant behavior type
4. **Select Voice**: Choose TTS voice preference
5. **Connect**: Click "Connect Voice"

### 3. Voice Conversation Flow

1. **Connect**: Establish WebSocket connection
2. **Start Listening**: Click microphone button
3. **Speak**: EVA automatically detects speech
4. **Processing**: Real-time transcription and response
5. **Voice Response**: Automatic TTS playback
6. **Continue**: Seamless back-and-forth conversation

### 4. Private Mode Usage

```bash
# Enable private mode
Password: eva2415!
→ Personal context now requires authentication

# Use private voice
1. Select "Personal" context
2. Enter password when prompted
3. Secure 24-hour session created
4. All conversations encrypted and isolated
```

## API Reference

### WebSocket API

#### Connection
```
WS /ws/voice/{session_id}
```

#### Initialization Message
```json
{
  "user_id": "user123",
  "context": "personal",
  "mode": "coach",
  "auth_session_id": "optional_for_private"
}
```

#### Message Types

**Audio Chunk (Client → Server)**
```json
{
  "type": "audio_chunk",
  "audio": "base64_encoded_audio"
}
```

**Start/Stop Conversation**
```json
{
  "type": "start_conversation"
}
{
  "type": "stop_conversation"
}
```

**Interrupt**
```json
{
  "type": "interrupt"
}
```

**Server Events**
```json
{
  "type": "speech_transcribed",
  "data": { "text": "Hello EVA" }
}
{
  "type": "eva_response",
  "data": { "text": "Hi! How can I help?" }
}
{
  "type": "voice_response",
  "data": { "audio": "base64_mp3", "format": "mp3" }
}
```

### REST API

#### Session Management
```bash
GET /api/voice/sessions
GET /api/voice/sessions/{session_id}
POST /api/voice/sessions/{session_id}/interrupt
```

#### Password Management
```bash
POST /api/users/{user_id}/contexts/personal/password
DELETE /api/users/{user_id}/contexts/personal/password
GET /api/users/{user_id}/contexts/personal/password/status
```

## Configuration

### Environment Variables

```env
# Required for voice system
OPENAI_API_KEY=your_openai_key          # For GPT-4 and Whisper
ELEVENLABS_API_KEY=your_elevenlabs_key  # For TTS
ZEP_API_KEY=your_zep_key               # For memory

# Optional configuration
OPENAI_MODEL=gpt-4-turbo-preview       # Model selection
ZEP_ENABLED=true                       # Enable memory
```

### Audio Settings

- **Sample Rate**: 16kHz (WebRTC VAD requirement)
- **Channels**: Mono (1 channel)
- **Format**: WebM with Opus codec
- **Chunk Size**: 100ms for real-time streaming
- **VAD Aggressiveness**: 2 (moderate filtering)

## Technical Details

### Voice Activity Detection

Uses WebRTC VAD with rolling buffer analysis:
```python
# 30ms frames at 16kHz
frame_duration = 30
sample_rate = 16000
aggressiveness = 2  # 0-3 scale

# Rolling buffer for speech detection
buffer_size = 50 frames  # ~1.5 seconds
speech_threshold = 30%   # of recent frames
```

### Audio Processing Pipeline

1. **Capture**: Browser MediaRecorder API
2. **Encode**: WebM/Opus format
3. **Stream**: Base64 over WebSocket
4. **Decode**: Server-side audio processing
5. **VAD**: Speech detection and buffering
6. **STT**: Whisper transcription
7. **LLM**: Context-aware response generation
8. **TTS**: ElevenLabs synthesis
9. **Stream**: Base64 MP3 to client
10. **Playback**: Browser Audio API

### Memory Integration

Voice conversations integrate seamlessly with EVA's memory:
- **Session Creation**: Automatic Zep session initialization
- **Message Storage**: Real-time conversation logging
- **Context Retrieval**: Memory-enhanced responses
- **Temporal Tracking**: Time-aware knowledge graphs

### Security Implementation

- **Password Hashing**: PBKDF2 with 100k iterations
- **Session Tokens**: Cryptographically secure random
- **Context Isolation**: Separate user profiles per context
- **WebSocket Security**: WSS in production environments

## Performance Optimization

### Latency Reduction
- **WebSocket**: Direct streaming (no HTTP overhead)
- **Audio Chunks**: 100ms for real-time feel
- **VAD**: Instant speech detection
- **Parallel Processing**: STT/TTS pipeline optimization

### Scalability
- **Connection Pooling**: Efficient WebSocket management
- **Memory Management**: Automatic session cleanup
- **Resource Limits**: Configurable timeouts and buffers
- **Load Balancing**: Stateless session design

### Audio Quality
- **Echo Cancellation**: Browser-level processing
- **Noise Suppression**: WebRTC algorithms
- **Bitrate Optimization**: Adaptive audio encoding
- **Jitter Buffer**: Smooth playback handling

## Troubleshooting

### Common Issues

**Microphone Not Working**
- Check browser permissions
- Ensure HTTPS or localhost
- Verify audio device selection

**WebSocket Connection Failed**
- Check server status
- Verify network connectivity
- Review browser console for errors

**Audio Quality Issues**
- Check microphone quality
- Reduce background noise
- Adjust VAD sensitivity

**Memory Not Persisting**
- Verify Zep API key
- Check context selection
- Ensure session authentication

### Debug Information

Enable debug logging:
```python
import logging
logging.getLogger('realtime_voice').setLevel(logging.DEBUG)
logging.getLogger('eva_voice_workflow').setLevel(logging.DEBUG)
```

Monitor WebSocket traffic:
```javascript
// Browser console
websocket.addEventListener('message', e => console.log('RX:', e.data));
websocket.addEventListener('send', e => console.log('TX:', e.data));
```

## Future Enhancements

### Planned Features

1. **Multi-language Support**
   - Automatic language detection
   - Polyglot conversations
   - Language-specific TTS voices

2. **Advanced VAD**
   - Custom wake words
   - Speaker identification
   - Background conversation filtering

3. **Enhanced Audio**
   - WebRTC P2P connections
   - Adaptive bitrate streaming
   - Spatial audio support

4. **Intelligence Features**
   - Emotion detection in voice
   - Conversation summarization
   - Smart interruption handling

### Integration Opportunities

- **WebRTC**: Peer-to-peer audio for better quality
- **OpenAI Realtime API**: When available
- **Custom STT Models**: Domain-specific transcription
- **Voice Cloning**: Personalized TTS voices

## Comparison: EVA vs OpenAI Agents SDK

| Feature | EVA Hybrid | OpenAI SDK |
|---------|------------|------------|
| **Accessibility** | Web-based ✅ | Desktop only ❌ |
| **Multi-user** | Yes ✅ | No ❌ |
| **Real-time** | Yes ✅ | Yes ✅ |
| **Memory** | Persistent ✅ | Session only ❌ |
| **Context Separation** | Yes ✅ | Limited ❌ |
| **Privacy** | Password protected ✅ | No ❌ |
| **Voice Quality** | High ✅ | High ✅ |
| **Latency** | Low ✅ | Lower ✅ |
| **Interruption** | Yes ✅ | Yes ✅ |
| **Setup Complexity** | Moderate | Simple |

## Conclusion

The EVA Hybrid Voice System successfully combines:
- **OpenAI Agents SDK patterns** for real-time voice processing
- **Web accessibility** for broad platform support
- **Advanced memory systems** for persistent, context-aware conversations
- **Enterprise security** with password protection and context isolation

This creates a unique voice AI system that's both powerful and accessible, suitable for everything from casual conversations to secure business discussions.