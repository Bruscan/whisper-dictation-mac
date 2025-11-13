#!/bin/bash
# Voice Dictation Launcher
# Start the voice dictation system

cd "$(dirname "$0")"

echo "🎙️  Starting Voice Dictation System..."
echo "   Hotkey: Option+Space (⌥ + Space)"
echo ""
echo "   Press the hotkey once to START recording"
echo "   Press it again to STOP and transcribe"
echo ""
echo "   For live mode: Command+Option+D (⌘ + ⌥ + D)"
echo ""
echo "   Press Ctrl+C to exit this program"
echo ""

# Check if pynput is installed
if ! python3 -c "import pynput" 2>/dev/null; then
    echo "📦 Installing pynput..."
    pip3 install pynput
fi

# Run the dictation script
python3 voice_dictation.py
