import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import OpenAI from 'openai';
import path from 'path';
import { fileURLToPath } from 'url';

// Load environment variables
dotenv.config({ override: true });

// Verify API key is loaded on startup
const loadedApiKey = process.env.OPENAI_API_KEY;
if (loadedApiKey) {
  console.log('[Server] ✅ API Key loaded from .env');
  console.log('[Server] Key type:', loadedApiKey.startsWith('sk-or-') ? 'OpenRouter' : 'OpenAI');
  console.log('[Server] Key preview:', loadedApiKey.substring(0, 25) + '...');
} else {
  console.error('[Server] ❌ WARNING: No OPENAI_API_KEY found in .env file!');
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Serve static files (HTML, CSS, JS)
app.use(express.static(path.join(__dirname, 'templates')));

// Initialize OpenAI client (supports both OpenAI and OpenRouter)
// Get API key - check both .env and environment variables
let apiKey = process.env.OPENAI_API_KEY;

// Log what we got
console.log('[Server] Environment check:');
console.log('[Server] OPENAI_API_KEY from .env:', apiKey ? apiKey.substring(0, 25) + '...' : 'NOT FOUND');

// If no key from .env, check if there's a system env var (might override)
if (!apiKey || !apiKey.startsWith('sk-or-')) {
  console.warn('[Server] ⚠️  WARNING: API key not found or not OpenRouter format!');
  console.warn('[Server] Make sure .env file has: OPENAI_API_KEY=sk-or-v1-...');
}

let openai;

if (apiKey && apiKey.startsWith('sk-or-')) {
  // OpenRouter API key detected
  openai = new OpenAI({
    apiKey: apiKey,
    baseURL: 'https://openrouter.ai/api/v1',
    defaultHeaders: {
      'HTTP-Referer': 'https://github.com/your-repo',
      'X-Title': 'AI Voice Assistant',
    },
  });
  console.log('[Server] ✅ Using OpenRouter API');
  console.log('[Server] API Key:', apiKey.substring(0, 20) + '...');
} else if (apiKey) {
  // Standard OpenAI API
  openai = new OpenAI({
    apiKey: apiKey,
  });
  console.log('[Server] ✅ Using OpenAI API');
  console.log('[Server] API Key:', apiKey.substring(0, 20) + '...');
} else {
  console.error('[Server] ❌ ERROR: No API key found in environment variables!');
  console.error('[Server] Make sure OPENAI_API_KEY is set in .env file');
}

// Conversation history (in-memory, resets on server restart)
const conversationHistory = [];
const MAX_HISTORY = 10;

// Fallback AI responses (when OpenAI is unavailable)
function generateFallbackResponse(userMessage) {
  const msg = userMessage.toLowerCase().trim();

  // Context-aware fallback responses
  const responses = {
    greetings: [
      "Hello! I'm an AI voice assistant. How can I help you today?",
      "Hi there! Nice to meet you. What would you like to talk about?",
      "Hey! I'm here and ready to chat with you.",
    ],
    time: [
      "I don't have access to the current time, but you can check your device.",
      "That's a great question! I'd need real-time data to answer accurately.",
    ],
    help: [
      "I'm here to help! Feel free to ask me anything.",
      "Sure, I'll do my best to assist you. What do you need?",
      "Of course! I'm happy to help with whatever you need.",
    ],
    name: [
      "I'm an AI Voice Assistant. No specific name, but you can call me what you like!",
      "I'm your friendly AI assistant. Feel free to give me a name if you'd like!",
    ],
    capabilities: [
      "I can chat with you, answer questions, and have conversations. Just speak or type what's on your mind!",
      "I'm here to listen and respond to your messages. Ask me anything and I'll do my best to help.",
    ],
  };

  // Check for keywords and return appropriate response
  if (
    msg.includes('hello') ||
    msg.includes('hi') ||
    msg.includes('hey') ||
    msg.includes('good morning') ||
    msg.includes('good afternoon')
  ) {
    return responses.greetings[Math.floor(Math.random() * responses.greetings.length)];
  }

  if (
    msg.includes('time') ||
    msg.includes('what time') ||
    msg.includes('current time')
  ) {
    return responses.time[Math.floor(Math.random() * responses.time.length)];
  }

  if (
    msg.includes('help') ||
    msg.includes('assist') ||
    msg.includes('support')
  ) {
    return responses.help[Math.floor(Math.random() * responses.help.length)];
  }

  if (
    msg.includes('name') ||
    msg.includes('who are you') ||
    msg.includes('what are you called')
  ) {
    return responses.name[Math.floor(Math.random() * responses.name.length)];
  }

  if (
    msg.includes('can you') ||
    msg.includes('what can') ||
    msg.includes('capabilities')
  ) {
    return responses.capabilities[Math.floor(Math.random() * responses.capabilities.length)];
  }

  // Default response for anything else
  return `That's an interesting question: "${userMessage}". I'm currently running in fallback mode, so I can't provide a full AI response right now. But I'm listening! Try asking me about greetings, my capabilities, or anything else you'd like to know.`;
}

// Fallback to Google Gemini when OpenAI / OpenRouter is unavailable
async function callGemini(message) {
  const geminiKey = (process.env.GOOGLE_API_KEY || process.env.GEMINI_API_KEY || '').trim();
  console.log('[API] callGemini key preview:', geminiKey ? geminiKey.substring(0, 15) : 'NONE');
  if (!geminiKey) return null;
  const models = ['gemini-3.5-flash-lite', 'gemini-3.5-flash', 'gemini-2.5-flash'];
  for (const model of models) {
    try {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;
      const payload = {
        contents: [
          {
            parts: [
              {
                text: `You are a helpful, creative, and engaging AI voice assistant. You answer all questions (logical and creative). Keep your responses concise (2-3 sentences typically).\n\nUser: ${message}`
              }
            ]
          }
        ]
      };
      const resp = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-goog-api-key': geminiKey
        },
        body: JSON.stringify(payload)
      });
      if (resp.ok) {
        const data = await resp.json();
        const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
        if (text) return text.trim();
      } else {
        const errText = await resp.text();
        console.error(`[API] Gemini model ${model} HTTP ${resp.status}:`, errText);
      }
    } catch (e) {
      console.error(`[API] Gemini model ${model} error:`, e.message);
    }
  }
  return null;
}

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

