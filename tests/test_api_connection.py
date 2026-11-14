"""
Comprehensive API connection test for AI Voice Assistant.
Tests OpenAI/OpenRouter and Google Gemini APIs, followed by voice output.
"""
import sys
import os
from pathlib import Path

# Add project root and src to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from dotenv import load_dotenv
load_dotenv(ROOT_DIR / ".env")

from ai_processor import AIProcessor
from assistant import AIVoiceAssistant

print("=" * 70)
print("AI Voice Assistant - API & Audio Diagnostics")
print("=" * 70)

openai_key = os.getenv("OPENAI_API_KEY")
google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

print(f"OpenAI / OpenRouter Key : {'Configured (' + openai_key[:15] + '...)' if openai_key else 'Not set'}")
print(f"Google Gemini Key       : {'Configured (' + google_key[:15] + '...)' if google_key else 'Not set'}")

if not openai_key and not google_key:
    print("\n[ERROR] No API keys configured in .env!")
    sys.exit(1)

# 1. Initialize AI Processor
print("\n[1] Initializing AI Processor...")
try:
    ai = AIProcessor()
    if ai.client or ai.gemini_client:
        print("[OK] AI Processor initialized successfully.")
    else:
        print("[ERROR] AI Processor could not initialize any client.")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Failed to initialize AI Processor: {e}")
    sys.exit(1)

# 2. Test Questions
test_questions = [
    ("What is 10 plus 5?", "Logical"),
    ("Why do penguins wear tuxedos?", "Creative"),
]

print("\n[2] Testing AI Generation...")
print("-" * 70)
for question, category in test_questions:
    print(f"\n[{category}] Q: {question}")
    try:
        response = ai.process(question)
        print(f"A: {response}")
    except Exception as e:
        print(f"[ERROR] {e}")

# 3. Test Voice Output
print("\n[3] Testing Voice Output...")
try:
    assistant = AIVoiceAssistant()
    assistant._ensure_voice_components()
    if assistant.voice_output:
        test_msg = "Hello! Voice output is working properly."
        print(f"Speaking: '{test_msg}'")
        assistant.voice_output.speak(test_msg)
        print("[OK] Voice output completed.")
    else:
        print("[INFO] Voice output not available (pyttsx3/audio device missing).")
except Exception as e:
    print(f"[WARNING] Voice output test skipped or failed: {e}")

print("\n" + "=" * 70)
print("Diagnostics Complete!")
print("=" * 70)

