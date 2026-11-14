"""
AI processor module for processing user input and generating responses.
Supports multiple AI providers: OpenAI, OpenRouter, and Google Gemini.
"""

import os
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

# Try to import Google Gemini
GEMINI_AVAILABLE = False
genai = None

# Try google.generativeai first, then google.genai as fallback
try:
    import google.generativeai as genai  # pyright: ignore[reportMissingImports]
    GEMINI_AVAILABLE = True
    print("[AIProcessor] Loaded google.generativeai")
except ImportError:
    try:
        from google import genai  # pyright: ignore[reportMissingImports]
        GEMINI_AVAILABLE = True
        print("[AIProcessor] Loaded google.genai")
    except ImportError:
        GEMINI_AVAILABLE = False
        print("[AIProcessor] Could not load Google Gemini libraries")


class AIProcessor:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI processor with OpenAI API.
        
        Args:
            api_key: OpenAI API key. If not provided, will use OPENAI_API_KEY env variable
        """
        load_dotenv()
        
        # Initialize history first to prevent 500 errors if init fails later
        self.conversation_history = []
        
        # Get API keys from environment
        openai_key = api_key or os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        
        # Initialize AI clients with fallback support
        self.client = None
        self.gemini_client = None
        self.is_openrouter = False
        self.use_gemini = False
        
        # Priority: OpenRouter/OpenAI first, then Gemini as fallback
        if openai_key:
            # Check if this is an OpenRouter API key (starts with sk-or-)
            if openai_key.startswith("sk-or-"):
                # Use OpenRouter API endpoint with required headers
                self.client = OpenAI(
                    api_key=openai_key,
                    base_url="https://openrouter.ai/api/v1",
                    default_headers={
                        "HTTP-Referer": "https://github.com/your-repo",
                        "X-Title": "AI Voice Assistant"
                    }
                )
                self.is_openrouter = True
                print("[AIProcessor] Using OpenRouter API (Primary)")
            else:
                # Use standard OpenAI API
                self.client = OpenAI(api_key=openai_key)
                self.is_openrouter = False
                print("[AIProcessor] Using OpenAI API (Primary)")
        
        # Initialize Gemini as fallback if available
        print(f"[AIProcessor] Checking Gemini availability: Available={GEMINI_AVAILABLE}, Key={gemini_key[:10] if gemini_key else 'None'}...")
        if GEMINI_AVAILABLE and gemini_key:
            try:
                # Configure with REST transport to avoid gRPC connection hangs on Windows
                genai.configure(api_key=gemini_key, transport='rest')
                
                # Active model candidates in priority order
                self.gemini_models = [
                    'gemini-3.5-flash-lite',
                    'gemini-3.5-flash',
                    'gemini-2.5-flash',
                    'gemini-3.8-flash',
                    'gemini-flash-latest'
                ]
                self.gemini_client = genai.GenerativeModel(self.gemini_models[0])
                self.gemini_active_model = self.gemini_models[0]
                print(f"[AIProcessor] Google Gemini API configured ({self.gemini_active_model})")
                
            except Exception as e:
                print(f"[AIProcessor] Gemini initialization failed: {e}")
                self.gemini_client = None
                self.gemini_models = []
                self.gemini_active_model = None
        
        if not self.client and not self.gemini_client:
            print("[AIProcessor] Warning: No API keys provided. AI features will not work.")
        
        self.system_prompt = """You are a helpful, creative, and engaging AI voice assistant. 
