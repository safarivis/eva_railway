#!/bin/bash

echo "🎤 Setting up Voice Dictation for Linux (CachyOS) 🎤"
echo "================================================"

# Install nerd-dictation from AUR
echo "Installing nerd-dictation..."
yay -S nerd-dictation-git

# Download a voice model
echo "Downloading English voice model..."
mkdir -p ~/.config/nerd-dictation
cd ~/.config/nerd-dictation

# Download the small English model (faster, less accurate)
if [ ! -d "vosk-model-small-en-us-0.15" ]; then
    echo "Downloading voice model..."
    wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip vosk-model-small-en-us-0.15.zip
    rm vosk-model-small-en-us-0.15.zip
fi

# Create convenience scripts
echo "Creating convenience scripts..."

# Create start script
cat > ~/bin/voice-start.sh << 'EOF'
#!/bin/bash
nerd-dictation begin --vosk-model-dir ~/.config/nerd-dictation/vosk-model-small-en-us-0.15
EOF

# Create stop script  
cat > ~/bin/voice-stop.sh << 'EOF'
#!/bin/bash
nerd-dictation end
EOF

# Make scripts executable
chmod +x ~/bin/voice-start.sh
chmod +x ~/bin/voice-stop.sh

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Add keyboard shortcuts in your desktop environment:"
echo "   - Start dictation: ~/bin/voice-start.sh"
echo "   - Stop dictation: ~/bin/voice-stop.sh"
echo ""
echo "2. Suggested shortcuts:"
echo "   - Start: Super+Alt+D (or any combo you prefer)"
echo "   - Stop: Super+Alt+S"
echo ""
echo "3. To use with Windsurf/Cursor:"
echo "   - Click in the prompt field"
echo "   - Press your start shortcut"
echo "   - Speak: 'Create a Python function that...'"
echo "   - Press your stop shortcut"
echo "   - The text appears and you can submit!"
echo ""
echo "🎯 For better accuracy, you can download the larger model:"
echo "   wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"