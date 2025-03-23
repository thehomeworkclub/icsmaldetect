#!/usr/bin/env python3
import time
import json
import requests

# --- Hardcoded API Credentials and Server URL ---
CONDUCTOR_AUTH_KEY = "zxvp2aa7baf2-076d-11f0-9d9d-065ebd459714"
CONDUCTOR_AUTH_SECRET = "kyORq2J20gc9E3tLUiabEBdBWWpNkD2Db00FwoZMg1LUXKrw"
CONDUCTOR_SERVER_URL = "https://developer.orkescloud.com/api"

# --- Function to Obtain an Auth Token ---
def get_auth_token():
    auth_url = f"{CONDUCTOR_SERVER_URL}/token"
    # Note: The token endpoint expects the credentials as "keyId" and "keySecret"
    payload = {
        "keyId": CONDUCTOR_AUTH_KEY,
        "keySecret": CONDUCTOR_AUTH_SECRET
    }
    print("Requesting authentication token...")
    response = requests.post(auth_url, json=payload)
    if response.status_code == 200:
        token = response.json().get("token")
        if token:
            print("Token obtained successfully.")
            return token
        else:
            print("Token not found in response:", response.json())
    else:
        print("Error obtaining token:", response.status_code)
        print("Response:", response.text)
    return None

# Global headers for subsequent API calls (token will be added after authentication)
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# --- Webhook Configuration ---
WEBHOOK_URL = "https://developer.orkescloud.com/webhook/zxvp050b08aa-0772-11f0-9d9d-05e8bd459714"
WEBHOOK_HEADERS = {
    "Content-Type": "application/json",
    "key": "val"  # Replace with your actual header key/value if needed
}

# --- Workflow JSON Definition ---
workflow_definition = {
    "createTime": 1742684561348,
    "updateTime": 1742684958761,
    "name": "ics_malware",
    "description": "Malware detection and alerting using anomaly detection in ICS's",
    "version": 1,
    "tasks": [
        {
            "name": "wait_for_webhook",
            "taskReferenceName": "waitWebhook",
            "type": "WAIT"
        },
        {
            "name": "process_webhook_response",
            "taskReferenceName": "processResponse",
            "type": "SIMPLE",
            "inputParameters": {
                "message": "Webhook received and processed successfully"
            }
        }
    ],
    "inputParameters": [],
    "outputParameters": {
        "responseMessage": "${processResponse.output.message}"
    },
    "failureWorkflow": "",
    "schemaVersion": 2,
    "restartable": True,
    "workflowStatusListenerEnabled": False,
    "ownerEmail": "sebastianralexis@gmail.com",
    "timeoutPolicy": "ALERT_ONLY",
    "timeoutSeconds": 0,
    "variables": {},
    "inputTemplate": {},
    "enforceSchema": True
}

# --- Functions for Workflow Integration ---

def register_workflow():
    url = f"{CONDUCTOR_SERVER_URL}/metadata/workflow"
    print("Registering workflow definition...")
    response = requests.post(url, headers=headers, data=json.dumps(workflow_definition))
    if response.status_code in (200, 204):
        print("Workflow registered successfully!")
    else:
        print(f"Error registering workflow: {response.status_code}")
        print("Response:", response.text)

def start_workflow():
    url = f"{CONDUCTOR_SERVER_URL}/workflow/ics_malware"
    print("Starting workflow instance...")
    response = requests.post(url, headers=headers, data=json.dumps({}))
    if response.status_code == 200:
        workflow_id = response.json().get("workflowId")
        print("Workflow started successfully!")
        print("Workflow ID:", workflow_id)
        return workflow_id
    else:
        print(f"Error starting workflow: {response.status_code}")
        print("Response:", response.text)
    return None

def send_webhook():
    payload = {
        "message": "Triggering ICS_Malware workflow",
        "metadata": {
            "source": "custom-platform"
        }
    }
    print("Sending webhook call...")
    response = requests.post(WEBHOOK_URL, headers=WEBHOOK_HEADERS, data=json.dumps(payload))
    if response.status_code == 200:
        print("Webhook called successfully!")
        print("Response from webhook:", response.text)
        send_callback(response.text)
    else:
        print(f"Error calling webhook: {response.status_code}")
        print("Response:", response.text)

def send_callback(previous_response):
    callback_payload = {
        "acknowledgement": "Webhook response received and processed",
        "original_response": previous_response
    }
    print("Sending callback with the following payload:")
    print(json.dumps(callback_payload, indent=4))
    # Optionally, you can POST this payload to another endpoint if required.

def poll_workflow(workflow_id, poll_interval=5, timeout=60):
    url = f"{CONDUCTOR_SERVER_URL}/workflow/{workflow_id}"
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            workflow_status = response.json().get("status")
            print(f"Current workflow status: {workflow_status}")
            if workflow_status in ["COMPLETED", "FAILED", "TERMINATED"]:
                print("Workflow execution finished.")
                print("Final workflow details:", json.dumps(response.json(), indent=4))
                return
        else:
            print("Error polling workflow:", response.status_code)
        time.sleep(poll_interval)
    print("Polling timed out before workflow completion.")

def main():
    token = get_auth_token()
    if token is None:
        print("Aborting due to authentication error.")
        return

    # Debug: Print token value
    print("Token:", token)

    # Update global headers with the token.
    # Here we add it in two common ways. If your Conductor instance requires a different header,
    # consult its documentation and update accordingly.
    headers["Authorization"] = f"Bearer {token}"
    headers["X-Authorization"] = f"Bearer {token}"

    register_workflow()
    workflow_id = start_workflow()
    if workflow_id is None:
        print("Aborting due to workflow start error.")
        return
    # Allow a brief pause to ensure the workflow is waiting on the webhook
    time.sleep(2)
    send_webhook()
    poll_workflow(workflow_id)

if __name__ == "__main__":
    main()
