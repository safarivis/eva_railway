# How to Run EVA Agent

This guide explains how to start and use the EVA agent with all its features including real-time voice, contextual memory, and private mode.

## 🚀 Quick Start Guide

### Prerequisites

- Python 3.9+
- Microphone access (for voice features)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Step 1: Install Dependencies

```bash
cd /home/ldp/louisdup/agents/eva_agent
pip install -r requirements.txt
```

### Step 2: Configure Environment

Ensure your `.env` file has the required API keys:

```env
# Required
OPENAI_API_KEY=your_openai_api_key          # For GPT-4 and Whisper STT
ELEVENLABS_API_KEY=your_elevenlabs_api_key  # For TTS voices
ZEP_API_KEY=your_zep_api_key               # For memory persistence

# Optional settings
OPENAI_MODEL=gpt-4-turbo-preview           # AI model to use
ZEP_ENABLED=true                           # Enable memory system
```

### Step 3: Start the Server

```bash
python core/eva.py
```

**Expected output:**
```
Zep memory layer initialized successfully
ElevenLabs TTS initialized successfully  
Whisper STT initialized successfully
Real-time voice system initialized successfully
Eva Agent initialized successfully with memory tools
INFO: Uvicorn running on http://0.0.0.0:8000
```

**⚠️ Important:** Keep this terminal window open - the server must stay running!

## 🌐 Access the Interfaces

### Simple Text Chat (Recommended)
**Command:** `python eva_chat.py`

**Features:**
- ✅ **WORKING** fast text chat with GPT-4.1
- ✅ Context switching (/context work|personal|creative|research)
- ✅ Mode switching (/mode friend|assistant|coach|tutor)
- ✅ Colorized terminal output
- ✅ Direct connection to Eva server

**Usage:**
```bash
# After starting eva server (python core/eva.py)
python eva_chat.py

# Commands:
You: hello
You: /context work
You: /mode assistant
You: exit
```

### Text Chat + TTS (Recommended for Voice Responses)
**Command:** `python eva_chat_tts.py`

**Features:**
- ✅ **WORKING** text chat with voice responses
- ✅ ElevenLabs TTS integration
- ✅ TTS controls (/tts on|off)
- ✅ All text chat features included
- ✅ Cross-platform audio support

**Usage:**
```bash
# After starting eva server (python core/eva.py)
python eva_chat_tts.py

# Commands:
You 🔊: hello eva          # Chat with TTS
You 🔊: /tts off           # Disable voice
You 🔇: /tts on            # Enable voice
You 🔇: /context work      # Change context
You 🔇: exit               # Quit
```

**Audio Requirements:**
- Linux: `sudo apt install mpg123`
- macOS: Built-in (afplay)
- Windows: Built-in (winsound)

### CLI Client Alternative
**Command:** `python utils/cli_client.py`

### Real-time Voice Mode
**URL:** `http://localhost:8000/static/index_realtime_voice.html`

**Features:**
- ✅ Continuous voice conversation
- ✅ Voice activity detection  
- ✅ Real-time streaming responses
- ✅ Context-aware memory
- ✅ Private mode with password protection
- ✅ Voice interruption support

### Standard Voice Mode
**URL:** `http://localhost:8000/static/index_private.html`

**Features:**
- ✅ Push-to-talk voice input
- ✅ Voice responses
- ✅ Context selection
- ✅ Password protection

### Basic Chat Interface
**URL:** `http://localhost:8000/`

**Features:**
- ✅ Text-only interface
- ✅ Streaming responses
- ✅ Basic functionality

## 🎤 Using Real-time Voice

### Initial Setup

1. **Open Real-time Interface**
   ```
   http://localhost:8000/static/index_realtime_voice.html
   ```

2. **Grant Microphone Permission**
   - Browser will prompt for microphone access
   - Click "Allow" to enable voice features

3. **Configure Settings**
   - **User ID**: Your unique identifier (auto-generated)
   - **Context**: Choose conversation type
     - `General` - Default conversations
     - `Work` - Professional discussions
     - `Personal` - Private matters (requires password)
     - `Creative` - Artistic projects
     - `Research` - Learning topics
   - **Mode**: Select EVA's personality
     - `Assistant` - Professional helper
     - `Coach` - Life coaching
     - `Tutor` - Educational guidance
     - `Advisor` - Business advice
     - `Friend` - Casual conversations
     - `Analyst` - Data analysis
     - `Creative` - Innovative thinking
   - **Voice**: Pick TTS voice preference

### Voice Conversation Flow

1. **Connect Voice Service**
   ```
   Click "Connect Voice" button
   ```

2. **Start Listening**
   ```
   Click the microphone button (🎤)
   Status changes to "Listening..."
   ```

3. **Speak Naturally**
   ```
   Just talk - EVA detects when you start/stop speaking
   No need to hold buttons or wait for prompts
   ```

4. **EVA Responds**
   ```
   Real-time transcription appears
   EVA processes and responds with voice
   Text response also displayed
   ```

5. **Continue Conversation**
   ```
   Keep talking naturally
   EVA remembers context across the conversation
   ```

6. **Interrupt if Needed**
   ```
   Click "Interrupt" to stop EVA mid-response
   Useful if you want to change direction
   ```

## 🔐 Private Mode Setup

### Enable Password Protection

1. **Click Private Settings**
   ```
   Click "🔐 Private Settings" button
   ```

2. **Enter Master Password**
   ```
   Password: eva2415!
   Click "Enable Private Mode"
   ```

3. **Confirmation**
   ```
   "Private mode enabled! Personal context now requires password."
   ```

### Using Private Context

1. **Select Personal Context**
   ```
   Change Context dropdown to "Personal (Private)"
   ```

