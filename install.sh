#!/bin/bash
# Installation script for Voice Dictation on Mac

set -e

echo "=============================================="
echo "🎙️  Voice Dictation Installation for macOS"
echo "=============================================="
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found!"
    echo ""
    echo "Please install Homebrew first:"
    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo ""
    exit 1
fi

echo "✅ Homebrew found"
echo ""

# Install sox
echo "1️⃣  Installing sox (audio recording)..."
if ! command -v sox &> /dev/null; then
    brew install sox
    echo "   ✅ sox installed"
else
    echo "   ✅ sox already installed"
fi
echo ""

# Install pynput
echo "2️⃣  Installing pynput (keyboard control)..."
if ! python3 -c "import pynput" 2>/dev/null; then
    pip3 install pynput
    echo "   ✅ pynput installed"
else
    echo "   ✅ pynput already installed"
fi
echo ""

# Clone whisper.cpp if needed
WHISPER_DIR="$HOME/whisper.cpp"
if [ ! -d "$WHISPER_DIR" ]; then
    echo "3️⃣  Installing whisper.cpp..."
    cd "$HOME"
    git clone https://github.com/ggml-org/whisper.cpp.git
    cd whisper.cpp
    echo "   ✅ whisper.cpp cloned"
else
    echo "3️⃣  whisper.cpp already installed"
    cd "$WHISPER_DIR"
fi
echo ""

# Build whisper.cpp
echo "4️⃣  Building whisper.cpp..."
if [ ! -f "build/bin/whisper-cli" ]; then
    make
    echo "   ✅ whisper.cpp built"
else
    echo "   ✅ whisper.cpp already built"
fi
echo ""

# Download a model
echo "5️⃣  Downloading Whisper model..."
if [ ! -f "models/ggml-base.bin" ]; then
    bash ./models/download-ggml-model.sh base
    echo "   ✅ Base model downloaded"
else
    echo "   ✅ Model already downloaded"
fi
echo ""

# Make scripts executable
cd "$(dirname "$0")"
chmod +x start-dictation.sh
chmod +x voice_dictation.py

echo "=============================================="
echo "✅ INSTALLATION COMPLETE!"
echo "=============================================="
echo ""
echo "To start using voice dictation:"
echo "  ./start-dictation.sh"
echo ""
echo "Hotkeys:"
echo "  Option+Space        - Push-to-talk recording"
echo "  Command+Option+D    - Toggle live mode"
echo ""
echo "📝 Note: macOS will ask for permissions:"
echo "   - Accessibility (for keyboard control)"
echo "   - Microphone (for recording)"
echo ""
echo "For better Swedish support, install KB-Whisper:"
echo "  cd ~/whisper.cpp"
echo "  bash ./models/download-ggml-model.sh large-v3-turbo-q5_0"
echo ""
