#!/usr/bin/env python3
import time
import random
from prometheus_client import start_http_server, Gauge
from arima_detector import ArimaDetector

class ICSMetrics:
    def __init__(self):
        # Initialize ARIMA detector
        self.detector = ArimaDetector()
        
        # Centrifuge metrics
        self.rotation_speed = Gauge('centrifuge_rotation_speed', 'Centrifuge rotation speed in RPM')
        self.vibration = Gauge('centrifuge_vibration', 'Vibration amplitude in mm/s')
        self.temperature = Gauge('centrifuge_temperature', 'Temperature in Celsius')
        self.pressure = Gauge('centrifuge_pressure', 'Process gas pressure in Pa')
        self.flow_rate = Gauge('gas_flow_rate', 'UF6 gas flow rate in g/min')
        self.voltage = Gauge('power_voltage', 'Operating voltage in V')
        self.current = Gauge('power_current', 'Operating current in A')
        
        # Normal operating parameters
        self.normal_params = {
            'rotation_speed': 60000,  # RPM
            'vibration': 1.0,         # mm/s
            'temperature': 310.6,      # °K
            'pressure': 120.0,        # Kpa
            'flow_rate': 65,          # m^2/hr
            'voltage': 480,           # V
            'current': 1200           # A
        }

    def add_noise(self, value, noise_factor):
        """Add minimal random noise to a value"""
        noise = random.uniform(-noise_factor, noise_factor)
        return value + (value * noise)

    def update_metrics(self):
        """Update all metrics with new values"""
        # Generate new values with extremely minimal noise
        new_values = {
            'rotation_speed': self.add_noise(self.normal_params['rotation_speed'], 0.00001),  # 0.001% variation
            'vibration': self.add_noise(self.normal_params['vibration'], 0.00005),           # 0.005% variation
            'temperature': self.add_noise(self.normal_params['temperature'], 0.00002),        # 0.002% variation
            'pressure': self.add_noise(self.normal_params['pressure'], 0.00003),             # 0.003% variation
            'flow_rate': self.add_noise(self.normal_params['flow_rate'], 0.00002),          # 0.002% variation
            'voltage': self.add_noise(self.normal_params['voltage'], 0.00001),              # 0.001% variation
            'current': self.add_noise(self.normal_params['current'], 0.00002)               # 0.002% variation
        }
        
        # Update metrics and check for anomalies
        for metric_name, value in new_values.items():
            # Set the value
            getattr(self, metric_name).set(value)

def main():
    try:
        # Start Prometheus HTTP server on port 8000
        start_http_server(8000)
        print("\nStarted normal operation simulation...")
        
        # Initialize metrics
        metrics = ICSMetrics()
        print("Base values:", metrics.normal_params)
        
        # Update metrics every second
        while True:
            metrics.update_metrics()
            time.sleep(1)
    except Exception as e:
        print(f"Error in ICS metrics simulation: {str(e)}")
        raise

if __name__ == '__main__':
    main()
