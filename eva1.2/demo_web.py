#!/usr/bin/env python3
"""
Eva 1.2 Demo Web Application
A lightweight demo of the Eva 1.2 assistant ecosystem interface
"""
from flask import Flask, render_template, request, jsonify, session
import os
import uuid
from datetime import datetime
import json
import random

app = Flask(__name__)
app.secret_key = 'eva12-demo-secret-key'

# Demo assistant configurations
DEMO_ASSISTANTS = [
    {
        'name': 'email_specialist',
        'display_name': 'Email Specialist',
        'description': 'Professional communication and email management',
        'model': 'gpt-4o',
        'temperature': 0.3,
        'tools': 4,
        'emoji': '📧',
        'keywords': ['email', 'send', 'message', 'mail', 'compose', 'reply', 'calendar']
    },
    {
        'name': 'coding_specialist', 
        'display_name': 'Coding Specialist',
        'description': 'Software development, debugging, and code analysis',
        'model': 'gpt-4o',
        'temperature': 0.1,
        'tools': 5,
        'emoji': '💻',
        'keywords': ['code', 'debug', 'python', 'function', 'bug', 'programming', 'develop']
    },
    {
        'name': 'music_curator',
        'display_name': 'Music Curator', 
        'description': 'Spotify integration and music discovery',
        'model': 'gpt-4o-mini',
        'temperature': 0.8,
        'tools': 4,
        'emoji': '🎵',
        'keywords': ['music', 'playlist', 'spotify', 'song', 'artist', 'play', 'listen']
    },
    {
        'name': 'research_analyst',
        'display_name': 'Research Analyst',
        'description': 'Information gathering and analysis', 
        'model': 'gpt-4o',
        'temperature': 0.2,
        'tools': 4,
        'emoji': '🔍',
        'keywords': ['research', 'analyze', 'find', 'search', 'information', 'study', 'investigate']
    },
    {
        'name': 'personal_assistant',
        'display_name': 'Personal Assistant',
        'description': 'Productivity and personal task management',
        'model': 'gpt-4o-mini', 
        'temperature': 0.4,
        'tools': 4,
        'emoji': '📅',
        'keywords': ['schedule', 'reminder', 'task', 'appointment', 'calendar', 'productivity']
    },
    {
        'name': 'creative_director',
        'display_name': 'Creative Director',
        'description': 'Content creation and creative projects',
        'model': 'gpt-4o',
        'temperature': 0.9,
        'tools': 4, 
        'emoji': '🎨',
        'keywords': ['create', 'design', 'content', 'image', 'creative', 'art', 'visual']
    }
]

def classify_task_demo(task):
    """Demo task classification"""
    task_lower = task.lower()
    
    # Find best matching assistant
    best_match = None
    best_score = 0
    
    for assistant in DEMO_ASSISTANTS:
        score = 0
        for keyword in assistant['keywords']:
            if keyword in task_lower:
                score += 1
        
        if score > best_score:
            best_score = score
            best_match = assistant
    
    # If no match, use research_analyst as fallback
    if not best_match or best_score == 0:
        best_match = next(a for a in DEMO_ASSISTANTS if a['name'] == 'research_analyst')
        confidence = 0.6
    else:
        confidence = min(0.95, 0.7 + (best_score * 0.1))
    
    return {
        'assistant': best_match,
        'confidence': confidence,
        'reasoning': f"Matched {best_score} keywords for {best_match['display_name']}"
    }

