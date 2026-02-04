"""
Backend Server for College Chatbot
Handles API requests from the frontend
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from app.services.agent_mcp import SimplifiedMCPAgent
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global agent instance
agent = None

def get_agent():
    global agent
    if agent is None:
        try:
            print("Initializing Chatbot Agent...")
            agent = SimplifiedMCPAgent()
            print("Chatbot agent initialized successfully")
        except Exception as e:
            print(f"Error initializing chatbot agent: {str(e)}")
    return agent

@app.route('/query', methods=['POST'])
def query():
    """Handle chat queries"""
    try:
        data = request.json
        logger.info(f"Received query: {data.get('message', '')[:50]}...")
        message = data.get('message')
        session_id = data.get('session_id')
        language = data.get('language', 'en')
        
        if not message:
            return jsonify({'error': 'Message required'}), 400
            
        chatbot = get_agent()
        if not chatbot:
             return jsonify({'error': 'Chatbot system not initialized'}), 500
             
        # Process query
        # TODO: Pass session_id and language if supported by agent in future
        answer = chatbot(message)
        
        return jsonify({
            'answer': answer,
            'session_id': session_id or 'new_session' 
        })
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'college-chatbot-backend'})

if __name__ == '__main__':
    print("=" * 70)
    print("TKRCET Chatbot Backend Server")
    print("=" * 70)
    print("\nStarting server...")
    print("API Endpoint: http://localhost:8000/query")
    print("\nPress Ctrl+C to stop")
    print("=" * 70)
    
    # Run on port 8000 (debug=False for stability)
    try:
        app.run(debug=False, host='0.0.0.0', port=8000)
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Press Enter to close...")
