# Working Scripts Guide

## Voice Interface Scripts (in voice/ directory)

### 🎯 **USE THESE:**

1. **`claude_voice_simple.py`** - Main voice interface
   - ✅ Works with Python 3.13 (no aifc issues)
   - ✅ Fallback audio handling
   - ✅ Same features as above
   ```bash
   python voice/claude_voice_simple.py
   ```

3. **`eva_voice_speechrecognition.py`** - Alternative voice agent
   - ✅ Standalone voice assistant
   - ✅ Wake word activation ("eva")
   - ✅ Built-in commands
   ```bash
   python voice/eva_voice_speechrecognition.py
   ```

### 📁 **SUPPORTING FILES (don't run directly):**
- `eva_voice_workflow.py` - Voice workflow manager
- `realtime_voice.py` - Real-time voice handling
- `simple_voice_recognition.py` - Basic recognition example

## Core EVA Server

**`core/eva.py`** - Main EVA server
- ✅ Web interface at http://localhost:8000
- ✅ REST API endpoints
- ✅ Zep memory integration
- ✅ Session persistence
```bash
python core/eva.py
```

## Text Chat

1. **Web Interface**: http://localhost:8000 (when EVA is running)
2. **API**: Use `/api/chat-simple` endpoint
3. **Voice scripts**: Can type instead of speaking

## Quick Start

```bash
# Terminal 1 - Start EVA server
source venv/bin/activate
python core/eva.py

# Terminal 2 - Use voice interface
source venv/bin/activate
python voice/claude_voice_direct_fixed.py
```