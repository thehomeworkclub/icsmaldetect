#!/usr/bin/env python3
import time
import random
import math
from prometheus_client import start_http_server, Gauge
from arima_detector import ArimaDetector

class ICSAttackSimulation:
    def __init__(self):
        # Initialize ARIMA detector
        self.detector = ArimaDetector()
        
        # Metrics under attack
        self.rotation_speed = Gauge('centrifuge_rotation_speed_attacked', 'Centrifuge rotation speed in RPM (with attacks)')
        self.vibration = Gauge('centrifuge_vibration_attacked', 'Vibration amplitude in mm/s (with attacks)')
        self.temperature = Gauge('centrifuge_temperature_attacked', 'Temperature in Celsius (with attacks)')
        self.pressure = Gauge('centrifuge_pressure_attacked', 'Process gas pressure in Pa (with attacks)')
        self.flow_rate = Gauge('gas_flow_rate_attacked', 'UF6 gas flow rate in g/min (with attacks)')
        self.voltage = Gauge('power_voltage_attacked', 'Operating voltage in V (with attacks)')
        self.current = Gauge('power_current_attacked', 'Operating current in A (with attacks)')
        
        # Initial parameters
        self.base_params = {
            'rotation_speed': 60000,  # RPM
            'vibration': 1.0,         # mm/s
            'temperature': 310.6,      # °K
            'pressure': 120.0,        # Kpa
            'flow_rate': 65,          # m^2/hr
            'voltage': 480,           # V
            'current': 1200           # A
        }
        
        # Copy base params to current params
        self.current_params = self.base_params.copy()
        
        # Catastrophic attack ranges
        self.attack_params = {
            'rotation_speed': {'max': 150000, 'min': 5000},    # Extreme speed variations
            'vibration': {'max': 50.0, 'min': 0.01},           # Dangerous vibrations
            'temperature': {'max': 800.0, 'min': 100.0},       # Critical temperature
            'pressure': {'max': 500.0, 'min': 5.0},            # Dangerous pressure
            'flow_rate': {'max': 200.0, 'min': 1.0},          # Critical flow disruption
            'voltage': {'max': 1000.0, 'min': 100.0},         # Severe power issues
            'current': {'max': 3000.0, 'min': 100.0}          # Dangerous current
        }
        
        # Attack state
        self.attack_type = None
        self.attack_progress = 0
        self.attack_duration = 60     # Longer duration for each attack
        self.is_attacking = False
        self.attack_cooldown = 0
        self.cooldown_period = 120    # 2 minutes between attacks

    def add_minimal_noise(self, value):
        """Add very minimal noise when not attacking"""
        noise = random.uniform(-0.00001, 0.00001)  # 0.001% variation
        return value + (value * noise)

    def generate_attack_value(self, metric_name):
        """Generate catastrophic attack values"""
        base_value = self.base_params[metric_name]
        attack_range = self.attack_params[metric_name]
        progress_factor = (self.attack_progress % self.attack_duration) / self.attack_duration
        
        if self.attack_type == 'meltdown':
            # Exponential increase to dangerous levels
            max_change = attack_range['max'] - base_value
            change = max_change * (progress_factor ** 3)  # Faster progression
            new_value = base_value + change
            
        elif self.attack_type == 'catastrophic':
            # Wild oscillations between extremes
            amplitude = attack_range['max'] - attack_range['min']
            frequency = 2.0  # Very fast oscillations
            new_value = ((attack_range['max'] + attack_range['min']) / 2 + 
                        amplitude * math.sin(progress_factor * 2 * math.pi * frequency))
            
        else:  # cascade
            # Cascading system failure
            severity = min(1.0, (self.attack_progress / 20))  # Quick escalation
            if random.random() < severity:
                new_value = random.choice([
                    attack_range['min'] * 0.5,  # Complete failure
                    attack_range['max'] * 1.5   # Catastrophic overload
                ])
            else:
                new_value = base_value * random.uniform(3.0, 5.0)  # Severe deviation
        
        return new_value

    def update_metrics(self):
        """Update metrics with attack patterns"""
        self.attack_progress += 1
        
        # Handle attack state changes
        if not self.is_attacking:
            if self.attack_cooldown > 0:
                self.attack_cooldown -= 1
            elif random.random() < 0.02:  # 2% chance to start attack
                self.is_attacking = True
                self.attack_type = random.choice(['meltdown', 'catastrophic', 'cascade'])
                print(f"\n!!! CRITICAL ALERT: {self.attack_type.upper()} ATTACK INITIATED !!!")
        
        # Generate and set new values
        for metric_name in self.current_params:
            if self.is_attacking:
                value = self.generate_attack_value(metric_name)
            else:
                value = self.add_minimal_noise(self.base_params[metric_name])
            
            # Calculate deviation
            base_value = self.base_params[metric_name]
            deviation_pct = ((value - base_value) / base_value) * 100
            
            # Update values
            self.current_params[metric_name] = value
            getattr(self, metric_name).set(value)
            
            # Report significant attacks
            if abs(deviation_pct) > 50:  # Only report major deviations
                print(f"CRITICAL: {metric_name} at {value:.2f} (deviation: {deviation_pct:+.1f}%)")
        
        # Check for attack phase end
        if self.is_attacking and self.attack_progress % self.attack_duration == 0:
            self.is_attacking = False
            self.attack_cooldown = self.cooldown_period
            print("\n--- Attack phase ended, systems attempting to stabilize ---")

def main():
    try:
        start_http_server(8001)
        simulation = ICSAttackSimulation()
        print("\nAttack simulation ready. Waiting to initiate...")
        print("Normal values:", simulation.base_params)
        
        while True:
            simulation.update_metrics()
            time.sleep(1)
    except Exception as e:
        print(f"Error in attack simulation: {str(e)}")
        raise

if __name__ == '__main__':
    main()