You answer ALL types of questions - both logical and illogical, serious and fun, realistic and imaginative.
For logical questions: Provide accurate, helpful information.
For illogical, absurd, or creative questions: Be playful, creative, and entertaining while still being helpful. Use humor, imagination, and creative thinking.
Keep your responses concise and natural for voice interaction (2-3 sentences typically).
Always respond in a friendly, conversational manner. Be engaging and make the conversation enjoyable."""

    def process(self, user_input: str) -> Optional[str]:
        """
        Process user input and generate an AI response.
        
        Args:
            user_input: The user's message
            
        Returns:
            AI-generated response or None if there's an error
        """
        try:
            # Check if any client is initialized
            if not self.client and not self.gemini_client:
                return "I'm sorry, but I need an API key to function. Please set OPENAI_API_KEY or GOOGLE_API_KEY in your .env file."
            
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            print(f"[AIProcessor] Processing: {user_input}")
            
            assistant_response = None
            
            # Try primary provider (OpenAI/OpenRouter) first
            if self.client:
                try:
                    print(f"[AIProcessor] Trying primary API (OpenAI/OpenRouter)...")
                    
                    # Get response from OpenAI/OpenRouter
                    if getattr(self, 'is_openrouter', False):
                        model = "openai/gpt-3.5-turbo"
                    else:
                        model = "gpt-3.5-turbo"
                    
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": self.system_prompt},
                            *self.conversation_history
                        ],
                        temperature=0.7,
                        max_tokens=500
                    )
                    
                    assistant_response = response.choices[0].message.content
                    print(f"[AIProcessor] Primary API response: {assistant_response[:100]}...")
                    
                except Exception as e:
                    print(f"[AIProcessor] Primary API failed: {e}")
                    # Fall through to Gemini
            
            # Fallback to Gemini if primary failed or not available
            if not assistant_response and self.gemini_client:
                print(f"[AIProcessor] Trying fallback API (Google Gemini)...")
                
                # Build conversation context for Gemini
                conversation_text = self.system_prompt + "\n\n"
                for msg in self.conversation_history[-6:]:  # Last 6 messages for context
                    role = "User" if msg["role"] == "user" else "Assistant"
                    conversation_text += f"{role}: {msg['content']}\n\n"
                
                models_to_try = [self.gemini_active_model] + [m for m in getattr(self, 'gemini_models', []) if m != self.gemini_active_model]
                for model_name in models_to_try:
                    try:
                        print(f"[AIProcessor] Attempting Gemini with model '{model_name}'...")
                        client = genai.GenerativeModel(model_name)
                        gemini_response = client.generate_content(
                            conversation_text,
                            generation_config={
                                'temperature': 0.7,
                                'max_output_tokens': 500,
                            }
                        )
                        assistant_response = gemini_response.text
                        self.gemini_active_model = model_name
                        self.gemini_client = client
                        print(f"[AIProcessor] Gemini ({model_name}) response: {assistant_response[:100]}...")
                        break
                    except Exception as e:
                        error_msg = str(e)
                        print(f"[AIProcessor] Gemini model '{model_name}' failed: {error_msg}")
                        if "quota" in error_msg.lower() or "429" in error_msg:
                            print("[AIProcessor] Gemini quota exceeded")
                            break
            
            if not assistant_response:
                return "I'm sorry, but I couldn't get a response from any AI service. Please check your API keys and try again."
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_response
            })
            
            # Keep conversation history manageable (last 10 messages)
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return assistant_response
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            print(f"[AIProcessor] Error: {error_type}: {error_msg}")
            
            # Provide helpful fallback responses that can be spoken
            if "quota" in error_msg.lower() or "429" in error_msg:
                return "I'm sorry, but I've reached my API quota limit. Please check your OpenAI account billing or try again later."
            elif "api key" in error_msg.lower() or "authentication" in error_msg.lower():
                return "I'm sorry, but there's an issue with my API key. Please check your OpenAI API key configuration."
            elif "rate limit" in error_msg.lower():
                return "I'm being rate limited. Please wait a moment and try again."
            else:
                return f"I encountered an error: {error_type}. Please try again or check your connection."

    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []

    def set_system_prompt(self, prompt: str):
        """
        Set a custom system prompt for the AI.
        
        Args:
            prompt: Custom system prompt
        """
        self.system_prompt = prompt
