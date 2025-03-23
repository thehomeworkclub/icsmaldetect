#!/usr/bin/env python3
import os
import time
import json
import requests
from datetime import datetime
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from sensordata.arima_detector import ArimaDetector

# Orkes Conductor configuration
CONDUCTOR_AUTH_KEY = os.getenv("CONDUCTOR_AUTH_KEY", "zxvp2aa7baf2-076d-11f0-9d9d-065ebd459714")
CONDUCTOR_AUTH_SECRET = os.getenv("CONDUCTOR_AUTH_SECRET", "kyORq2J20gc9E3tLUiabEBdBWWpNkD2Db00FwoZMg1LUXKrw")
CONDUCTOR_SERVER_URL = os.getenv("CONDUCTOR_SERVER_URL", "https://developer.orkescloud.com/api")
WEBHOOK_URL = "https://developer.orkescloud.com/webhook/zxvp050b08aa-0772-11f0-9d9d-05e8bd459714"

class OrkesICSMonitor:
    def __init__(self):
        self.detector = ArimaDetector()
        self.headers = {
            "Content-Type": "application/json",
            "x-conductor-auth-key": CONDUCTOR_AUTH_KEY,
            "x-conductor-auth-secret": CONDUCTOR_AUTH_SECRET
        }
        
        # Sample test data
        self.test_values = {
            'rotation_speed': 50000,
            'vibration': 2.0,
            'temperature': 75.0,
            'pressure': 550.0,
            'flow_rate': 70.0
        }

    def simulate_anomaly(self):
        """Simulate an anomaly by increasing rotation speed dramatically"""
        anomaly_values = self.test_values.copy()
        anomaly_values['rotation_speed'] = 65000  # Significant increase
        anomaly_values['vibration'] = 4.0        # Higher vibration
        return anomaly_values

    def send_webhook_notification(self, metric, value, anomaly_score):
        """Send webhook notification to Orkes Conductor"""
        payload = {
            "metric": metric,
            "value": value,
            "anomaly_score": anomaly_score,
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            response = requests.post(
                WEBHOOK_URL,
                headers=self.headers,
                json=payload
            )
            
            print(f"Webhook Response: {response.status_code}")
            print(f"Response body: {response.text}")
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error sending webhook: {str(e)}")
            return False

    def run_test(self):
        """Run a test simulation with anomaly detection"""
        print("Starting ICS monitoring test with Orkes Conductor integration...")

        # Phase 1: Normal operation
        print("\nPhase 1: Normal operation")
        for _ in range(30):  # 30 seconds of normal operation
            for metric, value in self.test_values.items():
                noise = value * 0.01  # 1% noise
                noisy_value = value + (noise * (2 * (0.5 - 0.5)))  # Random noise
                self.detector.add_reading(metric, noisy_value)
            time.sleep(1)

        # Phase 2: Introduce anomaly
        print("\nPhase 2: Introducing anomaly")
        anomaly_values = self.simulate_anomaly()
        
        for metric, value in anomaly_values.items():
            # Get anomaly status
            status = self.detector.get_status(metric, value)
            
            if status['is_anomaly'] and status['deviation'] is not None:
                # Calculate anomaly score
                anomaly_score = min(100, (status['deviation'] / self.detector.thresholds[metric]) * 50)
                
                print(f"\nAnomaly detected in {metric}:")
                print(f"Value: {value}")
                print(f"Anomaly score: {anomaly_score}")
                
                # Send webhook notification
                if self.send_webhook_notification(metric, value, anomaly_score):
                    print(f"Webhook notification sent successfully for {metric}")
                else:
                    print(f"Failed to send webhook notification for {metric}")

def main():
    monitor = OrkesICSMonitor()
    monitor.run_test()

if __name__ == "__main__":
    main()
