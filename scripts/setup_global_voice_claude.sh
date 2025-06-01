#!/bin/bash

echo "🎤 Setting up Global Voice-to-Claude Code System 🎤"
echo "================================================"

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  This script is designed for Linux. Adjust for your OS."
fi

# Install system dependencies
echo "📦 Installing system dependencies..."

# For Debian/Ubuntu
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y portaudio19-dev python3-pyaudio ffmpeg
    sudo apt-get install -y python3-dev python3-pip
    sudo apt-get install -y flac  # For speech recognition
fi

# For Arch/CachyOS
if command -v pacman &> /dev/null; then
    sudo pacman -S portaudio python-pyaudio ffmpeg flac --noconfirm
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python packages
echo "📦 Installing Python packages..."
pip install --upgrade pip

# Core packages for voice-to-Claude
pip install RealtimeSTT openai pygame sounddevice numpy scipy
pip install pynput pyperclip python-dotenv
pip install SpeechRecognition webrtcvad
pip install anthropic  # For direct Claude API access

# Optional: Install whisper for better STT
pip install openai-whisper

# Create .env file template if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env template..."
    cat > .env << 'EOF'
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here  # Optional if using Claude CLI

# Optional Configuration
CLAUDE_MODEL=claude-3-opus-20240229
TTS_VOICE=nova  # Options: alloy, echo, fable, onyx, nova, shimmer
STT_MODEL=whisper-1
EOF
    echo "⚠️  Please edit .env and add your API keys!"
fi

# Create systemd service for auto-start (optional)
echo "🔧 Creating systemd service file..."
cat > voice-claude.service << EOF
[Unit]
Description=Voice-to-Claude Code Assistant
After=network.target sound.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin:\$PATH"
Environment="DISPLAY=:0"
ExecStart=$(pwd)/venv/bin/python global_voice_claude_setup.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
EOF

echo "📝 To install as system service:"
echo "   sudo cp voice-claude.service /etc/systemd/system/"
echo "   sudo systemctl enable voice-claude"
echo "   sudo systemctl start voice-claude"

# Create desktop entry for easy launch
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/voice-claude.desktop << EOF
[Desktop Entry]
Name=Voice Claude Code
Comment=Voice assistant for Claude Code
Exec=$(pwd)/venv/bin/python $(pwd)/global_voice_claude_setup.py
Icon=microphone
Terminal=true
Type=Application
Categories=Development;Utility;
EOF

# Create launcher script
cat > launch_voice_claude.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python global_voice_claude_setup.py
EOF
chmod +x launch_voice_claude.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file and add your API keys:"
echo "   - OPENAI_API_KEY (required for TTS and optional STT)"
echo "   - ANTHROPIC_API_KEY (optional if using Claude CLI)"
echo ""
echo "2. Install Claude CLI globally (if not already installed):"
echo "   npm install -g @anthropic-ai/claude-cli"
echo ""
echo "3. Test the system:"
echo "   ./launch_voice_claude.sh"
echo ""
echo "4. Optional - Set up global hotkey:"
echo "   - KDE: System Settings → Shortcuts → Add Command"
echo "   - GNOME: Settings → Keyboard → Custom Shortcuts"
echo "   - Command: $(pwd)/launch_voice_claude.sh"
echo ""
echo "🎤 Usage:"
echo "   - Say trigger word (claude/sonnet/opus) + command"
echo "   - Example: 'Claude, create a Python function to sort a list'"
echo "   - Or use push-to-talk mode (Windows key by default)"