app.post('/api/chat', async (req, res) => {
  try {
    const { message } = req.body;

    console.log('[API] /api/chat called');
    console.log('[API] Received message:', message);

    if (!message || message.trim() === '') {
      return res.status(400).json({
        success: false,
        error: 'Empty message',
      });
    }

    // Add user message to conversation history
    conversationHistory.push({
      role: 'user',
      content: message,
    });

    // Keep conversation history under MAX_HISTORY
    if (conversationHistory.length > MAX_HISTORY * 2) {
      conversationHistory.splice(0, 2);
    }

    console.log('[API] Calling OpenAI API...');
    console.log('[API] OpenAI client initialized:', !!openai);
    console.log('[API] Current API key from env:', apiKey ? apiKey.substring(0, 25) + '...' : 'NOT SET');

    // Try to use OpenAI API
    let aiMessage = null;
    let usedFallback = false;

    try {
      // Check if OpenAI client is initialized
      if (!openai) {
        console.error('[API] ERROR: OpenAI client is not initialized!');
        throw new Error('OpenAI client not initialized. Check API key.');
      }

      // Use appropriate model based on API provider - try multiple formats for OpenRouter
      let model;
      if (apiKey && apiKey.startsWith('sk-or-')) {
        // Try OpenRouter models in order of preference
        model = 'openai/gpt-3.5-turbo';  // OpenRouter format
      } else {
        model = 'gpt-3.5-turbo';  // OpenAI format
      }
      
      console.log('[API] Using model:', model);
      console.log('[API] API Key type:', apiKey && apiKey.startsWith('sk-or-') ? 'OpenRouter' : 'OpenAI');
      
      const response = await openai.chat.completions.create({
        model: model,
        messages: [
          {
            role: 'system',
            content: 'You are a helpful, creative, and engaging AI voice assistant. You answer ALL types of questions - both logical and illogical, serious and fun, realistic and imaginative. For logical questions: Provide accurate, helpful information. For illogical, absurd, or creative questions: Be playful, creative, and entertaining while still being helpful. Keep your responses concise and natural for voice interaction (2-3 sentences typically). Always respond in a friendly, conversational manner.'
          },
          ...conversationHistory
        ],
        max_tokens: 500,  // Increased for full responses
        temperature: 0.7,
      });

      aiMessage = response.choices[0].message.content;
      console.log('[API] AI Response (SUCCESS):', aiMessage.substring(0, 100) + '...');
      usedFallback = false;
    } catch (openaiError) {
      console.error('[API] ========== API ERROR ==========');
      console.error('[API] Error Type:', openaiError.constructor.name);
      console.error('[API] Error Message:', openaiError.message);
      console.error('[API] Error Status:', openaiError.status);
      console.error('[API] Error Code:', openaiError.code);
      if (openaiError.response) {
        console.error('[API] Response Status:', openaiError.response.status);
        console.error('[API] Response Data:', openaiError.response.data);
      }
      console.error('[API] ===============================');
      
      // Try alternative model if first one fails (for OpenRouter)
      if (apiKey && apiKey.startsWith('sk-or-') && openaiError.status !== 401 && openaiError.status !== 403) {
        console.log('[API] Trying alternative model: gpt-3.5-turbo');
        try {
          const altResponse = await openai.chat.completions.create({
            model: 'gpt-3.5-turbo',  // Try without prefix
            messages: [
              {
                role: 'system',
                content: 'You are a helpful, creative, and engaging AI voice assistant. You answer ALL types of questions - both logical and illogical, serious and fun, realistic and imaginative. For logical questions: Provide accurate, helpful information. For illogical, absurd, or creative questions: Be playful, creative, and entertaining while still being helpful. Keep your responses concise and natural for voice interaction (2-3 sentences typically). Always respond in a friendly, conversational manner.'
              },
              ...conversationHistory
            ],
            max_tokens: 500,
            temperature: 0.7,
          });
          aiMessage = altResponse.choices[0].message.content;
          console.log('[API] AI Response (SUCCESS with alt model):', aiMessage.substring(0, 100) + '...');
          usedFallback = false;
        } catch (altError) {
          console.error('[API] Alternative model also failed:', altError.message);
          // Fall through to error handling below
        }
      }
      
      // Try Gemini fallback if primary API failed
      if (!aiMessage && (process.env.GOOGLE_API_KEY || process.env.GEMINI_API_KEY)) {
        console.log('[API] Primary API failed, trying Google Gemini fallback...');
        const geminiResp = await callGemini(message);
        if (geminiResp) {
          aiMessage = geminiResp;
          usedFallback = false;
          console.log('[API] Gemini Response (SUCCESS):', aiMessage.substring(0, 100) + '...');
        }
      }

      // Only use fallback if we still don't have a response
      if (!aiMessage) {
        if (openaiError.status === 401 || openaiError.status === 403) {
          aiMessage = "I'm sorry, but there's an authentication issue with my API key. Please check your API key configuration.";
          usedFallback = false;
        } else if (openaiError.status === 429) {
          aiMessage = "I'm being rate limited. Please wait a moment and try again.";
          usedFallback = false;
        } else {
          // Last resort - use fallback, but log it clearly
          console.error('[API] CRITICAL: Using fallback response - API call failed');
          aiMessage = generateFallbackResponse(message);
          usedFallback = true;
        }
      }
    }

    // Add AI response to history
    conversationHistory.push({
      role: 'assistant',
      content: aiMessage,
    });

    return res.json({
      success: true,
      response: aiMessage,
      user_input: message,
      using_fallback: usedFallback,
    });
  } catch (error) {
    console.error('[API] Critical Error:', error.message);

    // Ultimate fallback for unexpected errors
    const fallback =
      "I encountered an unexpected error, but I'm still here! Try asking me hello or tell me what you need.";

    return res.status(500).json({
      success: false,
      error: error.message || 'Failed to process message',
      fallback: fallback,
    });
  }
});

