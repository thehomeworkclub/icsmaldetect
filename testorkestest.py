#!/usr/bin/env python3
import requests
import json

# Replace with the actual webhook URL from Orkes Cloud
WEBHOOK_URL = "https://developer.orkescloud.com/webhook/zxvp050b08aa-0772-11f0-9d9d-065ebd459714"

# The headers must match what you configured in Conductor.
headers = {
    "Content-Type": "application/json",
    "key": "val"   # The custom header you set in the Webhook config
}

# The JSON payload you want to pass as workflow input
payload = {
    "testParam": "Testing HTTP Task",
    "timestamp": "2024-03-22T17:47:59"  # Using current time as reference
}

# Make the POST request to trigger the workflow
resp = requests.post(WEBHOOK_URL, headers=headers, json=payload)

print("Status code:", resp.status_code)
print("Response body:", resp.text)

# Sleep for a moment to let the workflow execute
import time
time.sleep(2)

# You can add workflow status checking here if you have access to the Orkes API
# This would require additional authentication and the workflow ID
print("\nNote: The workflow should have made a GET request to https://orkes-api-tester.orkesconductor.com/api")
print("You can check the workflow execution in your Orkes Cloud dashboard to see the HTTP task results")