2. **Authenticate**
   ```
   Enter password when prompted: eva2415!
   Secure 24-hour session created
   ```

3. **Secure Conversations**
   ```
   All conversations now encrypted and isolated
   Memory separated from other contexts
   ```

### Disable Private Mode

1. **Access Settings**
   ```
   Click "🔐 Private Settings"
   ```

2. **Disable Protection**
   ```
   Password: eva2415!
   Click "Disable Private Mode"
   ```

## 📱 Interface Controls

### Status Indicators

- **🟢 Connected** - Voice service ready
- **🔵 Listening** - EVA is listening for speech
- **🟠 Processing** - EVA is thinking/responding
- **🟣 Speaking** - EVA is delivering voice response
- **🔴 Error** - Something went wrong

### Voice Controls

- **🎤 Microphone Button** - Start/stop listening
- **Connect Voice** - Establish voice connection
- **Disconnect** - End voice session
- **Interrupt** - Stop EVA mid-response

### Real-time Features

- **Voice Activity Detection** - Automatic speech detection
- **Continuous Listening** - No push-to-talk needed
- **Interruption Support** - Stop and restart conversation
- **Context Memory** - Remembers previous conversations
- **Cross-Context Insights** - Work context can reference research

## 🐛 Troubleshooting

### Server Issues

**Server won't start:**
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt

# Check for missing API keys
cat .env
```

**Port already in use:**
```bash
# Kill existing processes
pkill -f "python eva.py"

# Or use different port
uvicorn eva:app --host 0.0.0.0 --port 8001
```

### Voice Issues

**Microphone not working:**
- ✅ Grant browser microphone permissions
- ✅ Use HTTPS or localhost (required for microphone)
- ✅ Check browser console for errors
- ✅ Try different browser

**No voice response:**
- ✅ Verify ElevenLabs API key
- ✅ Check internet connection
- ✅ Try different voice in dropdown
- ✅ Check browser audio settings

**Poor audio quality:**
- ✅ Reduce background noise
- ✅ Check microphone quality
- ✅ Move closer to microphone
- ✅ Use headphones to prevent echo

### Connection Issues

**WebSocket connection failed:**
```javascript
// Check browser console for errors
WebSocket connection to 'ws://localhost:8000/ws/voice/...' failed
```
- ✅ Ensure server is running
- ✅ Check firewall settings
- ✅ Try refreshing page
- ✅ Check network connectivity

**Memory not persisting:**
- ✅ Verify Zep API key is valid
- ✅ Check context selection
- ✅ Ensure user ID is consistent
- ✅ Check browser local storage

### Authentication Issues

**Private mode not working:**
- ✅ Password must be exactly: `eva2415!`
- ✅ Check for typos or extra spaces
- ✅ Clear browser cache/cookies
- ✅ Try incognito/private browsing

**Session expired:**
- ✅ Sessions last 24 hours
- ✅ Re-enter password if needed
- ✅ Check system time/timezone

## 🔧 Advanced Usage

### Using CLI Client

For text-only interaction:
```bash
# Basic usage
python cli_client.py

# With initial message
python cli_client.py --message "Hello EVA!"
```

### API Testing

Test endpoints directly:
```bash
# Check system status
curl http://localhost:8000/api/info

# Get available voices
curl http://localhost:8000/api/voices

# Check active voice sessions
curl http://localhost:8000/api/voice/sessions
```

### Debug Mode

Enable detailed logging:
```bash
# Set environment variable
export EVA_DEBUG=true

# Or add to .env file
echo "EVA_DEBUG=true" >> .env
```

## 🚦 Server Management

### Start Server
```bash
python eva.py
```

### Stop Server
```bash
# Press Ctrl+C in terminal
# Or kill process
pkill -f "python eva.py"
```

### Restart Server
```bash
# Use the restart script
./restart_eva.sh

# Or manually
pkill -f "python eva.py"
sleep 2
python eva.py
```

### Background Running
```bash
# Run in background (Linux/Mac)
nohup python eva.py > eva.log 2>&1 &

# Check if running
ps aux | grep eva.py
```

## 📊 Performance Tips

### Optimize Audio
- Use wired headphones to reduce latency
- Close other audio applications
- Check system audio settings
- Use high-quality microphone

### Improve Response Time
- Ensure stable internet connection
- Close unnecessary browser tabs
- Use Chrome/Edge for best WebSocket performance
- Check server resources (CPU/RAM)

### Memory Management
- Restart server periodically for long sessions
- Clear browser cache if experiencing issues
- Monitor Zep memory usage
- Use specific contexts to organize conversations

## 🔄 Updates and Maintenance

### Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### Clear Memory
```bash
# Reset Zep sessions (if needed)
rm .eva_private_auth.json

# Clear browser storage
# Go to browser dev tools > Application > Storage > Clear
```

### Backup Configuration
```bash
# Backup important files
cp .env .env.backup
cp .eva_private_auth.json .eva_private_auth.json.backup
```

## ✅ Success Checklist

Before using EVA, verify:

- [ ] Server starts without errors
- [ ] All API keys configured
- [ ] Microphone permission granted
- [ ] Web interface loads properly
- [ ] Voice connection establishes
- [ ] Speech detection works
- [ ] Voice responses play
- [ ] Memory persists across sessions
- [ ] Private mode functions correctly

## 📞 Getting Help

If you encounter issues:

1. **Check this guide** for common solutions
2. **Review server logs** in terminal
3. **Check browser console** for errors
4. **Verify API keys** are correct and valid
5. **Test with different browsers**
6. **Restart server** and try again

EVA is now ready for intelligent voice conversations with memory, context awareness, and private mode protection!