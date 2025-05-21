from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
# Import AI services
from ai_services.rule_based_service import get_response as get_rule_based_response
from ai_services.custom_api_service import get_response as get_custom_api_response

# Configuration for Custom API
# IMPORTANT: Do NOT commit real API keys. These are placeholders.
# Users should set these via environment variables or a dedicated config file in a real application.
CUSTOM_API_URL = "YOUR_API_URL_HERE"  # e.g., https://api.example.com/chat
CUSTOM_API_KEY = "YOUR_API_KEY_HERE"  # Can be empty if not needed by the API
USE_CUSTOM_API = False  # Switch to True to use the custom API service

# For testing with a mock API (like jsonplaceholder):
# CUSTOM_API_URL = "https://jsonplaceholder.typicode.com/posts" 
# CUSTOM_API_KEY = "" # No key needed for jsonplaceholder
# USE_CUSTOM_API = True # Set to True to test, then False

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Route to serve index.html from the root directory
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
        if user_message is None: # Check if 'message' key exists
            return jsonify({"error": "Missing 'message' key in JSON data"}), 400

        bot_response_text = ""
        if USE_CUSTOM_API:
            # Ensure the URL is not the placeholder if USE_CUSTOM_API is True
            if CUSTOM_API_URL == "YOUR_API_URL_HERE" or not CUSTOM_API_URL:
                print("Warning: USE_CUSTOM_API is True, but CUSTOM_API_URL is not configured. Falling back to rule-based.")
                bot_response_text = get_rule_based_response(user_message)
            else:
                print(f"Using Custom API Service with URL: {CUSTOM_API_URL}")
                bot_response_text = get_custom_api_response(user_message)
        else:
            print("Using Rule-Based Service")
            bot_response_text = get_rule_based_response(user_message)

        bot_response = {"reply": bot_response_text}
        return jsonify(bot_response)
    except Exception as e:
        print(f"Error in /chat endpoint: {e}") # Log error for debugging
        return jsonify({"error": "An internal server error occurred"}), 500

if __name__ == '__main__':
    # Note: The user will need to run `pip install Flask Flask-CORS requests`
    # The 'requests' library is needed for the custom_api_service.
    
    # --- Conceptual Test with Mock API ---
    # To test the custom API integration:
    # 1. Uncomment the mock API settings above (CUSTOM_API_URL for jsonplaceholder, USE_CUSTOM_API = True).
    # 2. Run `python app.py`.
    # 3. Send a message from the chat interface.
    # 4. The custom_api_service.py will attempt to POST to jsonplaceholder.
    #    Since jsonplaceholder doesn't expect {"query": ...} and doesn't return {"answer": ...},
    #    the custom_api_service will likely return one of its error/fallback messages.
    #    This tests the wiring and error handling.
    # 5. Remember to revert the mock API settings in app.py before committing.
    # --- End Conceptual Test ---

    app.run(debug=True, port=5000)
