# ai_services/custom_api_service.py
import requests
import os # For potentially getting API details from environment variables in the future

# Import configuration from app.py.
# This creates a slight coupling but is simpler for this example.
# A more advanced setup might use a dedicated config module or Flask's app.config.
try:
    from app import CUSTOM_API_URL, CUSTOM_API_KEY
except ImportError:
    # Fallback if running this module directly or app is not in PYTHONPATH
    # In a real application, manage configurations more robustly.
    CUSTOM_API_URL = os.environ.get("CUSTOM_API_URL", "YOUR_API_URL_HERE_FALLBACK")
    CUSTOM_API_KEY = os.environ.get("CUSTOM_API_KEY", "YOUR_API_KEY_HERE_FALLBACK")

def get_response(user_message: str) -> str:
    """
    Processes the user's message by calling a custom external API
    and returns the AI's response.

    Args:
        user_message: The message string from the user.

    Returns:
        A string containing the AI's response from the custom API,
        or a fallback message if an error occurs.
    """
    if not CUSTOM_API_URL or CUSTOM_API_URL == "YOUR_API_URL_HERE":
        return "Error: Custom API URL is not configured."

    headers = {
        "Content-Type": "application/json",
    }
    if CUSTOM_API_KEY and CUSTOM_API_KEY != "YOUR_API_KEY_HERE":
        # Assuming Bearer token authentication as a common example
        headers["Authorization"] = f"Bearer {CUSTOM_API_KEY}"
        # Alternatively, for X-API-Key:
        # headers["X-API-Key"] = CUSTOM_API_KEY

    # Assuming the API expects a JSON payload with a "query" field
    payload = {"query": user_message}

    try:
        response = requests.post(CUSTOM_API_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        # Assuming the API returns JSON with an "answer" field
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
    # Example usage (for testing this module directly)
    # You would need to set CUSTOM_API_URL and potentially CUSTOM_API_KEY
    # or ensure app.py is in PYTHONPATH for the import to work.
    
    # For testing with a mock API:
    # CUSTOM_API_URL = "https://jsonplaceholder.typicode.com/posts" # This API expects a different payload and returns different JSON
    # CUSTOM_API_KEY = ""
    
    # Test case for jsonplaceholder (it doesn't use "query" or return "answer" directly)
    # If CUSTOM_API_URL is jsonplaceholder, the current payload/response parsing will "fail" gracefully.
    # To test jsonplaceholder properly, you'd adjust payload and response parsing:
    # payload = {"title": "foo", "body": "bar", "userId": 1}
    # then in response handling: bot_reply = api_response_json.get("title") + " " + str(api_response_json.get("id"))

    # print(get_response("Tell me a joke about APIs."))
    
    # Example with a hypothetical correct API:
    if CUSTOM_API_URL != "YOUR_API_URL_HERE_FALLBACK" and CUSTOM_API_URL != "YOUR_API_URL_HERE":
        print(f"Testing with CUSTOM_API_URL: {CUSTOM_API_URL}")
        test_message = "Hello from custom_api_service test!"
        print(f"Sending: {test_message}")
        print(f"Received: {get_response(test_message)}")
    else:
        print("Please configure CUSTOM_API_URL in this file (or via app.py/environment) to test.")

    # Note: To run this test, you'll need to install requests: pip install requests
