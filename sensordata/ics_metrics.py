#!/usr/bin/env python3
import time
import random
from prometheus_client import start_http_server, Gauge

# Initialize Prometheus metrics
class ICSMetrics:
    def __init__(self):
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
            'rotation_speed': 50000,  # RPM
            'vibration': 2.0,         # mm/s
            'temperature': 75.0,      # °C
            'pressure': 550.0,        # Pa
            'flow_rate': 70.0,        # g/min
            'voltage': 380.0,         # V
            'current': 10.0           # A
        }

    def add_noise(self, value, noise_factor):
        """Add random noise to a value"""
        noise = random.uniform(-noise_factor, noise_factor)
        return value + (value * noise)

    def update_metrics(self):
        """Update all metrics with new values"""
        # Simulate normal operation with small variations
        self.rotation_speed.set(self.add_noise(self.normal_params['rotation_speed'], 0.01))
        self.vibration.set(self.add_noise(self.normal_params['vibration'], 0.05))
        self.temperature.set(self.add_noise(self.normal_params['temperature'], 0.02))
        self.pressure.set(self.add_noise(self.normal_params['pressure'], 0.03))
        self.flow_rate.set(self.add_noise(self.normal_params['flow_rate'], 0.02))
        self.voltage.set(self.add_noise(self.normal_params['voltage'], 0.005))
        self.current.set(self.add_noise(self.normal_params['current'], 0.02))

def main():
    try:
        # Start Prometheus HTTP server on port 8000
        start_http_server(8000)
        print("Prometheus metrics server started on port 8000")
        
        # Initialize metrics
        metrics = ICSMetrics()
        print("ICS metrics initialized successfully")
        
        # Update metrics every second
        while True:
            metrics.update_metrics()
            time.sleep(1)
    except Exception as e:
        print(f"Error in ICS metrics simulation: {str(e)}")
        raise

if __name__ == '__main__':
    main()
