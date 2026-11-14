"""
Web server module for serving the 3D visualization interface.
Uses Flask to create a web app that integrates with the AI voice assistant.
"""

from flask import Flask, render_template, jsonify, request
try:
    from flask_cors import CORS
    _HAS_FLASK_CORS = True
except Exception:
    CORS = None
    _HAS_FLASK_CORS = False
from ai_processor import AIProcessor
import threading
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class WebServer:
    def __init__(self, ai_processor: AIProcessor, host='0.0.0.0', port=5000):
        """
        Initialize the web server with Flask.
        
        Args:
            ai_processor: AIProcessor instance for handling AI responses
            host: Server host (default: localhost)
            port: Server port (default: 5000)
        """
        # Get the base directory (parent of src folder)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_dir = os.path.join(base_dir, 'templates')
        
        self.app = Flask(__name__, template_folder=template_dir)
        # Enable CORS via flask_cors if available, otherwise add a simple after_request fallback
        if _HAS_FLASK_CORS and CORS:
            CORS(self.app)
        else:
            print('[WebServer] flask_cors not available; using simple CORS fallback')
            @self.app.after_request
            def _add_cors_headers(response):
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
                return response
        
        # Robust initialization of AI Processor
        if not isinstance(ai_processor, AIProcessor) and hasattr(ai_processor, 'process'):
             # It might be a duck-typed object, which is fine
             self.ai_processor = ai_processor
        elif isinstance(ai_processor, AIProcessor):
             self.ai_processor = ai_processor
        else:
             print(f"[WebServer] WARNING: Invalid ai_processor provided: {type(ai_processor)}. Creating new instance.")
             # Fallback: create a new instance
             self.ai_processor = AIProcessor()
             
        self.host = host
        self.port = port
        
        print(f"[WebServer] Base dir: {base_dir}")
        print(f"[WebServer] Template dir: {template_dir}")
        print(f"[WebServer] Template exists: {os.path.exists(template_dir)}")
        
        # Set up routes
        self.setup_routes()

    def setup_routes(self):
        """Setup all Flask routes."""
        
        @self.app.errorhandler(404)
        def not_found(error):
            """Handle 404 errors."""
            return jsonify({'error': 'Not found', 'path': request.path}), 404
        
        @self.app.route('/')
        def index():
            """Serve the main visualization page."""
            try:
                return render_template('index.html')
            except Exception as e:
                print(f"[Error] Template error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            """
            API endpoint for chat interaction.
            Receives user input and returns AI response.
            """
            print("[API] /api/chat endpoint called")
            try:
                # Get JSON data from request
                data = request.get_json(force=True, silent=True)
                print(f"[API] Request data: {data}")
                
                if data is None:
                    print("[API] Error: No JSON data received")
                    return jsonify({'success': False, 'error': 'Invalid JSON'}), 400
                
                user_input = data.get('message', '').strip()
                print(f"[API] Received message: {user_input}")
                
                if not user_input:
                    return jsonify({'success': False, 'error': 'Empty message'}), 400
                
                # Process with AI
                print(f"[API] Processing with AI...")
                response = self.ai_processor.process(user_input)
                print(f"[API] AI Response: {response}")
                
                if not response:
                    # Provide an explicit fallback message that the frontend can speak
                    fallback = "Sorry, I can't reach the AI service right now. Please check your API key or quota."
                    print(f"[API] No AI response, returning fallback to client")
                    # Return 200 even on functional error so frontend handles it gracefully
                    return jsonify({
                        'success': False,
                        'error': 'Failed to process message - check API key and connection',
                        'response': fallback,
                        'fallback': fallback,
                        'using_fallback': True
                    })

                return jsonify({
                    'success': True,
                    'response': response,
                    'user_input': user_input
                })
            except Exception as e:
                import traceback
                error_msg = str(e)
                traceback.print_exc()
                print(f"[API] Exception in chat endpoint: {error_msg}")
                # Log to file for debugging
                with open("server_error.log", "a") as f:
                    f.write(f"Error: {error_msg}\n")
                    traceback.print_exc(file=f)
                return jsonify({'success': False, 'error': f'Server error: {error_msg}'}), 500
        
        @self.app.route('/api/test', methods=['GET'])
        def test():
            """Test the AI processor."""
            try:
                print("[TEST] Testing AI processor...")
                response = self.ai_processor.process("Say hello!")
                if response:
                    return jsonify({
                        'success': True,
                        'test': 'passed',
                        'response': response
                    })
                else:
                    return jsonify({
                        'success': False,
                        'test': 'failed',
                        'error': 'No response from AI'
                    }), 500
            except Exception as e:
                return jsonify({
                    'success': False,
                    'test': 'error',
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/reset', methods=['POST'])
        def reset():
            """Reset the conversation history."""
            try:
                self.ai_processor.reset_conversation()
                return jsonify({'success': True, 'message': 'Conversation reset'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/status', methods=['GET'])
        def status():
            """Get assistant status and debug info."""
            import os
            api_key = os.getenv("OPENAI_API_KEY", "NOT SET")
            api_key_display = api_key[:10] + "..." if len(api_key) > 10 else "NOT SET"
            
            # Safe access to conversation history
            try:
                history_len = len(self.ai_processor.conversation_history)
            except AttributeError:
                history_len = 0
            
            return jsonify({
                'status': 'online',
                'model': 'gpt-3.5-turbo',
                'conversation_length': history_len,
                'api_key_configured': api_key != "NOT SET",
                'api_key_preview': api_key_display
            })

    def run(self, debug=False):
        """
        Run the Flask server.
        
        Args:
            debug: Enable debug mode (default: False)
        """
        print(f"\n[WebServer] All registered routes:")
        for rule in self.app.url_map.iter_rules():
            print(f"  {rule.rule} -> {rule.endpoint}")
        
        print(f"\n[WebServer] Web Server Starting at http://localhost:{self.port}")
        print("[WebServer] Open your browser and visit the URL above")
        print("[WebServer] Press Ctrl+C to stop the server\n")
        
        self.app.run(host=self.host, port=self.port, debug=debug, use_reloader=False)

    def run_threaded(self, debug=False):
        """
        Run the Flask server in a background thread.
        
        Args:
            debug: Enable debug mode
            
        Returns:
            Thread object
        """
        thread = threading.Thread(target=self.run, args=(debug,), daemon=True)
        thread.start()
        return thread


if __name__ == '__main__':
    # Allow running this file directly for quick testing
    try:
        load_dotenv()
    except Exception:
        pass

    try:
        ai_proc = AIProcessor()
    except Exception as e:
        print(f"[Main] Warning: could not initialize AIProcessor: {e}")
        ai_proc = AIProcessor(api_key=None)

    server = WebServer(ai_proc, port=5000)
    server.run(debug=True)