app.get('/api/status', (req, res) => {
  const apiKey = process.env.OPENAI_API_KEY;
  const apiKeyConfigured = !!apiKey && apiKey !== '';
  const apiKeyPreview = apiKey
    ? apiKey.substring(0, 10) + '...'
    : 'NOT SET';

  res.json({
    status: 'online',
    model: 'gpt-3.5-turbo',
    conversation_length: conversationHistory.length,
    api_key_configured: apiKeyConfigured,
    api_key_preview: apiKeyPreview,
  });
});

app.get('/api/test', async (req, res) => {
  try {
    console.log('[TEST] Testing OpenAI API...');

    const response = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [
        {
          role: 'user',
          content: 'Say hello!',
        },
      ],
      max_tokens: 50,
    });

    const testResponse = response.choices[0].message.content;

    return res.json({
      success: true,
      test: 'passed',
      response: testResponse,
    });
  } catch (error) {
    console.error('[TEST] Error:', error.message);
    return res.status(500).json({
      success: false,
      test: 'failed',
      error: error.message,
    });
  }
});

app.post('/api/reset', (req, res) => {
  conversationHistory.length = 0;
  console.log('[API] Conversation reset');

  return res.json({
    success: true,
    message: 'Conversation reset',
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not found',
    path: req.path,
  });
});

// Start server
app.listen(PORT, () => {
  console.log('\n[WebServer] All registered routes:');
  console.log('  GET  / (serves index.html)');
  console.log('  POST /api/chat');
  console.log('  GET  /api/status');
  console.log('  GET  /api/test');
  console.log('  POST /api/reset');

  console.log(`\n🌐 Web Server Starting at http://localhost:${PORT}`);
  console.log('🎨 Open your browser and visit the URL above');
  console.log('[WebServer] Press Ctrl+C to stop the server\n');
});
