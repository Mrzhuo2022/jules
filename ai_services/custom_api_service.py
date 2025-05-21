# ai_services/custom_api_service.py
import requests
import os

try:
    from app import CUSTOM_API_URL, CUSTOM_API_KEY
except ImportError:
    CUSTOM_API_URL = os.environ.get("CUSTOM_API_URL", "YOUR_API_URL_HERE_FALLBACK")
    CUSTOM_API_KEY = os.environ.get("CUSTOM_API_KEY", "YOUR_API_KEY_HERE_FALLBACK")

def get_response(user_message: str, history: list) -> str:
    """
    Processes the user's message by calling a custom external API,
    including conversation history, and returns the AI's response.

    Args:
        user_message: The current message string from the user.
        history: A list of previous message exchanges.
                 Each element is a dictionary e.g., {'user': 'message', 'bot': 'reply'}.

    Returns:
        A string containing the AI's response from the custom API,
        or a fallback message if an error occurs.
    """
    if not CUSTOM_API_URL or CUSTOM_API_URL == "YOUR_API_URL_HERE" or CUSTOM_API_URL == "YOUR_API_URL_HERE_FALLBACK":
        return "Error: Custom API URL is not configured."

    headers = {
        "Content-Type": "application/json",
    }
    if CUSTOM_API_KEY and CUSTOM_API_KEY != "YOUR_API_KEY_HERE" and CUSTOM_API_KEY != "YOUR_API_KEY_HERE_FALLBACK":
        headers["Authorization"] = f"Bearer {CUSTOM_API_KEY}"

    # Adapt history to the format [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    formatted_history = []
    for exchange in history:
        if exchange.get('user'):
            formatted_history.append({"role": "user", "content": exchange['user']})
        if exchange.get('bot'):
            formatted_history.append({"role": "assistant", "content": exchange['bot']})
    
    # The payload structure depends on the custom API.
    # Common patterns include sending history as a list of messages.
    # Here, we send the current message as "query" and history separately.
    # Some APIs might prefer the current message to be the last item in the history list.
    payload = {
        "query": user_message,
        "history": formatted_history 
    }
    # Alternative payload if API expects current message within history:
    # formatted_history.append({"role": "user", "content": user_message})
    # payload = {"messages": formatted_history}


    try:
        response = requests.post(CUSTOM_API_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        api_response_json = response.json()
        bot_reply = api_response_json.get("answer")

        if bot_reply:
            return bot_reply
        else:
            print(f"Custom API response did not contain 'answer' field. Response: {api_response_json}")
            return "Sorry, I received an unexpected response from the AI service."

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - {response.status_code} - {response.text}")
        return f"Sorry, there was an issue with the AI service (HTTP {response.status_code})."
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        return "Sorry, I couldn't connect to the external AI service."
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        return "Sorry, the request to the AI service timed out."
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred during the API request: {req_err}")
        return "Sorry, an unexpected error occurred while contacting the AI service."
    except ValueError as json_err: # Includes JSONDecodeError
        print(f"Error parsing JSON response from custom API: {json_err}")
        return "Sorry, I received an invalid response from the AI service."

if __name__ == '__main__':
    if CUSTOM_API_URL != "YOUR_API_URL_HERE_FALLBACK" and CUSTOM_API_URL != "YOUR_API_URL_HERE":
        print(f"Testing with CUSTOM_API_URL: {CUSTOM_API_URL}")
        test_message = "What was the first thing I said?"
        test_history = [
            {"user": "My name is Bob.", "bot": "Nice to meet you, Bob!"},
            {"user": "What is my name?", "bot": "Your name is Bob."}
        ]
        print(f"Sending: {test_message} with history: {test_history}")
        print(f"Received: {get_response(test_message, test_history)}")
    else:
        print("Please configure CUSTOM_API_URL in this file (or via app.py/environment) to test.")
