#!/usr/bin/env python3
"""
Voice Dictation for macOS using whisper.cpp
Two modes:
  1. Push-to-talk: Option+Space to toggle recording
  2. Live mode: Command+Option+D to toggle continuous listening
"""

import subprocess
import threading
import os
import signal
import tempfile
import time
from pynput import keyboard
from pynput.keyboard import Key, Controller

# Configuration - will be auto-detected
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WHISPER_CPP_DIR = os.path.join(os.path.expanduser("~"), "whisper.cpp")
WHISPER_PATH = os.path.join(WHISPER_CPP_DIR, "build/bin/whisper-cli")

# Try to find the best available model
def find_model():
    """Find the best available Whisper model"""
    models_dir = os.path.join(WHISPER_CPP_DIR, "models")

    # Preferred models in order
    preferred_models = [
        "ggml-kb-whisper-large-q5.bin",  # KB-Whisper (best for Swedish)
        "ggml-large-v3-turbo-q5_0.bin",  # Large turbo
        "ggml-medium.bin",                # Medium
        "ggml-small.bin",                 # Small
        "ggml-base.bin",                  # Base
    ]

    for model in preferred_models:
        model_path = os.path.join(models_dir, model)
        if os.path.exists(model_path):
            return model_path

    # Fallback: find any .bin file
    if os.path.exists(models_dir):
        for f in os.listdir(models_dir):
            if f.endswith(".bin"):
                return os.path.join(models_dir, f)

    return None

MODEL_PATH = find_model()
RECORD_COMMAND = "rec"  # sox command for recording

# State
dictation_mode = "push-to-talk"  # "push-to-talk" or "live"
is_recording = False
recording_process = None
temp_audio_file = None
recording_start_time = None
keyboard_controller = Controller()

# Live mode state
live_mode_active = False
live_mode_thread = None
live_mode_stop_event = threading.Event()

def record_audio(output_file):
    """Record audio using sox (rec command)"""
    try:
        # Record audio: 16kHz, mono, 16-bit WAV
        cmd = ["rec", "-r", "16000", "-c", "1", "-b", "16", output_file]
        return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("Error: 'sox' not found. Install it with: brew install sox")
        return None

def transcribe_audio(audio_file):
    """Transcribe audio file using whisper.cpp"""
    try:
        cmd = [
            WHISPER_PATH,
            "-m", MODEL_PATH,
            "-f", audio_file,
            "-nt",  # No timestamps
            "-np",  # No progress
            "-l", "auto",  # Auto-detect language (Swedish or English)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minutes for longer audio
        )

        # Extract transcription from output
        output = result.stdout + result.stderr

        # Find the transcribed text
        lines = output.split('\n')
        transcription = ""
        for line in lines:
            # Skip empty lines and system info
            if line.strip() and not line.startswith('[') and 'whisper' not in line.lower() and 'system' not in line.lower():
                # Remove leading/trailing whitespace and brackets
                clean_line = line.strip()
                if clean_line and not clean_line.startswith('main:'):
                    transcription += clean_line + " "

        transcription = transcription.strip()

        # Filter out blank audio markers and system messages
        if not transcription or transcription in ["[BLANK_AUDIO]", "[SOUND]", "[MUSIC]", "[NOISE]", ""]:
            return ""

        # Remove any remaining markers
        transcription = transcription.replace("[BLANK_AUDIO]", "").replace("[SOUND]", "").replace("[MUSIC]", "").replace("[NOISE]", "").strip()

        return transcription
    except Exception as e:
        print(f"Error transcribing: {e}")
        return ""

def type_text(text):
    """Type the transcribed text using keyboard simulation"""
    if text:
        print(f"Typing: {text}")
        keyboard_controller.type(text)

