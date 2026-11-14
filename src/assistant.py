"""
Main AI Voice Assistant module that integrates all components.
"""

import os
from typing import Optional
from ai_processor import AIProcessor
from web_server import WebServer


class AIVoiceAssistant:
    def __init__(self, ai_processor: Optional[AIProcessor] = None, api_key: Optional[str] = None):
        """
        Initialize the AI Voice Assistant with all components.
        
        Args:
            ai_processor: existing AIProcessor instance (optional)
            api_key: OpenAI API key (optional)
        """
        print("Initializing AI Voice Assistant...")
        # Voice components are optional and created lazily when needed
        self.voice_input = None
        self.voice_output = None
        if ai_processor:
            self.ai_processor = ai_processor
        else:
            self.ai_processor = AIProcessor(api_key)
        self.running = False

    def _ensure_voice_components(self):
        """Lazily import and initialize voice input/output so web mode won't fail if packages missing."""
        if self.voice_input is None or self.voice_output is None:
            try:
                from voice_input import VoiceInput
                from voice_output import VoiceOutput
                self.voice_input = VoiceInput()
                self.voice_output = VoiceOutput()
            except Exception as e:
                print(f"Error initializing voice components: {e}")
                self.voice_input = None
                self.voice_output = None

    def listen_and_respond(self) -> bool:
        """
        Listen for user voice input, process it with AI, and respond with voice output.
        
        Returns:
            True if successful, False otherwise
        """
        # Step 1: Listen for voice input
        self._ensure_voice_components()
        if not self.voice_input:
            print("Voice input not available")
            return False
        user_input = self.voice_input.listen()
        if not user_input:
            return False
        
        # Step 2: Process with AI
        ai_response = self.ai_processor.process(user_input)
        if not ai_response:
            self.voice_output.speak("I encountered an error processing your request.")
            return False
        
        # Step 3: Output voice response
        if self.voice_output:
            return self.voice_output.speak(ai_response)
        else:
            print(ai_response)
            return True

    def run(self):
        """Run the assistant in a continuous loop."""
        self.running = True
        print("\n🎤 AI Voice Assistant Started!")
        print("Say 'exit' or 'quit' to stop the assistant.")
        print("-" * 50)
        
        self.voice_output.speak("Hello! I'm your AI voice assistant. How can I help you?")
        
        try:
            while self.running:
                success = self.listen_and_respond()
                
                if not success:
                    print("Please try again.\n")
                else:
                    print()
                    
        except KeyboardInterrupt:
            print("\n\nShutting down...")
            self.stop()

    def stop(self):
        """Stop the assistant."""
        self.running = False
        if self.voice_output:
            try:
                self.voice_output.speak("Goodbye!")
            except Exception:
                pass
        print("Assistant stopped.")

    def run_text_mode(self):
        """Run the assistant in text mode for testing without microphone."""
        self.running = True
        print("\n📝 AI Voice Assistant (Text Mode)")
        print("Type 'exit' or 'quit' to stop the assistant.")
        print("-" * 50)
        
        try:
            while self.running:
                try:
                    user_input = input("\nYou: ").strip()
                    
                    if user_input.lower() in ['exit', 'quit']:
                        self.stop()
                        break
                    
                    if not user_input:
                        continue
                    
                    ai_response = self.ai_processor.process(user_input)
                    if ai_response:
                        print(f"Assistant: {ai_response}")
                    else:
                        print("Error: Could not process your input.")
                        
                except KeyboardInterrupt:
                    print("\n\nShutting down...")
                    self.stop()
                    break
                    
        except Exception as e:
            print(f"Error in text mode: {e}")
            self.stop()


if __name__ == "__main__":
    import sys
    
    # Check if API key is set (OpenAI, OpenRouter, or Google Gemini)
    api_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not api_key and not google_key:
        print("⚠️  Warning: Neither OPENAI_API_KEY nor GOOGLE_API_KEY is set.")
        print("Please set your API key in .env file to use the AI features.")
        sys.exit(1)
    
    # Create assistant. Pass api_key as keyword arg to avoid assigning it to ai_processor arg
    assistant = AIVoiceAssistant(api_key=api_key)
    
    # Check command line arguments
    mode = sys.argv[1] if len(sys.argv) > 1 else "text"
    
    if mode == "web":
        # Run in web mode with 3D visualization
        print("\n🌐 Starting AI Voice Assistant in WEB MODE")
        print("🎨 Open your browser at http://localhost:5000")
        web_server = WebServer(assistant.ai_processor, port=5000)
        web_server.run()
    
    elif mode == "voice":
        # Run in voice mode
        print("\n🎤 Starting AI Voice Assistant in VOICE MODE")
        assistant.run()
    
    else:
        # Default: text mode
        print("\n📝 Starting AI Voice Assistant in TEXT MODE")
        assistant.run_text_mode()
