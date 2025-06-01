#!/bin/bash
# Restart EVA with new configuration

echo "Stopping EVA server..."
pkill -f "python eva.py" || true
pkill -f "uvicorn" || true
sleep 2

echo "Starting EVA server with new configuration..."
cd /home/ldp/louisdup/agents/eva_agent
python eva.py