def detect_silence(audio_file, threshold_seconds=1.5):
    """Check if audio file ends with silence"""
    try:
        # Use sox to detect silence at the end
        result = subprocess.run(
            ["sox", audio_file, "-n", "stat"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Simple check: if file is very small, it's probably silence
        if os.path.exists(audio_file):
            size = os.path.getsize(audio_file)
            # Less than 50KB for 1.5 seconds = likely silence
            if size < 50000:
                return True
        return False
    except:
        return False

def live_mode_worker():
    """Worker thread for live mode continuous listening"""
    global live_mode_stop_event

    print("🎤 Live mode: Listening continuously...")
    print("   Speak naturally - I'll transcribe when you pause!")

    chunk_duration = 5  # Record in 5-second chunks
    silence_chunks = 0
    accumulated_audio_files = []

    while not live_mode_stop_event.is_set():
        # Record a chunk
        chunk_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        rec_process = record_audio(chunk_file)

        if rec_process is None:
            break

        # Wait for chunk duration
        time.sleep(chunk_duration)

        # Stop recording this chunk
        rec_process.terminate()
        rec_process.wait()

        # Check if chunk has speech
        if os.path.exists(chunk_file) and os.path.getsize(chunk_file) > 100000:
            # Has audio, accumulate it
            accumulated_audio_files.append(chunk_file)
            silence_chunks = 0
            print("🎙️  [Speaking detected...]")
        else:
            # Silence detected
            silence_chunks += 1
            os.remove(chunk_file)

            # If we have accumulated audio and now silence, transcribe!
            if accumulated_audio_files and silence_chunks >= 1:
                print("⏸️  [Pause detected - transcribing...]")

                # Combine all accumulated audio files
                if len(accumulated_audio_files) == 1:
                    combined_file = accumulated_audio_files[0]
                else:
                    # Merge audio files with sox
                    combined_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
                    try:
                        subprocess.run(
                            ["sox"] + accumulated_audio_files + [combined_file],
                            check=True,
                            capture_output=True,
                            timeout=10
                        )
                    except:
                        combined_file = accumulated_audio_files[0]

                # Transcribe
                transcription = transcribe_audio(combined_file)

                if transcription:
                    type_text(transcription + " ")
                    print("✅ Transcribed!")

                # Cleanup
                for f in accumulated_audio_files:
                    try:
                        os.remove(f)
                    except:
                        pass

                if combined_file not in accumulated_audio_files:
                    try:
                        os.remove(combined_file)
                    except:
                        pass

                accumulated_audio_files = []
                silence_chunks = 0

    # Cleanup on exit
    for f in accumulated_audio_files:
        try:
            os.remove(f)
        except:
            pass

    print("⏹️  Live mode stopped")

def toggle_live_mode():
    """Toggle live mode on/off"""
    global live_mode_active, live_mode_thread, live_mode_stop_event, dictation_mode

    if not live_mode_active:
        # Start live mode
        print("\n" + "=" * 60)
        print("🔴 LIVE MODE ACTIVATED")
        print("=" * 60)
        print("I'm now listening continuously!")
        print("Speak naturally and I'll transcribe when you pause.")
        print()
        print("Press Command+Option+D again to stop live mode")
        print("=" * 60)
        print()

        live_mode_active = True
        dictation_mode = "live"
        live_mode_stop_event.clear()
        live_mode_thread = threading.Thread(target=live_mode_worker, daemon=True)
        live_mode_thread.start()
    else:
        # Stop live mode
        print("\n" + "=" * 60)
        print("⏹️  STOPPING LIVE MODE...")
        print("=" * 60)

        live_mode_active = False
        dictation_mode = "push-to-talk"
        live_mode_stop_event.set()

        if live_mode_thread:
            live_mode_thread.join(timeout=2)

        print("✅ Switched back to push-to-talk mode")
        print("   Use Option+Space for manual recording")
        print("=" * 60)
        print()

def toggle_recording():
    """Toggle recording on/off (push-to-talk mode)"""
    global is_recording, recording_process, temp_audio_file, recording_start_time

    # Don't allow push-to-talk while in live mode
    if live_mode_active:
        print("⚠️  Live mode is active! Use Command+Option+D to exit live mode first.")
        return

    if not is_recording:
        # Start recording
        print("\n🎤 Recording started... (Press Option+Space again to stop)")
        print("   💡 Tip: 5-30 seconds = best results!")
        is_recording = True
        recording_start_time = time.time()

        # Create temporary file for audio
        temp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name

        # Start recording
        recording_process = record_audio(temp_audio_file)

        if recording_process is None:
            is_recording = False
            print("❌ Failed to start recording")
    else:
        # Stop recording
        recording_duration = time.time() - recording_start_time if recording_start_time else 0
        print(f"⏹️  Recording stopped ({int(recording_duration)}s). Transcribing...")

        if recording_duration > 30:
            print("   ⚠️  Long audio may take time & reduce accuracy. Try 5-30s segments!")

        is_recording = False

        if recording_process:
            recording_process.terminate()
            recording_process.wait()
            recording_process = None

            # Wait a moment for file to be fully written
            time.sleep(0.2)

            # Transcribe
            if os.path.exists(temp_audio_file) and os.path.getsize(temp_audio_file) > 1000:
                transcription = transcribe_audio(temp_audio_file)

                if transcription:
                    # Type the transcription
                    type_text(transcription)
                    print("✅ Transcription complete!")
                else:
                    print("⚠️  No speech detected (silence or too short)")
            else:
                print("⚠️  Audio file is too short or doesn't exist")

            # Clean up
            try:
                os.remove(temp_audio_file)
            except:
                pass

def on_activate_push_to_talk():
    """Hotkey activation callback for push-to-talk"""
    toggle_recording()

def on_activate_toggle_live():
    """Hotkey activation callback for live mode toggle"""
    toggle_live_mode()

def main():
    """Main function"""
    # Check if whisper.cpp is installed
    if not os.path.exists(WHISPER_CPP_DIR):
        print("=" * 60)
        print("❌ ERROR: whisper.cpp not found!")
        print("=" * 60)
        print()
        print(f"Expected location: {WHISPER_CPP_DIR}")
        print()
        print("Please install whisper.cpp first:")
        print("  cd ~")
        print("  git clone https://github.com/ggml-org/whisper.cpp.git")
        print("  cd whisper.cpp")
        print("  make")
        print("  bash ./models/download-ggml-model.sh base")
        print()
        return

    if not MODEL_PATH or not os.path.exists(MODEL_PATH):
        print("=" * 60)
        print("❌ ERROR: No Whisper model found!")
        print("=" * 60)
        print()
        print("Please download a model:")
        print("  cd ~/whisper.cpp")
        print("  bash ./models/download-ggml-model.sh base")
        print()
        print("For Swedish (recommended):")
        print("  bash ./models/download-ggml-model.sh large-v3-turbo-q5_0")
        print()
        return

    print("=" * 60)
    print("🎙️  Voice Dictation System - Dual Mode")
    print("=" * 60)
    print(f"Model: {os.path.basename(MODEL_PATH)}")
    print(f"Whisper: {WHISPER_PATH}")
    print()
    print("📋 MODES:")
    print()
    print("1️⃣  PUSH-TO-TALK MODE (default)")
    print("   Hotkey: Option+Space")
    print("   • Press once to start recording")
    print("   • Press again to stop and transcribe")
    print("   • Best for: precise control, 5-30 second chunks")
    print()
    print("2️⃣  LIVE MODE")
    print("   Hotkey: Command+Option+D (toggle on/off)")
    print("   • Listens continuously")
    print("   • Auto-transcribes when you pause")
    print("   • Best for: natural speech, longer dictation")
    print()
    print("Current mode: PUSH-TO-TALK")
    print()
    print("Press Ctrl+C to exit")
    print("=" * 60)
    print()

    # Check if sox is installed
    try:
        subprocess.run(["which", "rec"], check=True, capture_output=True)
    except:
        print("⚠️  Warning: 'sox' not found. Installing...")
        print("Installing sox via Homebrew...")
        subprocess.run(["brew", "install", "sox"], check=False)

    # Set up global hotkeys
    with keyboard.GlobalHotKeys({
        '<alt>+<space>': on_activate_push_to_talk,
        '<cmd>+<alt>+d': on_activate_toggle_live
    }) as listener:
        listener.join()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
        if recording_process:
            recording_process.terminate()
        if live_mode_active:
            live_mode_stop_event.set()
