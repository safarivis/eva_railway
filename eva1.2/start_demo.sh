#!/bin/bash
# Start Eva 1.2 Demo Web Interface

echo "🚀 Starting Eva 1.2 Demo Web Interface"
echo "====================================="
echo ""
echo "✨ This demo showcases the Eva 1.2 specialized assistant ecosystem"
echo "🤖 Test task classification and assistant routing without API keys"
echo ""

# Check if Flask is available
python -c "import flask" 2>/dev/null || {
    echo "Installing Flask..."
    pip install flask
}

echo "🌐 Starting web server at http://localhost:5000"
echo ""
echo "💡 Try these example messages:"
echo "   • 'Send an email to the team about our meeting'"
echo "   • 'Debug this Python function that's throwing errors'"
echo "   • 'Create a high-energy workout playlist'"
echo "   • 'Research competitor pricing strategies'"
echo "   • 'Schedule a meeting with the design team'"
echo "   • 'Design a logo for our new product'"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the demo web app
python demo_web.py