document.addEventListener('DOMContentLoaded', () => {
    const chatDisplay = document.getElementById('chat-display');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const loadingIndicator = document.getElementById('loading-indicator');

    /**
     * Displays a message in the chat display.
     * @param {string} messageText - The text of the message.
     * @param {string} sender - The sender of the message ('user' or 'bot').
     * @param {HTMLElement} [elementToReplace=null] - Optional. If provided, this element will be replaced.
     */
    function displayMessage(messageText, sender, elementToReplace = null) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message-bubble');
        if (sender === 'user') {
            messageElement.classList.add('user-message');
        } else {
            messageElement.classList.add('bot-message');
        }
        messageElement.textContent = messageText;

        if (elementToReplace) {
            chatDisplay.replaceChild(messageElement, elementToReplace);
        } else {
            // If loading indicator is visible, insert message before it, otherwise append
            if (loadingIndicator.style.display !== 'none' && chatDisplay.contains(loadingIndicator)) {
                 chatDisplay.insertBefore(messageElement, loadingIndicator);
            } else {
                chatDisplay.appendChild(messageElement);
            }
        }
        
        // Scroll to the bottom
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }

    /**
     * Shows or hides the loading indicator and manages input field/button state.
     * @param {boolean} show - True to show loading, false to hide.
     */
    function setLoadingState(show) {
        if (show) {
            loadingIndicator.style.display = 'block'; // Or 'flex' if using flex for styling
            userInput.disabled = true;
            sendButton.disabled = true;
            chatDisplay.scrollTop = chatDisplay.scrollHeight; // Scroll to show loading indicator
        } else {
            loadingIndicator.style.display = 'none';
            userInput.disabled = false;
            sendButton.disabled = false;
            userInput.focus(); // Set focus back to input field
        }
    }

    /**
     * Sends a message to the backend server and displays the bot's response.
     * @param {string} messageText - The message to send.
     */
    function sendMessageToServer(messageText) {
        setLoadingState(true);

        fetch('http://127.0.0.1:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: messageText }),
        })
        .then(response => {
            if (!response.ok) {
                // Attempt to parse error response for more details if available
                return response.json().catch(() => {
                    // If response is not JSON or parsing fails, throw a generic error
                    throw new Error(`HTTP error! status: ${response.status}`);
                }).then(errorData => {
                    // If errorData has a specific message, include it
                    const errorMessage = errorData && errorData.error ? errorData.error : `HTTP error! status: ${response.status}`;
                    throw new Error(errorMessage);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.reply) {
                displayMessage(data.reply, 'bot');
            } else {
                console.error('Bot response did not contain a reply:', data);
                displayMessage('Error: Bot response format incorrect.', 'bot');
            }
        })
        .catch(error => {
            console.error('Error sending message to server:', error);
            displayMessage(`Sorry, an error occurred: ${error.message}`, 'bot');
        })
        .finally(() => {
            setLoadingState(false);
        });
    }

    /**
     * Handles sending a message from the user input.
     */
    function handleSendMessage() {
        const messageText = userInput.value.trim();
        if (messageText === '' || userInput.disabled) { // Prevent sending if input is disabled
            return;
        }
        
        displayMessage(messageText, 'user');
        sendMessageToServer(messageText);
        userInput.value = ''; // Clear input field
    }

    // Event Listeners
    sendButton.addEventListener('click', handleSendMessage);

    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            handleSendMessage();
        }
    });
});
