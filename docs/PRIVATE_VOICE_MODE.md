# Private Voice Mode for EVA Agent

This document explains the enhanced private mode with voice capabilities for the EVA agent.

## Overview

The Private Voice Mode combines:
- **Password-protected personal context** for sensitive conversations
- **Voice input** via Web Speech API (STT)
- **Voice output** via ElevenLabs (TTS)
- **Secure session management** with 24-hour expiry

## Features

### 1. Password Protection

- **Password**: `eva2415!`
- **Purpose**: Enable/disable password protection for personal context
- **Scope**: Only applies to "Personal" context
- **Session Duration**: 24 hours

### 2. Voice Capabilities

#### Voice Input (Speech-to-Text)
- Hold the microphone button to record
- Release to convert speech to text
- Automatic message sending after conversion
- Uses OpenAI Whisper API

#### Voice Output (Text-to-Speech)
- Automatic TTS for all assistant responses
- Multiple voice options via ElevenLabs
- Voice preference saved locally

### 3. Private Mode Management

#### Enabling Private Mode
1. Click "🔐 Private Settings" button
2. Enter password: `eva2415!`
3. Click "Enable Private Mode"
4. Personal context now requires password

#### Disabling Private Mode
1. Click "🔐 Private Settings" button
2. Enter password: `eva2415!`
3. Click "Disable Private Mode"
4. Personal context accessible without password

## Usage

### Web Interface

Access the private voice interface at: `http://localhost:8000/static/index_private.html`

### First-Time Setup

1. **Grant Microphone Permission**: Browser will ask for microphone access
2. **Set Your Voice**: Choose from available TTS voices
3. **Configure Private Mode**: Use settings button to enable/disable

### Using Private Context

When private mode is ENABLED:
1. Select "Personal" context
2. Enter password when prompted (first message only)
3. Conversation proceeds with password protection
4. Session valid for 24 hours

When private mode is DISABLED:
1. Select "Personal" context
2. No password required
3. Normal conversation flow

### Voice Interaction

1. **Voice Input**: Hold microphone button → Speak → Release
2. **Voice Output**: Automatic TTS playback for responses
3. **Text Input**: Still available via text field

## API Endpoints

### Password Management

```bash
# Set password for personal context
POST /api/users/{user_id}/contexts/personal/password
{
  "password": "eva2415!"
}

# Remove password protection
DELETE /api/users/{user_id}/contexts/personal/password

# Verify password and get session
POST /api/users/{user_id}/contexts/personal/password/verify
{
  "password": "eva2415!"
}

# Check if password is required
GET /api/users/{user_id}/contexts/personal/password/status

# Enable/disable without removing password
PUT /api/users/{user_id}/contexts/personal/password/toggle
{
  "enabled": true
}
```

### Voice Endpoints

```bash
# Text-to-Speech
POST /api/tts
{
  "text": "Hello world",
  "voice_id": "voice_id_here"
}

# Speech-to-Text
POST /api/stt
FormData: audio file

# Get available voices
GET /api/voices

# Get TTS models
GET /api/tts/models
```

## Security Features

### Password Storage
- PBKDF2 with SHA256 hashing
- 100,000 iterations
- Random salt per password
- Stored in `.eva_private_auth.json` (600 permissions)

### Session Management
- Cryptographically secure session tokens
- 24-hour expiry
- Automatic cleanup of expired sessions
- Session bound to user ID and context

### Privacy
- Personal context completely isolated
- No cross-context data leakage
- Voice data not stored after processing
- All communications encrypted

## Configuration

### Environment Variables

```env
# Required for voice features
ELEVENLABS_API_KEY=your_elevenlabs_key
OPENAI_API_KEY=your_openai_key  # For Whisper STT

# Zep memory (required)
ZEP_API_KEY=your_zep_key
ZEP_ENABLED=true
```

### Voice Settings

- Voice selection persists in browser localStorage
- Microphone permissions required for voice input
- Audio autoplay must be enabled for TTS

## Troubleshooting

### Microphone Not Working
1. Check browser permissions
2. Ensure HTTPS or localhost
3. Try different browser

### TTS Not Playing
1. Check browser autoplay settings
2. Verify ElevenLabs API key
3. Check voice selection

### Password Issues
1. Password is exactly: `eva2415!`
2. Check `.eva_private_auth.json` exists
3. Verify file permissions (600)

### Session Expired
1. Re-enter password when prompted
2. Sessions last 24 hours
3. Check system time sync

## Best Practices

### Security
- Don't share the master password
- Regularly review `.eva_private_auth.json`
- Use private mode for sensitive topics only

### Voice Usage
- Speak clearly for better STT accuracy
- Choose appropriate TTS voice for context
- Use headphones to avoid echo

### Context Management
- Keep personal matters in Personal context
- Use private mode for sensitive conversations
- Remember context isolation is absolute

## Example Workflows

### Private Voice Journal
1. Enable private mode with `eva2415!`
2. Select Personal context + Friend mode
3. Use voice to record daily thoughts
4. EVA responds with empathetic voice

### Confidential Planning
1. Enable private mode
2. Select Personal context + Advisor mode
3. Discuss sensitive plans via voice
4. Password-protected memory retention

### Quick Voice Notes
1. Hold mic button
2. Speak your note
3. EVA transcribes and responds
4. Audio response plays automatically