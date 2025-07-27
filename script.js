document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const chatMessages = document.getElementById('chatMessages');
    const clearButton = document.getElementById('clearChat');

    // Handle clear chat
    clearButton.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear the chat history?')) {
            // Keep only the initial greeting message
            const initialMessage = chatMessages.firstElementChild;
            chatMessages.innerHTML = '';
            chatMessages.appendChild(initialMessage);
        }
    });

    // Add sound effect for messages
    const messageSound = new Audio('data:audio/wav;base64,UklGRl4JAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YToJAAB4eHh3eX19fHx9fX18e3p5eHZ1dHNwb3BvcG9wcXFxc3Jzc3R0dHR1dHRzcnBvbm1sa2tqaWlpamtsb');
    messageSound.volume = 0.2;

    // Format timestamp
    const formatTimestamp = () => {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    // Create typing indicator
    const createTypingIndicator = () => {
        const typing = document.createElement('div');
        typing.className = 'message bot typing';
        typing.innerHTML = `
            <div class="message-content">
                <div class="typing">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        return typing;
    };

    // Add message to chat (supports markdown)
    const addMessage = (message, isUser = false) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;

        const content = document.createElement('div');
        content.className = 'message-content';
        // Render markdown/code blocks for bot messages
        if (!isUser) {
            content.innerHTML = renderMarkdown(message);
        } else {
            content.textContent = message;
        }

        const timestamp = document.createElement('div');
        timestamp.className = 'timestamp';
        timestamp.textContent = formatTimestamp();

        messageDiv.appendChild(content);
        messageDiv.appendChild(timestamp);

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    // Simple markdown/code block renderer
    function renderMarkdown(text) {
        // Code block
        text = text.replace(/```([\w]*)\n([\s\S]*?)```/g, (match, lang, code) => {
            return `<pre class="code-block"><code>${escapeHtml(code)}</code></pre>`;
        });
        // Inline code
        text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
        // Bold
        text = text.replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>');
        // Italic
        text = text.replace(/\*([^*]+)\*/g, '<i>$1</i>');
        // Line breaks
        text = text.replace(/\n/g, '<br>');
        return text;
    }
    function escapeHtml(text) {
        return text.replace(/[&<>]/g, tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[tag]));
    }

    // Handle form submission
    // Conversation history for context
    let conversationHistory = [];

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const message = userInput.value.trim();
        if (!message) return;

        // Add user message to chat
        addMessage(message, true);
        userInput.value = '';

        // Add to history
        let lastBot = conversationHistory.length > 0 ? conversationHistory[conversationHistory.length - 1].bot : '';
        conversationHistory.push({ user: message, bot: lastBot });

        try {
            // Show typing indicator
            const typingIndicator = createTypingIndicator();
            chatMessages.appendChild(typingIndicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            // Send message to backend with history
            const backendURL = window.location.hostname === 'localhost'
                ? 'http://localhost:5000/api/chat'
                : '/api/chat';
            const response = await fetch(backendURL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message, history: conversationHistory.slice(-10) })
            });

            // Remove typing indicator
            chatMessages.removeChild(typingIndicator);

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            messageSound.play();

            // Typing effect for bot response
            await typeBotMessage(data.response);

            // Add to history
            conversationHistory[conversationHistory.length - 1].bot = data.response;

        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, I encountered an error. Please try again.');
        }
    });

    // Typing effect for bot message
    async function typeBotMessage(fullMessage) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        const content = document.createElement('div');
        content.className = 'message-content';
        messageDiv.appendChild(content);
        const timestamp = document.createElement('div');
        timestamp.className = 'timestamp';
        timestamp.textContent = formatTimestamp();
        messageDiv.appendChild(timestamp);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Typing animation (character by character)
        let i = 0;
        while (i <= fullMessage.length) {
            content.innerHTML = renderMarkdown(fullMessage.slice(0, i));
            chatMessages.scrollTop = chatMessages.scrollHeight;
            await new Promise(res => setTimeout(res, 10 + Math.random() * 30));
            i++;
        }
    }

    // Focus input on load
    userInput.focus();

    // Handle Enter key
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
});
