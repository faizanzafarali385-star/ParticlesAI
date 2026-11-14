/**
 * Simple test script for the Web Server chat API endpoint.
 * Tests POST http://localhost:5000/api/chat
 */

const TEST_URL = 'http://localhost:5000/api/chat';

async function testChatEndpoint() {
  console.log(`Testing Chat API at: ${TEST_URL}`);
  try {
    const response = await fetch(TEST_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'What is 2 + 2?' }),
    });

    if (!response.ok) {
      console.error(`HTTP error: ${response.status} ${response.statusText}`);
      const text = await response.text();
      console.error('Response:', text);
      return;
    }

    const data = await response.json();
    console.log('[OK] Received API response:');
    console.log('Success  :', data.success);
    console.log('Response :', data.response);
  } catch (err) {
    console.error('[ERROR] Failed to connect to server:', err.message);
    console.error('Ensure either `server.js` or `src/assistant.py web` is running on port 5000.');
  }
}

testChatEndpoint();

