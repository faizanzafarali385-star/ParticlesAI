# Quick Start Guide

## 🚀 Getting Started

### 1. Configure Your API Key

Edit [.env](.env) and provide either a Google Gemini key or an OpenAI / OpenRouter key:

**Option A: Google Gemini (Recommended - Free)**
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```
Get a free key: https://aistudio.google.com/apikey

**Option B: OpenAI or OpenRouter**
```env
OPENAI_API_KEY=sk-your-key-here
# or for OpenRouter:
# OPENAI_API_KEY=sk-or-v1-your-openrouter-key-here
```

### 2. Run in Web Mode (Recommended)

**Quickest way on Windows:**
Double-click `START_WEB.bat` in the project folder.

**Or via Terminal (PowerShell / Command Prompt):**
```bash
cd "c:\Users\faiza\OneDrive\Desktop\Completed\par_4.0"
.venv\Scripts\activate
python src/assistant.py web
```

Then open your browser:
```
http://localhost:5000
```

### 3. Interact with the Assistant

**In Web Mode:**
- Click "ENGAGE" to start the visualization
- Type your questions in the chat box at the top right
- Click shapes to change the particle visualization
- Use your hand with a webcam for hand tracking

**In Text Mode:**
```bash
.venv\Scripts\activate
python src/assistant.py text
```

**In Voice Mode:**
```bash
.venv\Scripts\activate
python src/assistant.py voice
```

---

## 🎨 Web Interface Features

| Feature | Description |
|---------|-------------|
| **Neon Particles** | 7000 ultra-bright glowing particles |
| **Shapes** | 6 different particle formations (Sphere, Heart, Helix, Torus, Ring, Cloud) |
| **Hand Tracking** | Move hand left/right to rotate, pinch to compress |
| **Audio Visualization** | Responds to microphone audio |
| **Chat Box** | Type natural language questions |
| **Real-time AI** | Instant responses from OpenAI GPT |

---

## ⚙️ Troubleshooting

### Web server won't start
- Make sure port 5000 is not in use
- Check firewall settings

### Chat not responding
- Verify OpenAI API key is set in [.env](.env)
- Check you have available OpenAI credits

### Hand tracking not working
- Allow webcam access when prompted
- Ensure good lighting
- Position camera 1-2 feet away

### Visualization is slow
- Close other applications
- Use a better GPU or reduce particle count in code
- Try a different browser

---

## 📚 Project Files

- [src/assistant.py](src/assistant.py) - Main entry point
- [src/ai_processor.py](src/ai_processor.py) - AI engine
- [src/voice_input.py](src/voice_input.py) - Speech recognition
- [src/voice_output.py](src/voice_output.py) - Text-to-speech
- [src/web_server.py](src/web_server.py) - Flask server
- [templates/index.html](templates/index.html) - Web interface
- [requirements.txt](requirements.txt) - Dependencies

---

## 🔧 Customization

### Change particle colors
Edit [templates/index.html](templates/index.html):
```javascript
const CONFIG = {
    colorBase: 0x00ffff,   // Cyan
    colorHot: 0xff00aa     // Magenta
};
```

### Adjust bloom intensity
Edit same file:
```javascript
bloomStrength: 3.5,    // Increase for more glow
bloomRadius: 0.8,      // Increase for wider glow
```

### Customize AI behavior
Edit [src/ai_processor.py](src/ai_processor.py):
```python
self.system_prompt = """Your custom prompt here"""
```

---

## 🎯 Next Steps

1. ✅ Run `python src/assistant.py web`
2. ✅ Open http://localhost:5000
3. ✅ Click ENGAGE
4. ✅ Type a question
5. ✅ Watch the neon particles respond!

Enjoy your AI Voice Assistant! 🚀
