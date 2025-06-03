# EVA Agent Deployment Plan

## 🎯 **Current Status**
- ✅ EVA server working locally (`python core/eva.py`)
- ✅ Web interface at http://localhost:8000
- ✅ Voice chat working with ElevenLabs (`python voice/eva_elevenlabs_voice.py`)
- ✅ Secure voice recordings in `voice_recordings/`
- ✅ Session persistence and Zep memory integration
- ✅ Project organized and cleaned up

## 🚀 **Railway Deployment Plan (Next Session)**

### **Step 1: Prepare Repository**
```bash
# Already created:
- railway.json (deployment config)
- nixpacks.toml (build config) 
- .railwayignore (ignore files)
- Updated eva.py for PORT environment variable
```

### **Step 2: Deploy to Railway**
1. **Sign up**: https://railway.app (GitHub login)
2. **Deploy**: "Deploy from GitHub repo"
3. **Connect**: Upload eva_agent project
4. **Environment Variables**:
   ```
   OPENAI_API_KEY=your_openai_key
   ELEVENLABS_API_KEY=your_elevenlabs_key
   ZEP_API_KEY=your_zep_key
   OPENAI_MODEL=gpt-4.1
   ```

### **Step 3: Test Deployment**
- Access Railway URL (https://your-app.up.railway.app)
- Test web interface
- Test voice functionality
- Verify session persistence

## 💰 **Cost Structure**
- **Free Trial**: $5 credit to test
- **Hobby Plan**: $5/month for always-on deployment
- **Features**: 512MB RAM, 1GB storage, custom domain

## 🔧 **Working Scripts Summary**
```
voice/
├── eva_elevenlabs_voice.py     # ✅ Main voice interface (ElevenLabs STT/TTS)
├── eva_voice_working.py        # ⚠️  Has aifc issues
└── eva_voice_chat.py           # ✅ Text/voice hybrid

core/
└── eva.py                      # ✅ Main server (web + API)

Web Interface:
└── http://localhost:8000       # ✅ Working web chat
```

## 🎤 **Voice Setup Issues Resolved**
- ❌ SpeechRecognition + Python 3.13 = aifc module errors
- ✅ ElevenLabs STT/TTS = works perfectly
- ✅ pydub installed for audio format conversion

## 📋 **Next Session TODO**
1. [ ] Test Railway deployment
2. [ ] Set up environment variables
3. [ ] Test web interface on deployed URL
4. [ ] Test ElevenLabs voice functionality
5. [ ] Configure custom domain (optional)
6. [ ] Set up monitoring/logs

## 🎯 **Goals Achieved**
- Full working EVA agent with voice capabilities
- Clean, organized codebase
- Secure voice recording storage
- Session persistence with Zep memory
- Web interface working locally
- Ready for cloud deployment

## 🔗 **Important URLs**
- Local EVA: http://localhost:8000
- Railway: https://railway.app
- Project docs: `WORKING_SCRIPTS.md`

---
**Status**: Ready for Railway deployment in next session! 🚀