#!/bin/bash
# Toggle voice dictation on/off with a single key

PIDFILE="/tmp/nerd-dictation.pid"
MODEL_DIR="$HOME/.config/nerd-dictation/vosk-model-small-en-us-0.15"

if [ -f "$PIDFILE" ]; then
    # Dictation is running, stop it
    nerd-dictation end
    rm -f "$PIDFILE"
    # Optional: Play stop sound
    # paplay /usr/share/sounds/freedesktop/stereo/complete.oga &
else
    # Dictation is not running, start it
    nerd-dictation begin --vosk-model-dir "$MODEL_DIR" &
    echo $! > "$PIDFILE"
    # Optional: Play start sound  
    # paplay /usr/share/sounds/freedesktop/stereo/message.oga &
fi