def generate_demo_response(message, assistant, confidence):
    """Generate a demo response"""
    responses = {
        'email_specialist': [
            f"I would help you compose and send that email professionally. As your Email Specialist, I'd ensure proper formatting, tone, and scheduling.",
            f"I'd draft that email for you with appropriate professional language and help you schedule any necessary follow-ups.",
            f"Let me help you with that email communication. I'll make sure it's clear, professional, and gets the results you need."
        ],
        'coding_specialist': [
            f"I'd analyze your code thoroughly, identify any bugs or optimization opportunities, and provide specific fixes with explanations.",
            f"As your Coding Specialist, I'd review that code for errors, suggest improvements, and help you implement best practices.",
            f"I would debug that code systematically, explain what's causing any issues, and provide clean, optimized solutions."
        ],
        'music_curator': [
            f"I'd search Spotify for the perfect tracks matching your mood and create a personalized playlist just for you!",
            f"Let me curate some amazing music for you! I'll find songs that match your taste and create the perfect playlist.",
            f"I'd discover new music tailored to your preferences and organize it into a playlist you'll love."
        ],
        'research_analyst': [
            f"I'd conduct thorough research on that topic, gather reliable sources, and provide you with a comprehensive analysis.",
            f"Let me investigate that for you. I'll find the most relevant and up-to-date information and present it clearly.",
            f"I would research that topic extensively and provide you with detailed insights and actionable findings."
        ],
        'personal_assistant': [
            f"I'd help you organize that task, set appropriate reminders, and integrate it seamlessly into your schedule.",
            f"Let me manage that for you! I'll schedule it appropriately and make sure you stay on top of all your commitments.",
            f"I would coordinate that appointment, handle the scheduling details, and ensure everything runs smoothly."
        ],
        'creative_director': [
            f"I'd brainstorm creative concepts for that project and help you develop compelling visual and content ideas.",
            f"Let me unleash some creativity! I'd design innovative approaches and help bring your creative vision to life.",
            f"I would develop creative strategies for that project and provide you with fresh, engaging concepts."
        ]
    }
    
    assistant_responses = responses.get(assistant['name'], [
        f"I would handle that request using my specialized knowledge and tools.",
        f"Let me assist you with that using my domain expertise.",
        f"I'd provide specialized help for that task."
    ])
    
    response = random.choice(assistant_responses)
    
    # Add confidence-based preamble
    if confidence > 0.8:
        response = f"[Demo Mode] {response}"
    else:
        response = f"[Demo Mode - Lower Confidence] {response}"
    
    return response

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
        
        # Classify task and generate response
        classification = classify_task_demo(message)
        assistant = classification['assistant']
        confidence = classification['confidence']
        
        response_text = generate_demo_response(message, assistant, confidence)
        
        return jsonify({
            'response': response_text,
            'assistant': assistant['name'],
            'confidence': confidence,
            'thread_id': f"demo-thread-{session['user_id']}",
            'timestamp': datetime.now().isoformat()
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/assistants')
def get_assistants():
    """Get list of available assistants"""
    return jsonify({'assistants': DEMO_ASSISTANTS})

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({
        'status': 'demo',
        'assistants': {'total': len(DEMO_ASSISTANTS), 'active': len(DEMO_ASSISTANTS)},
        'threads': {'total': 1, 'active': 1},
        'orchestration': {'total_requests': 0, 'success_rate': 1.0}
    })

@app.route('/api/classify', methods=['POST'])
def classify_task():
    """Classify a task to see which assistant would handle it"""
    try:
        data = request.get_json()
        task = data.get('task', '')
        
        if not task:
            return jsonify({'error': 'No task provided'}), 400
        
        classification = classify_task_demo(task)
        assistant = classification['assistant']
        
        return jsonify({
            'task': task,
            'assistant': assistant['name'],
            'confidence': classification['confidence'],
            'reasoning': classification['reasoning'],
            'fallback_assistants': ['research_analyst']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n🚀 Starting Eva 1.2 Demo Web Interface")
    print("=" * 50)
    print("✅ Demo mode active - no OpenAI API key required")
    print("🤖 All 6 specialized assistants available for testing")
    print("📊 Task classification system operational")
    print("\n📱 Access the web interface at:")
    print("   http://localhost:5000\n")
    print("💡 Try these example messages:")
    print("   • 'Send an email to the team about our meeting'")
    print("   • 'Debug this Python function that's throwing errors'") 
    print("   • 'Create a high-energy workout playlist'")
    print("   • 'Research competitor pricing strategies'")
    print("   • 'Schedule a meeting with the design team'")
    print("   • 'Design a logo for our new product'")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)