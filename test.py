import requests
import json

WEBHOOK_URL = "https://developer.orkescloud.com/webhook/zxvp050b08aa-0772-11f0-9d9d-05e8bd459714"
HEADERS = {
    "Content-Type": "application/json",
    "key": "val"  # Replace with your actual header key/value
}

payload = {
    "message": "Triggering ICS_Malware workflow",
    "metadata": {
        "source": "custom-platform"
    }
}

response = requests.post(WEBHOOK_URL, headers=HEADERS, data=json.dumps(payload))

if response.status_code == 200:
    print("Webhook called successfully!")
    print("Response:", response.text)
else:
    print(f"Error calling webhook: {response.status_code}")
    print("Response:", response.text)
