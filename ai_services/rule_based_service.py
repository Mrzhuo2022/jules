# ai_services/rule_based_service.py

def get_response(user_message: str, history: list) -> str:
    """
    Processes the user's message based on a predefined set of rules
    and returns the AI's response.

    Args:
        user_message: The current message string from the user.
        history: A list of previous message exchanges (currently not used by this service).
                 Each element is a dictionary e.g., {'user': 'message', 'bot': 'reply'}.


    Returns:
        A string containing the AI's response.
    """
    # The history argument is ignored in this simple rule-based service for now.
    # It's included to match the common AI service interface.
    _ = history # Mark as unused

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
    
    return bot_response_text
