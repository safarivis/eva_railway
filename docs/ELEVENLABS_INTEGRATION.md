# ElevenLabs Integration for Eva Agent

This document describes the ElevenLabs Text-to-Speech (TTS) and Speech-to-Text (STT) integration for Eva Agent.

## Features

### Text-to-Speech (TTS)
- Convert agent responses to natural-sounding speech using ElevenLabs API
- Support for multiple voices and models
- Streaming audio generation for low-latency responses
- Base64 audio encoding for easy client integration

### Speech-to-Text (STT)
- Convert user audio input to text using OpenAI Whisper API
- Support for multiple languages
- WebM audio format support

## Configuration

Add these environment variables to your `.env` file:

```env
# ElevenLabs API Key (required for TTS)
ELEVENLABS_API_KEY=sk_bd89a58ef5ee69fc40314fdf531568682f291f9376dfac45

# OpenAI API Key (required for STT using Whisper)
OPENAI_API_KEY=your_openai_api_key_here
```

## API Endpoints

### 1. Text-to-Speech
```
POST /api/tts
```

Request body:
```json
{
  "text": "Hello, world!",
  "voice_id": "optional_voice_id",
  "stream": false
}
```

Returns: Audio file (MP3 format)

### 2. Speech-to-Text
```
POST /api/stt
```

Request: Multipart form data with audio file

Returns:
```json
{
  "text": "Transcribed text",
  "filename": "audio.webm"
}
```

### 3. Get Available Voices
```
GET /api/voices
```

Returns list of available ElevenLabs voices.

### 4. Get TTS Models
```
GET /api/tts/models
```

Returns list of available ElevenLabs models.

## Using Voice in Agent Conversations

When creating a new agent run, enable voice by setting `voice_enabled` to `true`:

```json
POST /agents/eva/runs
{
  "messages": [
    {
      "role": "user",
      "content": "Hello Eva!"
    }
  ],
  "stream": true,
  "voice_enabled": true,
  "voice_id": "optional_voice_id"
}
```

When voice is enabled, the agent will send an additional `agent.audio` event with base64-encoded audio:

```json
{
  "event_type": "agent.audio",
  "data": {
    "audio": "base64_encoded_audio_data",
    "format": "mp3"
  }
}
```

## Testing

Run the test script to verify the integration:

```bash
python test_elevenlabs.py
```

This will test:
1. TTS functionality
2. Agent with voice responses
3. STT functionality (if test audio file is present)

## Implementation Details

The integration consists of:

1. **elevenlabs_integration.py**: Core integration module
   - `ElevenLabsIntegration`: Handles TTS operations
   - `WhisperSTT`: Handles STT operations using OpenAI Whisper

2. **eva.py modifications**:
   - Added voice support to run requests
   - Audio generation after text responses
   - New API endpoints for TTS/STT operations

3. **Dependencies**:
   - `httpx`: For API requests
   - `openai`: For Whisper STT
   - `python-multipart`: For file uploads

## Notes

- ElevenLabs primarily focuses on TTS; STT is handled by OpenAI Whisper
- The default voice is "Rachel" (ID: 21m00Tcm4TlvDq8ikWAM)
- Audio is returned as MP3 format for broad compatibility
- Consider rate limits when using these services in production