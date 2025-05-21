document.addEventListener('DOMContentLoaded', () => {
    const chatDisplay = document.getElementById('chat-display');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    /**
     * Displays a message in the chat display.
     * @param {string} messageText - The text of the message.
     * @param {string} sender - The sender of the message ('user' or 'bot').
     */
    function displayMessage(messageText, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message-bubble');
        if (sender === 'user') {
            messageElement.classList.add('user-message');
        } else {
            messageElement.classList.add('bot-message');
        }
        messageElement.textContent = messageText;
        chatDisplay.appendChild(messageElement);

        // Scroll to the bottom
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }

    /**
     * Sends a message to the backend server and displays the bot's response.
     * @param {string} messageText - The message to send.
     */
    function sendMessageToServer(messageText) {
        fetch('http://127.0.0.1:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: messageText }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
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
            // Display a user-friendly error message in the chat
            displayMessage('Sorry, I couldn\'t connect to the bot. Please try again later.', 'bot');
        });
    }

    /**
     * Handles sending a message from the user input.
     */
    function handleSendMessage() {
        const messageText = userInput.value.trim();
        if (messageText !== '') {
            displayMessage(messageText, 'user'); // Display user's message immediately
            sendMessageToServer(messageText);    // Send to server and let it handle bot's response
            userInput.value = '';                // Clear input field
        }
    }

    // Event Listeners
    sendButton.addEventListener('click', handleSendMessage);

    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            handleSendMessage();
        }
    });

    // Optional: Initial message from bot or instructions
    // displayMessage("Hello! Type your message and press Enter or click Send.", 'bot');
});
