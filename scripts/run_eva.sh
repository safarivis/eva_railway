#!/bin/bash

# Run Eva Agent
# This script starts both the Eva server and the CLI client

# Create and activate virtual environment if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Start the Eva server in the background
echo "Starting Eva server..."
python core/eva.py &
SERVER_PID=$!

# Wait for the server to start
sleep 3

# Start the CLI client
echo "Starting CLI client..."
python utils/cli_client.py

# When client exits, kill the server
kill $SERVER_PID

echo "Eva agent shutdown complete."