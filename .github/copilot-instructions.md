# AI Voice Assistant - Copilot Instructions

## Project Overview
This is a comprehensive Python-based AI voice assistant with a stunning 3D web interface that combines:
- Speech Recognition (Google Speech API via SpeechRecognition library)
- Natural Language Processing (OpenAI GPT models)
- Text-to-Speech (pyttsx3)
- 3D Particle Visualization (Three.js with neon bloom effects)
- Hand Tracking (MediaPipe Hands)
- Web Interface (Flask)

## Key Components

### Backend
- `src/assistant.py` - Main orchestrator (text, voice, or web mode)
- `src/ai_processor.py` - OpenAI API integration for intelligent responses
- `src/voice_input.py` - Microphone audio capture and transcription
- `src/voice_output.py` - Text-to-speech engine
- `src/web_server.py` - Flask web server with chat API

### Frontend
- `templates/index.html` - 3D visualization interface with chat, hand tracking, and audio visualization

## Features
- ✨ Ultra-bright neon particle effects with bloom post-processing
- 🎨 6 particle shapes (Sphere, Heart, Helix, Torus, Ring, Cloud)
- 👐 Hand tracking and pinch detection via webcam
- 🎤 Audio visualization responding to microphone input
- 💬 Real-time chat interface
- 🎙️ Voice mode with microphone input and speaker output
- 📝 Text mode for terminal-based interaction
- 🌐 Web mode with 3D visualization at http://localhost:5000

## Setup Status
- [x] Project structure created
- [x] All core modules implemented
- [x] Web server with Flask integration
- [x] Dependencies installed and verified
- [x] Documentation complete
- [ ] API key configuration (user action needed)
- [ ] Testing

## Running the Assistant

### Web Mode (Recommended - 3D Visualization)
```bash
python src/assistant.py web
```
Then open: http://localhost:5000

### Text Mode (CLI)
```bash
python src/assistant.py text
```

### Voice Mode (Microphone)
```bash
python src/assistant.py voice
```

## Configuration
1. Set OpenAI API key in `.env`:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

2. (Optional) Customize in `src/ai_processor.py`:
   - System prompt for AI behavior
   - Model selection (gpt-3.5-turbo, gpt-4, etc.)
   - Temperature and max tokens

3. (Optional) Customize visualization in `templates/index.html`:
   - Particle colors
   - Bloom intensity
   - Particle count

## Development Guidelines
- Keep AI responses concise for voice/web interaction (< 30 seconds)
- Test in text mode first before enabling voice
- Maintain conversation history for context (max 10 messages)
- Adjust voice settings in voice_output.py for different environments
- Restart Flask server when modifying templates or web_server.py

## Dependencies
- pyaudio - Audio input/output
- SpeechRecognition - Speech-to-text
- pyttsx3 - Text-to-speech
- openai - AI model access
- python-dotenv - Environment variable management
- flask - Web framework
- flask-cors - Cross-origin support
- requests - HTTP library

## File Structure
```
ai-voice-assistant/
├── src/
│   ├── assistant.py
│   ├── ai_processor.py
│   ├── voice_input.py
│   ├── voice_output.py
│   └── web_server.py
├── templates/
│   └── index.html
├── requirements.txt
├── .env (create this with API key)
├── README.md
├── QUICKSTART.md
└── .github/
    └── copilot-instructions.md
```

## Next Steps
1. Add OpenAI API key to `.env`
2. Run `python src/assistant.py web`
3. Open browser to http://localhost:5000
4. Click "ENGAGE" and start chatting!

