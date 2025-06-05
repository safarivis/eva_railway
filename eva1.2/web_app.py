#!/usr/bin/env python3
"""
Eva 1.2 Local Web Application
Test the specialized assistant ecosystem in your browser
"""
from flask import Flask, render_template, request, jsonify, session
import os
import sys
import asyncio
import uuid
from datetime import datetime
import json

# Add eva1.2 to path
eva12_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, eva12_path)

# Import Eva 1.2 components
try:
    from core.assistant_manager import get_assistant_manager
    from core.eva_orchestrator import get_eva_orchestrator
    from config.eva1_config import Eva12Config
    EVA12_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Eva 1.2 modules not available: {e}")
    print("Running in demo mode")
    EVA12_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'eva12-test-secret-key')

# Initialize Eva 1.2 components
config = None
orchestrator = None
assistant_manager = None

def init_eva12():
    """Initialize Eva 1.2 components"""
    global orchestrator, assistant_manager, config
    if not EVA12_AVAILABLE:
        return False
        
    try:
        # Set test mode if no API key
        if not os.environ.get('OPENAI_API_KEY'):
            os.environ['OPENAI_API_KEY'] = 'test_key_for_demo'
            os.environ['EVA12_TEST_MODE'] = 'true'
        
        config = Eva12Config.from_env()
        assistant_manager = get_assistant_manager()
        orchestrator = get_eva_orchestrator()
        print("✅ Eva 1.2 initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Eva 1.2: {e}")
        return False

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get or create user session
        if 'user_id' not in session:
            session['user_id'] = str(uuid.uuid4())
        user_id = session['user_id']
        
        # Process through Eva 1.2 orchestrator
        if orchestrator:
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                response = loop.run_until_complete(
                    orchestrator.process_user_request(message, user_id)
                )
                
                return jsonify({
                    'response': response.response_text,
                    'assistant': response.assistant_used,
                    'thread_id': response.thread_id,
                    'confidence': response.confidence,
                    'timestamp': datetime.now().isoformat()
                })
            finally:
                loop.close()
        else:
            # Fallback demo mode
            return jsonify({
                'response': f"[Demo Mode] I would process: '{message}' through Eva 1.2 assistants",
                'assistant': 'demo',
                'thread_id': 'demo-thread',
                'confidence': 0.0,
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/assistants')
def get_assistants():
    """Get list of available assistants"""
    if assistant_manager:
        assistants = []
        for name, config in assistant_manager.assistant_configs.items():
            assistants.append({
                'name': name,
                'description': config.description,
                'model': config.model,
                'temperature': config.temperature,
                'tools': len(config.tools)
            })
        return jsonify({'assistants': assistants})
    else:
        # Demo data
        return jsonify({
            'assistants': [
                {'name': 'email_specialist', 'description': 'Email and communication expert', 'model': 'gpt-4o', 'temperature': 0.3, 'tools': 4},
                {'name': 'coding_specialist', 'description': 'Software development assistant', 'model': 'gpt-4o', 'temperature': 0.1, 'tools': 5},
                {'name': 'music_curator', 'description': 'Music discovery and playlists', 'model': 'gpt-4o-mini', 'temperature': 0.8, 'tools': 4},
                {'name': 'research_analyst', 'description': 'Research and analysis', 'model': 'gpt-4o', 'temperature': 0.2, 'tools': 4},
                {'name': 'personal_assistant', 'description': 'Productivity and scheduling', 'model': 'gpt-4o-mini', 'temperature': 0.4, 'tools': 4},
                {'name': 'creative_director', 'description': 'Creative content and design', 'model': 'gpt-4o', 'temperature': 0.9, 'tools': 4}
            ]
        })

@app.route('/api/status')
def get_status():
    """Get system status"""
    if orchestrator:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            status = loop.run_until_complete(orchestrator.get_system_status())
            return jsonify(status)
        finally:
            loop.close()
    else:
        return jsonify({
            'status': 'demo',
            'assistants': {'total': 6, 'active': 0},
            'threads': {'total': 0, 'active': 0},
            'orchestration': {'total_requests': 0, 'success_rate': 0.0}
        })

@app.route('/api/classify', methods=['POST'])
def classify_task():
    """Classify a task to see which assistant would handle it"""
    try:
        data = request.get_json()
        task = data.get('task', '')
        
        if not task:
            return jsonify({'error': 'No task provided'}), 400
        
        if assistant_manager:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                route = loop.run_until_complete(assistant_manager.classify_task(task))
                return jsonify({
                    'task': task,
                    'assistant': route.assistant_name,
                    'confidence': route.confidence,
                    'reasoning': route.reasoning,
                    'fallback_assistants': route.fallback_assistants
                })
            finally:
                loop.close()
        else:
            # Demo classification
            return jsonify({
                'task': task,
                'assistant': 'demo_assistant',
                'confidence': 0.85,
                'reasoning': 'Demo mode classification',
                'fallback_assistants': []
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n🚀 Starting Eva 1.2 Local Web Interface")
    print("=" * 50)
    
    # Initialize Eva 1.2
    if init_eva12():
        print("✅ Eva 1.2 ready!")
    else:
        print("⚠️  Running in demo mode (no OpenAI API key)")
    
    print("\n📱 Access the web interface at:")
    print("   http://localhost:5000\n")
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)