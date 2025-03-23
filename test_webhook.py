#!/usr/bin/env python3
import os
import time
import json
import requests
from datetime import datetime

# Orkes Conductor configuration
CONDUCTOR_AUTH_KEY = os.getenv("CONDUCTOR_AUTH_KEY", "zxvp2aa7baf2-076d-11f0-9d9d-065ebd459714")
CONDUCTOR_AUTH_SECRET = os.getenv("CONDUCTOR_AUTH_SECRET", "kyORq2J20gc9E3tLUiabEBdBWWpNkD2Db00FwoZMg1LUXKrw")
WEBHOOK_URL = "https://developer.orkescloud.com/webhook/zxvp050b08aa-0772-11f0-9d9d-05e8bd459714"

def send_test_webhook():
    """Send a test webhook to Orkes Conductor"""
    headers = {
        "Content-Type": "application/json",
        "x-conductor-auth-key": CONDUCTOR_AUTH_KEY,
        "x-conductor-auth-secret": CONDUCTOR_AUTH_SECRET
    }
    
    # Test payload
    payload = {
        "metric": "test_metric",
        "value": 100,
        "timestamp": datetime.utcnow().isoformat(),
        "test_id": "webhook_test_1"
    }

    try:
        print("Sending webhook notification...")
        response = requests.post(
            WEBHOOK_URL,
            headers=headers,
            json=payload
        )
        
        print(f"\nWebhook Response Status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            print("\nWebhook test successful!")
        else:
            print(f"\nWebhook test failed with status code: {response.status_code}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"\nError sending webhook: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting Orkes Conductor webhook test...")
    send_test_webhook()
