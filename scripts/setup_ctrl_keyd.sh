#!/bin/bash

echo "🎮 Setting up Ctrl key as voice dictation toggle"
echo "=============================================="

# Install keyd
echo "Installing keyd..."
yay -S keyd

# Create config directory
sudo mkdir -p /etc/keyd/

# Create keyd config
echo "Creating keyd configuration..."
sudo tee /etc/keyd/default.conf > /dev/null << 'EOF'
[ids]
*

[main]
# Make right ctrl toggle voice dictation when tapped
rightctrl = overload(control, cmd:~/louisdup/agents/eva_agent/voice_toggle.sh)

# Keep left ctrl as normal
leftctrl = control
EOF

# Copy toggle script to home bin
mkdir -p ~/bin
cp ~/louisdup/agents/eva_agent/voice_toggle.sh ~/bin/
chmod +x ~/bin/voice_toggle.sh

# Enable and start keyd
echo "Enabling keyd service..."
sudo systemctl enable keyd
sudo systemctl start keyd

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 How to use:"
echo "   - Tap RIGHT CTRL to start/stop voice dictation"
echo "   - LEFT CTRL works normally for shortcuts"
echo ""
echo "🎯 Test it now:"
echo "   1. Open any text editor"
echo "   2. Tap right Ctrl once"
echo "   3. Start speaking"
echo "   4. Tap right Ctrl again to stop"
echo ""
echo "Note: First run setup_voice_dictation.sh if you haven't already!"