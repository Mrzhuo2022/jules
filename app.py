import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

# Import AI services
from ai_services.rule_based_service import get_response as get_rule_based_response
from ai_services.custom_api_service import get_response as get_custom_api_response

# Configuration for Custom API - Loaded from environment variables
CUSTOM_API_URL = os.environ.get("CUSTOM_API_URL", None) # Default to None if not set
CUSTOM_API_KEY = os.environ.get("CUSTOM_API_KEY", None) # Default to None if not set
# Convert string "True" or "true" to boolean True, otherwise False
USE_CUSTOM_API = os.environ.get("USE_CUSTOM_API", "False").lower() == "true"

# Flask Configuration - Loaded from environment variables
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() == "true"

# Conversation History Configuration
conversation_histories = {}  # Stores history for different sessions
DEFAULT_SESSION_ID = "global_session"  # Using a single global session for now
MAX_HISTORY_LENGTH = 5  # Max number of user-bot exchanges to keep

app = Flask(__name__, static_folder='static')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        user_message = data.get('message')
        if user_message is None:
            return jsonify({"error": "Missing 'message' key in JSON data"}), 400

        session_id = DEFAULT_SESSION_ID
        current_history = conversation_histories.get(session_id, [])
        history_for_ai = list(current_history) 

        bot_response_text = ""
        if USE_CUSTOM_API:
            if not CUSTOM_API_URL or CUSTOM_API_URL == "YOUR_API_URL_HERE": # Check against placeholder too
                print("Warning: USE_CUSTOM_API is True, but CUSTOM_API_URL is not configured or is a placeholder. Falling back to rule-based.")
                bot_response_text = get_rule_based_response(user_message, history_for_ai)
            else:
                print(f"Using Custom API Service with URL: {CUSTOM_API_URL}")
                bot_response_text = get_custom_api_response(user_message, history_for_ai)
        else:
            print("Using Rule-Based Service")
            bot_response_text = get_rule_based_response(user_message, history_for_ai)

        current_history.append({'user': user_message, 'bot': bot_response_text})
        if len(current_history) > MAX_HISTORY_LENGTH:
            current_history = current_history[-MAX_HISTORY_LENGTH:]
        conversation_histories[session_id] = current_history

        bot_response = {"reply": bot_response_text}
        return jsonify(bot_response)
    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500

if __name__ == '__main__':
    # Note: The user will need to run `pip install Flask Flask-CORS requests python-dotenv`
    # `python-dotenv` is for loading .env files.
    # `requests` is needed for the custom_api_service.
    app.run(debug=FLASK_DEBUG, port=5000)
