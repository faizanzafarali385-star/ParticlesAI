"""
Test module for voice input (microphone) and voice output (TTS).
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from voice_output import VoiceOutput

def test_tts():
    print("Testing Text-to-Speech...")
    tts = VoiceOutput()
    success = tts.speak("Testing speech synthesis. Everything is sounding clear.")
    if success:
        print("[OK] Text-to-speech test passed.")
    else:
        print("[WARNING] Text-to-speech failed.")

if __name__ == "__main__":
    test_tts()

