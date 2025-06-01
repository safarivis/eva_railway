#!/usr/bin/env python3
import subprocess
import sys

print("Starting EVA server...")
print("Access the interface at: http://localhost:8000/static/index_private.html")
print("Press Ctrl+C to stop\n")

try:
    subprocess.run([sys.executable, "eva.py"], cwd="/home/ldp/louisdup/agents/eva_agent")
except KeyboardInterrupt:
    print("\nServer stopped.")