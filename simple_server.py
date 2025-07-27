from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from datetime import datetime
import random
from urllib.parse import parse_qs, urlparse
import os

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

class ChatbotHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            user_message = data.get('message', '').lower()

            # Process message and get response
            response = self.get_response(user_message)

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'response': response,
                'status': 'success'
            }).encode())
        else:
            super().do_POST()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def get_response(self, message):
        hour = datetime.now().hour
        
        # Handle greetings
        if any(word in message for word in ['hello', 'hi', 'hey']):
            if 5 <= hour < 12:
                prefix = "Good morning! "
            elif 12 <= hour < 17:
                prefix = "Good afternoon! "
            elif 17 <= hour < 22:
                prefix = "Good evening! "
            else:
                prefix = "Hello! "
            return prefix + random.choice(responses['greeting'])
            
        # Handle goodbyes
        if any(word in message for word in ['bye', 'goodbye', 'see you']):
            return random.choice(responses['goodbye'])
            
        # Handle thanks
        if any(word in message for word in ['thanks', 'thank you']):
            return random.choice(responses['thanks'])
            
        # Default response
        return random.choice(responses['default'])

def run_server():
    print("Starting server at http://localhost:5000")
    httpd = HTTPServer(('localhost', 5000), ChatbotHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run_server()
