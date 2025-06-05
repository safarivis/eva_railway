# 🌐 Eva 1.2 Local Testing Guide

Test the Eva 1.2 specialized assistant ecosystem in your local browser!

## 🚀 Quick Start

### Option 1: Demo Mode (No API Key Required)
```bash
cd eva1.2
./start_demo.sh
```

### Option 2: Full Eva 1.2 (Requires OpenAI API Key)
```bash
cd eva1.2
export OPENAI_API_KEY="your-api-key-here"
./start_web.sh
```

## 🌐 Access the Interface

Open your browser and go to:
**http://localhost:5000**

## 🧪 Test Scenarios

### 📧 Email Specialist
- "Send an email to the team about tomorrow's meeting"
- "Compose a professional message to our client"
- "Schedule a follow-up email for next week"

### 💻 Coding Specialist  
- "Debug this Python function that's throwing errors"
- "Review my code for optimization opportunities"
- "Help me write unit tests for this module"

### 🎵 Music Curator
- "Create a high-energy workout playlist"
- "Find some chill jazz music for studying" 
- "Play my favorite indie rock songs"

### 🔍 Research Analyst
- "Research competitor pricing strategies"
- "Analyze market trends in AI technology"
- "Find information about sustainable energy solutions"

### 📅 Personal Assistant
- "Schedule a meeting with the design team"
- "Remind me to call mom tomorrow"
- "Add grocery shopping to my task list"

### 🎨 Creative Director
- "Design a logo for our new product"
- "Create content for our social media campaign"
- "Brainstorm ideas for the company rebrand"

## 🎯 What You'll See

- **Task Classification**: Watch as Eva 1.2 intelligently routes your requests to the right specialist
- **Confidence Scoring**: See how confident the system is about each routing decision
- **Assistant Profiles**: View all 6 specialized assistants and their capabilities
- **Real-time Chat**: Experience the seamless conversation flow
- **Beautiful UI**: Enjoy the modern, dark-themed interface

## 🔧 Technical Features Demonstrated

- ✅ **Intelligent Task Routing** - Automatic classification to the best specialist
- ✅ **6 Specialized Assistants** - Each with domain-specific expertise
- ✅ **Confidence Scoring** - Transparency in decision-making
- ✅ **Fallback Mechanisms** - Graceful handling of ambiguous requests
- ✅ **Modern Web Interface** - Responsive, real-time chat experience
- ✅ **Session Management** - Persistent conversations across interactions

## 🚦 Status Indicators

- **Green Dot**: Eva 1.2 system is active and ready
- **Assistant Badges**: Shows which specialist is handling each response
- **Confidence Percentage**: Displays system confidence in routing decisions
- **Request Counter**: Tracks total interactions

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Kill any existing Flask processes
pkill -f "python.*demo_web.py"
# Or use a different port
python demo_web.py --port 5001
```

### Missing Dependencies
```bash
pip install flask python-dotenv
```

### Permission Issues
```bash
chmod +x start_demo.sh
```

## 📊 Demo vs Production

| Feature | Demo Mode | Production Mode |
|---------|-----------|-----------------|
| API Key Required | ❌ | ✅ |
| Task Classification | ✅ (Local) | ✅ (OpenAI) |
| Response Generation | ✅ (Simulated) | ✅ (Real) |
| Assistant Routing | ✅ | ✅ |
| Web Interface | ✅ | ✅ |
| Cost Tracking | ❌ | ✅ |
| Thread Persistence | ❌ | ✅ |

## 🎉 Next Steps

After testing locally:

1. **Deploy to Production**: Use the deployment guide in `docs/DEPLOYMENT_GUIDE.md`
2. **Configure Environment**: Set up all environment variables from `.env.eva12`
3. **Run Full Tests**: Execute `python run_all_tests.py` for comprehensive validation
4. **Monitor Performance**: Use the built-in analytics and cost tracking
5. **Explore Phase 4**: Plan for batch processing and advanced features

---

**Enjoy exploring Eva 1.2! 🚀**