from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

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

        user_message_lower = user_message.lower()
        bot_response_text = ""

        if "hello" in user_message_lower or "hi" in user_message_lower:
            bot_response_text = "Hi there! How can I help you today?"
        elif "how are you" in user_message_lower:
            bot_response_text = "I'm doing well, thank you for asking!"
        elif "bye" in user_message_lower or "goodbye" in user_message_lower:
            bot_response_text = "Goodbye! Have a great day!"
        else:
            bot_response_text = "Sorry, I didn't understand that. Can you rephrase?"
            # Or, to revert to echoing:
            # bot_response_text = user_message

        bot_response = {"reply": bot_response_text}
        return jsonify(bot_response)
    except Exception as e:
        print(f"Error in /chat endpoint: {e}") # Log error for debugging
        return jsonify({"error": "An internal server error occurred"}), 500

if __name__ == '__main__':
    # Note: The user will need to run `pip install Flask Flask-CORS`
    app.run(debug=True, port=5000)
