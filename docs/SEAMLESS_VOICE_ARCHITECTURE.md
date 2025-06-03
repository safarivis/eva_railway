# Seamless Voice Architecture for Eva

## Current Problems
- Press-to-talk is clunky and unnatural
- Wake word detection is unreliable
- Latency between speech and response
- Not production-ready for hosting

## Proposed Solutions

### 1. **LiveKit Integration (Recommended for Production)**
```python
# Real-time WebRTC with LiveKit
- Ultra-low latency (< 100ms)
- Always-on microphone with smart VAD
- Handles thousands of concurrent users
- Built-in echo cancellation
- Works globally with edge servers
```

**Benefits:**
- Production-ready infrastructure
- Scales automatically
- Handles network issues gracefully
- Professional WebRTC implementation

### 2. **OpenAI Realtime API (Cutting Edge)**
```python
# Direct voice-to-voice with OpenAI
- Native voice understanding
- No STT/TTS round trip
- Natural conversation flow
- Emotion and tone preservation
```

### 3. **Enhanced WebSocket Implementation**
Building on existing `realtime_voice.py`:

```python
# Improvements needed:
1. Replace wake word with smart VAD
2. Implement audio streaming pipeline
3. Add speculative execution
4. Use faster-whisper with GPU
5. Stream TTS responses
```

## Quick Implementation Plan

### Phase 1: Immediate Improvements (1-2 days)
```bash
# 1. Install RealtimeSTT for seamless voice
pip install RealtimeSTT

# 2. Create new seamless voice endpoint
python eva_voice_seamless.py
```

### Phase 2: LiveKit Integration (3-5 days)
```python
# 1. Set up LiveKit server
docker run -d \
  -p 7880:7880 \
  -p 7881:7881 \
  -p 7882:7882/udp \
  livekit/livekit-server \
  --dev

# 2. Integrate with Eva
pip install livekit-server-sdk
```

### Phase 3: Production Deployment (1 week)
- Deploy LiveKit to cloud
- Set up global edge servers
- Implement fallback mechanisms
- Add monitoring and analytics

## Seamless Voice Flow

```
User speaks → 
  LiveKit captures audio → 
    Smart VAD detects speech → 
      Stream to Whisper → 
        Eva processes → 
          Stream TTS response → 
            Interrupt if user speaks
```

## Code Example: Seamless Voice with RealtimeSTT

```python
from RealtimeSTT import AudioToTextRecorder

class SeamlessEvaVoice:
    def __init__(self):
        self.recorder = AudioToTextRecorder(
            spinner=False,
            model="tiny",  # Use base or small for better accuracy
            language="en",
            silero_sensitivity=0.4,
            webrtc_sensitivity=3,
            post_speech_silence_duration=0.4,
            min_length_of_recording=0.5,
            min_gap_between_recordings=0.1,
            enable_realtime_transcription=True,
            realtime_processing_pause=0.1,
            on_realtime_transcription_update=self.process_partial,
        )
        
    def process_partial(self, text):
        """Process partial transcription for faster response"""
        # Start processing Eva's response speculatively
        if len(text.split()) > 3:
            asyncio.create_task(self.prepare_response(text))
    
    def run(self):
        print("Eva is listening... Just speak naturally!")
        while True:
            text = self.recorder.text()
            if text:
                response = self.get_eva_response(text)
                self.speak_response(response)
```

## Hosting Considerations

### For Development:
- Use RealtimeSTT for quick seamless experience
- WebSocket implementation for custom control

### For Production:
- **LiveKit** - Best for scalability and reliability
- **Agora** - Alternative with good global coverage
- **Daily.co** - Simple WebRTC with good DX
- **Twilio** - Enterprise-grade but expensive

### Architecture for 1000+ users:
```
                    ┌─────────────┐
                    │   Clients   │
                    └──────┬──────┘
                           │ WebRTC
                    ┌──────┴──────┐
                    │  LiveKit    │
                    │  Media Server│
                    └──────┬──────┘
                           │ Audio Stream
                    ┌──────┴──────┐
                    │ Eva Backend │
                    │  (FastAPI)  │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │  Whisper +  │
                    │  TTS Pool   │
                    └─────────────┘
```

## Next Steps

1. **Try RealtimeSTT** for immediate improvement
2. **Set up LiveKit** dev environment  
3. **Benchmark latency** with different approaches
4. **Choose solution** based on your scale needs

The key is to move from "push-to-talk" to "just talk" - making Eva feel like a natural conversation partner, not a voice assistant.