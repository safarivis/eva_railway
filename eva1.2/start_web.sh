#!/bin/bash
# Start Eva 1.2 Web Interface

echo "🚀 Starting Eva 1.2 Web Interface"
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install required packages
echo "Installing dependencies..."
pip install flask python-dotenv

# Set environment variables for test mode
export EVA12_TEST_MODE=true
export ENABLE_ASSISTANTS_API=true
export ENABLE_THREAD_MANAGEMENT=true
export FALLBACK_TO_EVA=true

echo ""
echo "✅ Eva 1.2 is ready!"
echo ""
echo "🌐 Open your browser and go to:"
echo "   http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the web app
python web_app.py