from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import time
import logging
from dotenv import load_dotenv

# Initialize
load_dotenv()
app = Flask(__name__)
CORS(app)

# Configuration
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "mistral")
TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced prompt template
TRAVEL_PROMPT = """[INST] <<SYS>>
You are TravelMate, a friendly travel assistant. Respond to greetings naturally, 
and for travel requests provide:
1. 1-3 location suggestions
2. Each as a bullet point with:
   - **Place**: Brief highlight
   - Best for: [type of travelers]
   - When: [best season]
<</SYS>>

{user_input} [/INST]"""

def check_ollama():
    """Verify Ollama is running"""
    try:
        res = requests.get("http://localhost:11434/", timeout=5)
        return res.status_code == 200
    except Exception as e:
        logger.error(f"Ollama check failed: {e}")
        return False

def generate_response(user_input: str) -> str:
    """Get response from Ollama with enhanced error handling"""
    try:
        # Handle greetings separately
        if user_input.lower().strip() in ("hi", "hello", "hey"):
            return "Hello! I'm TravelMate. Where would you like to go today?"

        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": MODEL_NAME,
                "prompt": TRAVEL_PROMPT.format(user_input=user_input),
                "stream": False,
                "options": {
                    "temperature": 0.5,
                    "num_predict": 150,
                    "top_p": 0.9
                }
            },
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        
        logger.error(f"Ollama API error: {response.status_code} - {response.text}")
    except requests.exceptions.Timeout:
        logger.error("Ollama timeout - Model may not be loaded")
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
    
    return None

@app.route('/api/chat', methods=['POST'])
def chat():
    if not check_ollama():
        return jsonify({
            "response": "Our travel service is currently unavailable. Please try again later.",
            "success": False
        }), 503

    try:
        data = request.get_json()
        user_input = data.get("message", "").strip()
        
        if not user_input:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        logger.info(f"Processing: '{user_input}'")
        
        bot_response = generate_response(user_input)
        
        if not bot_response:
            return jsonify({
                "response": "I'm having trouble generating a response. Please try again.",
                "success": False
            }), 500
            
        return jsonify({
            "response": bot_response,
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        return jsonify({
            "response": "An unexpected error occurred.",
            "success": False
        }), 500

if __name__ == '__main__':
    logger.info(f"Starting server with model: {MODEL_NAME}")
    app.run(host='0.0.0.0', port=5000, debug=False)  # debug=False for production