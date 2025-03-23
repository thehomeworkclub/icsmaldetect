#!/usr/bin/env python3
import os
import json
import requests

# Orkes Conductor configuration
CONDUCTOR_AUTH_KEY = os.getenv("CONDUCTOR_AUTH_KEY", "zxvp2aa7baf2-076d-11f0-9d9d-065ebd459714")
CONDUCTOR_AUTH_SECRET = os.getenv("CONDUCTOR_AUTH_SECRET", "kyORq2J20gc9E3tLUiabEBdBWWpNkD2Db00FwoZMg1LUXKrw")
CONDUCTOR_SERVER_URL = "https://developer.orkescloud.com/api"

def register_workflow():
    """Register the workflow definition with Orkes Conductor"""
    headers = {
        "Content-Type": "application/json",
        "x-conductor-auth-key": CONDUCTOR_AUTH_KEY,
        "x-conductor-auth-secret": CONDUCTOR_AUTH_SECRET
    }

    # Read workflow definition
    with open('webhook_workflow.json', 'r') as f:
        workflow_def = json.load(f)

    # Register workflow
    register_url = f"{CONDUCTOR_SERVER_URL}/metadata/workflow"
    
    try:
        response = requests.post(
            register_url,
            headers=headers,
            json=[workflow_def]  # API expects an array of workflow definitions
        )
        
        print(f"Workflow registration status: {response.status_code}")
        print("Response:", response.text)
        
        if response.status_code == 204:
            print("Workflow registered successfully!")
        else:
            print("Failed to register workflow")
            
    except Exception as e:
        print(f"Error registering workflow: {str(e)}")

def start_workflow():
    """Start a workflow execution"""
    headers = {
        "Content-Type": "application/json",
        "x-conductor-auth-key": CONDUCTOR_AUTH_KEY,
        "x-conductor-auth-secret": CONDUCTOR_AUTH_SECRET
    }

    # Workflow input
    workflow_input = {
        "callback_url": "http://localhost:8080/webhook-response"
    }

    # Start workflow
    start_url = f"{CONDUCTOR_SERVER_URL}/workflow/webhook_echo_workflow"
    
    try:
        response = requests.post(
            start_url,
            headers=headers,
            json=workflow_input
        )
        
        print(f"\nWorkflow start status: {response.status_code}")
        print("Response:", response.text)
        
        if response.status_code == 200:
            workflow_id = response.text.strip('"')
            print(f"Workflow started with ID: {workflow_id}")
            return workflow_id
        else:
            print("Failed to start workflow")
            
    except Exception as e:
        print(f"Error starting workflow: {str(e)}")

if __name__ == "__main__":
    print("Registering workflow with Orkes Conductor...")
    register_workflow()
    
    print("\nStarting workflow execution...")
    workflow_id = start_workflow()
    
    if workflow_id:
        print(f"\nWorkflow Status URL: https://play.orkes.io/execution/{workflow_id}")
