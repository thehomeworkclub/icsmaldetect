#!/usr/bin/env python3
import time
import random
import math
from prometheus_client import start_http_server, Gauge

class ICSAttackSimulation:
    def __init__(self):
        # Centrifuge metrics with attack patterns
        self.rotation_speed = Gauge('centrifuge_rotation_speed_attacked', 'Centrifuge rotation speed in RPM (with attacks)')
        self.vibration = Gauge('centrifuge_vibration_attacked', 'Vibration amplitude in mm/s (with attacks)')
        self.temperature = Gauge('centrifuge_temperature_attacked', 'Temperature in Celsius (with attacks)')
        self.pressure = Gauge('centrifuge_pressure_attacked', 'Process gas pressure in Pa (with attacks)')
        self.flow_rate = Gauge('gas_flow_rate_attacked', 'UF6 gas flow rate in g/min (with attacks)')
        self.voltage = Gauge('power_voltage_attacked', 'Operating voltage in V (with attacks)')
        self.current = Gauge('power_current_attacked', 'Operating current in A (with attacks)')
        
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
        
        # Attack state
        self.attack_active = False
        self.attack_type = None
        self.attack_duration = 0
        self.attack_progress = 0

    def add_noise(self, value, noise_factor):
        """Add random noise to a value"""
        noise = random.uniform(-noise_factor, noise_factor)
        return value + (value * noise)

    def simulate_stuxnet_attack(self):
        """Simulate different types of Stuxnet-like attacks"""
        if not self.attack_active:
            # 5% chance to start an attack
            if random.random() < 0.05:
                self.attack_active = True
                self.attack_type = random.choice([
                    'overspeed',      # Dangerous speed increase
                    'underspeed',     # Subtle speed decrease
                    'oscillation'     # Speed oscillation
                ])
                self.attack_duration = random.randint(10, 30)  # Attack lasts 10-30 seconds
                self.attack_progress = 0
                print(f"Starting {self.attack_type} attack for {self.attack_duration} seconds")

        if self.attack_active:
            self.attack_progress += 1
            if self.attack_progress >= self.attack_duration:
                self.attack_active = False
                self.attack_type = None
                print("Attack completed")

    def get_attack_values(self):
        """Calculate sensor values based on current attack state"""
        if not self.attack_active:
            return {k: self.add_noise(v, 0.01) for k, v in self.normal_params.items()}

        values = self.normal_params.copy()
        progress_factor = self.attack_progress / self.attack_duration

        if self.attack_type == 'overspeed':
            # Gradually increase speed to 63,000 RPM
            speed_increase = 13000 * progress_factor
            values['rotation_speed'] += speed_increase
            values['vibration'] += speed_increase / 1000  # Increased vibration
            values['temperature'] += speed_increase / 500  # Temperature rise
            values['current'] += speed_increase / 5000  # Higher power consumption

        elif self.attack_type == 'underspeed':
            # Subtly decrease speed by up to 10%
            speed_decrease = 5000 * progress_factor
            values['rotation_speed'] -= speed_decrease
            values['flow_rate'] -= speed_decrease / 10000
            values['pressure'] -= speed_decrease / 100

        elif self.attack_type == 'oscillation':
            # Create oscillating speed pattern
            oscillation = 2000 * math.sin(self.attack_progress * 0.5)
            values['rotation_speed'] += oscillation
            values['vibration'] += abs(oscillation / 1000)
            values['pressure'] += oscillation / 100

        return values

    def update_metrics(self):
        """Update all metrics with new values"""
        self.simulate_stuxnet_attack()
        values = self.get_attack_values()
        
        # Set new values
        self.rotation_speed.set(values['rotation_speed'])
        self.vibration.set(values['vibration'])
        self.temperature.set(values['temperature'])
        self.pressure.set(values['pressure'])
        self.flow_rate.set(values['flow_rate'])
        self.voltage.set(values['voltage'])
        self.current.set(values['current'])

def main():
    try:
        # Start Prometheus HTTP server on port 8001 (different from normal metrics)
        start_http_server(8001)
        print("Prometheus metrics server (attack simulation) started on port 8001")
        
        # Initialize metrics
        metrics = ICSAttackSimulation()
        print("Attack simulation metrics initialized successfully")
        
        # Update metrics every second
        while True:
            metrics.update_metrics()
            time.sleep(1)
    except Exception as e:
        print(f"Error in attack simulation: {str(e)}")
        raise

if __name__ == '__main__':
    main()
