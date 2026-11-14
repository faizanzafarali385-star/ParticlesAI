"""
Voice input module for capturing audio from the microphone and converting it to text.
"""

import speech_recognition as sr
from typing import Optional


class VoiceInput:
    def __init__(self):
        """Initialize the speech recognizer."""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def listen(self, timeout: int = 10) -> Optional[str]:
        """
        Listen to audio input from the microphone and convert it to text.
        
        Args:
            timeout: Maximum time in seconds to listen for audio
            
        Returns:
            Transcribed text or None if no speech detected
        """
        try:
            with self.microphone as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=timeout)
            
            print("Processing audio...")
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
            
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand what you said.")
            return None
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
