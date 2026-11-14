"""
Voice output module for converting text to speech.
"""

import pyttsx3
from typing import Optional


class VoiceOutput:
    def __init__(self):
        """Initialize the text-to-speech engine."""
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)

    def speak(self, text: str) -> bool:
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Assistant: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
            return False

    def set_voice(self, voice_id: int = 0):
        """
        Set the voice for text-to-speech.
        
        Args:
            voice_id: Index of the voice to use (0=default, 1=alternative, etc.)
        """
        try:
            voices = self.engine.getProperty('voices')
            if voice_id < len(voices):
                self.engine.setProperty('voices', voices[voice_id].id)
        except Exception as e:
            print(f"Error setting voice: {e}")

    def set_speed(self, speed: int = 150):
        """
        Set the speech speed.
        
        Args:
            speed: Words per minute (50-300)
        """
        self.engine.setProperty('rate', max(50, min(300, speed)))

    def set_volume(self, volume: float = 0.9):
        """
        Set the speech volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
