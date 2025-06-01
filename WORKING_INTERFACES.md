# ✅ Working Eva Interfaces

This document lists the **confirmed working** interfaces for Eva Agent.

## 🎯 Primary Working Interfaces

### 1. **Text Chat** (Fastest) ⚡
```bash
python eva_chat.py
```
- ✅ Pure text chat with GPT-4.1
- ✅ Instant responses
- ✅ Context & mode switching
- ✅ Colorized output
- ✅ Memory persistence with Zep

### 2. **Text Chat + TTS** (Voice Responses) 🔊
```bash
python eva_chat_tts.py
```
- ✅ Text chat with voice responses
- ✅ ElevenLabs TTS integration
- ✅ Toggle TTS on/off with `/tts on|off`
- ✅ Cross-platform audio support
- ✅ All text chat features

## 🚀 Quick Start

**Terminal 1 - Start Server:**
```bash
cd ~/louisdup/agents/eva_agent
source venv/bin/activate
python core/eva.py
```

**Terminal 2 - Choose Interface:**
```bash
# Text only (fastest)
python eva_chat.py

# Text + voice responses 
python eva_chat_tts.py
```

## 📋 Commands Reference

### Universal Commands (Both Interfaces)
```
/context work|personal|creative|research|general
/mode friend|assistant|coach|tutor|advisor|analyst|creative
exit|quit|bye
```

### TTS-Specific Commands (eva_chat_tts.py only)
```
/tts on   - Enable voice responses
/tts off  - Disable voice responses
```

## 🎵 Audio Setup (For TTS)

**Linux:**
```bash
sudo apt install mpg123
# or
sudo apt install ffmpeg
```

**macOS:** Built-in (afplay)  
**Windows:** Built-in (winsound)

## 🔧 Configuration

### Environment Variables
```env
OPENAI_MODEL=gpt-4.1
OPENAI_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here  # For TTS
ZEP_API_KEY=your_key_here         # For memory
ZEP_ENABLED=true
```

### Model Configuration
- Currently using: **GPT-4.1** (OpenAI's latest)
- TTS: **ElevenLabs Turbo V2.5**
- Memory: **Zep Cloud**

## 🎭 Personality Modes

- **friend** - Casual, conversational
- **assistant** - Professional, helpful
- **coach** - Motivational, supportive  
- **tutor** - Educational, explanatory
- **advisor** - Strategic, analytical
- **analyst** - Data-focused, logical
- **creative** - Innovative, artistic

## 🗂️ Context Types

- **general** - Default conversations
- **work** - Professional discussions
- **personal** - Private matters
- **creative** - Artistic projects
- **research** - Learning topics

## ✅ Confirmed Working Features

- [x] GPT-4.1 model integration
- [x] Text chat interface  
- [x] TTS voice responses
- [x] Context switching
- [x] Mode switching
- [x] Memory persistence
- [x] Colorized terminal output
- [x] Cross-platform audio
- [x] Toggle TTS on/off
- [x] Error handling
- [x] Graceful shutdown

## 🚫 Not Working / Untested

- [ ] CLI client (utils/cli_client.py) - connection issues
- [ ] Web interface - needs testing
- [ ] Voice input (STT) - available in web interface
- [ ] Streaming responses in terminal

## 📊 Performance

**Text Chat (eva_chat.py):**
- Response time: ~1-3 seconds
- Memory usage: Low
- CPU usage: Low

**Text + TTS (eva_chat_tts.py):**
- Response time: ~3-6 seconds (includes TTS)
- Memory usage: Medium  
- CPU usage: Medium

## 🔄 Status

Last updated: June 1, 2025  
Eva Agent Status: **WORKING** ✅  
Primary interfaces: **STABLE** ✅  
TTS integration: **WORKING** ✅  
Memory system: **WORKING** ✅