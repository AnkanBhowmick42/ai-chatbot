from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import random
from datetime import datetime

# Simple response dictionary
responses = {
    'greeting': [
        "Hello! How can I help you today?",
        "Hi there! What can I do for you?",
        "Greetings! How may I assist you?"
    ],
    'goodbye': [
        "Goodbye! Have a great day!",
        "See you later!",
        "Take care! Come back soon!"
    ],
    'thanks': [
        "You're welcome!",
        "Glad I could help!",
        "My pleasure!"
    ],
    'default': [
        "I'm not sure I understand. Could you rephrase that?",
        "Interesting! Tell me more about that.",
        "I'm still learning. Could you explain differently?"
    ]
}
import nltk
import logging
import os
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('wordnet')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Create and train the ChatterBot instance
chatbot = ChatBot(
    'WebAssistant',
    logic_adapters=[
        'chatterbot.logic.BestMatch',
        'chatterbot.logic.MathematicalEvaluation',
        'chatterbot.logic.TimeLogicAdapter'
    ],
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///database.sqlite3'
)

corpus_trainer = ChatterBotCorpusTrainer(chatbot)
corpus_trainer.train(
    "chatterbot.corpus.english.greetings",
    "chatterbot.corpus.english.conversations",
    "chatterbot.corpus.english.emotions",
    "chatterbot.corpus.english.ai"
)

# Custom training data
custom_conversations = [
    [
        "What can you help me with?",
        "I can help you with general conversations, answer questions, and provide information on various topics."
    ],
    [
        "Tell me about yourself",
        "I'm an AI chatbot created using Python, ChatterBot, and NLTK. I'm designed to learn from conversations and provide helpful responses."
    ],
    [
        "How do you learn?",
        "I learn through training data and conversations. Each interaction helps me improve my responses."
    ]
]
list_trainer = ListTrainer(chatbot)
for conversation in custom_conversations:
    list_trainer.train(conversation)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').lower()
        history = data.get('history', [])  # List of previous messages
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Use history to make the bot more context-aware (simple example)
        context = "\n".join([f"User: {msg['user']}\nBot: {msg['bot']}" for msg in history if 'user' in msg and 'bot' in msg])
        
        # Get response based on message content
        response = None
        hour = datetime.now().hour
        
        # Example: If user says 'code' or 'python', return markdown code block
        if 'code' in user_message or 'python' in user_message:
            response = ("Here's a Python example:\n\n" +
                        '```python\n' +
                        'def hello():\n    print("Hello, world!")\n' +
                        '```')
        # Use ChatterBot for general queries
        else:
            try:
                response = str(chatbot.get_response(user_message))
            except Exception as e:
                logger.error(f"ChatterBot error: {str(e)}")
                response = None
        # Use context for a more interactive feel
        if 'previous' in user_message or 'context' in user_message:
            response = f"Here's what we've talked about so far:\n\n{context if context else 'No previous conversation.'}"
        # Default response
        if not response or response.strip() == '' or response.lower() in [r.lower() for r in responses['default']]:
            response = random.choice(responses['default'])
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    # Use environment variables for production settings
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    host = os.environ.get('HOST', '0.0.0.0')  # Accept connections from all IPs
    
    app.run(host=host, port=port, debug=debug)
