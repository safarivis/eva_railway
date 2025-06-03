# How to Run EVA Agent and EVA Chat

## Running EVA Agent (Server + CLI)

The EVA Agent consists of a server component and a CLI client. To run both together:

```bash
# From the project root directory
bash scripts/run_eva.sh
```

This script will:
1. Create a virtual environment (if it doesn't exist)
2. Install required dependencies
3. Start the EVA server in the background
4. Launch the CLI client for interaction

### Web Interface
Once the server is running, you can access the web interface at:
- http://localhost:8000/static/index_private.html

### Server Only
If you only want to run the server component:

```bash
# Activate the virtual environment
source venv/bin/activate

# Run the server
python core/eva.py
```

## Running EVA Chat (Standalone Chat Interface)

For a simplified chat interface without the full server:

```bash
# Activate the virtual environment
source venv/bin/activate

# Run the chat interface
python eva_chat.py
```

### EVA Chat Commands
- Type `exit` to quit the chat
- Type `/help` to see all available commands

## Troubleshooting

If you encounter dependency issues, make sure to activate the virtual environment:

```bash
source venv/bin/activate
```

If the virtual environment doesn't exist or is missing dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
