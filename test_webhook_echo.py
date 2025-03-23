#!/usr/bin/env python3
import os
import json
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# Orkes Conductor configuration
CONDUCTOR_AUTH_KEY = os.getenv("CONDUCTOR_AUTH_KEY", "zxvp2aa7baf2-076d-11f0-9d9d-065ebd459714")
CONDUCTOR_AUTH_SECRET = os.getenv("CONDUCTOR_AUTH_SECRET", "kyORq2J20gc9E3tLUiabEBdBWWpNkD2Db00FwoZMg1LUXKrw")
WEBHOOK_URL = "https://developer.orkescloud.com/webhook/zxvp050b08aa-0772-11f0-9d9d-05e8bd459714"

# Local server configuration
LOCAL_HOST = "localhost"
LOCAL_PORT = 8080
CALLBACK_URL = f"http://{LOCAL_HOST}:{LOCAL_PORT}/webhook-response"

class ResponseHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests from Orkes Conductor"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        print("\n=== Received Response from Workflow ===")
        try:
            response_data = json.loads(post_data.decode('utf-8'))
            print(json.dumps(response_data, indent=2))
        except:
            print(post_data.decode('utf-8'))
        
        # Send response back to Orkes
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "received"}).encode())

def start_server():
    """Start local HTTP server"""
    server = HTTPServer((LOCAL_HOST, LOCAL_PORT), ResponseHandler)
    print(f"\nStarting server at http://{LOCAL_HOST}:{LOCAL_PORT}")
    server.serve_forever()

def send_test_webhook():
    """Send test webhook to Orkes Conductor"""
    headers = {
        "Content-Type": "application/json",
        "x-conductor-auth-key": CONDUCTOR_AUTH_KEY,
        "x-conductor-auth-secret": CONDUCTOR_AUTH_SECRET
    }
    
    # Test payload
    payload = {
        "callback_url": CALLBACK_URL,
        "data": {
            "message": "Test webhook trigger",
            "timestamp": datetime.utcnow().isoformat(),
            "test_id": "echo_test_1",
            "values": {
                "metric1": 100,
                "metric2": 200
            }
        }
    }

    print("\n=== Sending Webhook to Orkes Conductor ===")
    print(json.dumps(payload, indent=2))

    try:
        response = requests.post(
            WEBHOOK_URL,
            headers=headers,
            json=payload
        )
        
        print(f"\nWebhook Response Status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"\nError sending webhook: {str(e)}")
        return False

def main():
    print("Starting Orkes Conductor webhook echo test...")
    
    # Start local server in a separate thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    try:
        # Send test webhook
        send_test_webhook()
        
        # Keep main thread running to receive response
        print("\nWaiting for workflow response... (Press Ctrl+C to exit)")
        server_thread.join()
        
    except KeyboardInterrupt:
        print("\nTest completed. Shutting down...")

if __name__ == "__main__":
    main()
