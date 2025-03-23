#!/usr/bin/env python3
import time
import random
import math
import logging
from prometheus_client import start_http_server, Gauge, Counter
from arima_detector import ArimaDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ICSAttackSimulation:
    def __init__(self):
        logger.info("Initializing ICS Attack Simulation...")
        
        # Initialize ARIMA detector
        self.detector = ArimaDetector()
        
        # Base metrics (Prometheus will add attack_ prefix)
        self.metrics = {
            'rotation_speed': Gauge('centrifuge_rotation_speed', 'Centrifuge rotation speed in RPM'),
            'vibration': Gauge('centrifuge_vibration', 'Vibration amplitude in mm/s'),
            'temperature': Gauge('centrifuge_temperature', 'Temperature in Celsius'),
            'pressure': Gauge('centrifuge_pressure', 'Process gas pressure in Pa'),
            'flow_rate': Gauge('gas_flow_rate', 'UF6 gas flow rate in g/min'),
            'voltage': Gauge('power_voltage', 'Operating voltage in V'),
            'current': Gauge('power_current', 'Operating current in A')
        }
        
        # Attack counters
        self.attack_counts = Counter('attacks_total', 'Total number of attacks initiated', ['type'])
        self.metric_updates = Counter('attack_metric_updates_total', 'Total number of metric updates during attacks')
        
        # Initial parameters (matching training data)
        self.base_params = {
            'rotation_speed': 10000,  # RPM
            'vibration': 2.0,         # mm/s
            'temperature': 75.0,      # °C
            'pressure': 550.0,        # Pa
            'flow_rate': 70.0,        # g/min
            'voltage': 380.0,         # V
            'current': 10.0           # A
        }
        
        # Copy base params to current params
        self.current_params = self.base_params.copy()
        
        # Attack ranges (based on training data anomalies)
        self.attack_params = {
            'rotation_speed': {'max': 20000, 'min': 1000},     # RPM
            'vibration': {'max': 4.0, 'min': 0.1},            # mm/s
            'temperature': {'max': 85.0, 'min': 65.0},        # °C
            'pressure': {'max': 560.0, 'min': 540.0},         # Pa
            'flow_rate': {'max': 80.0, 'min': 60.0},          # g/min
            'voltage': {'max': 390.0, 'min': 370.0},          # V
            'current': {'max': 20.0, 'min': 5.0}              # A
        }
        
        # Attack state
        self.attack_type = None
        self.attack_progress = 0
        self.attack_duration = 60
        self.is_attacking = False
        self.attack_cooldown = 0
        self.cooldown_period = 120
        
        logger.info("Attack simulation initialized with base values: %s", str(self.base_params))

    def add_minimal_noise(self, value):
        """Add minimal noise (matching training data)"""
        noise = random.uniform(-0.1, 0.1)  # 0.1% variation
        return value + (value * noise)

    def generate_attack_value(self, metric_name):
        """Generate attack values based on training data patterns"""
        base_value = self.base_params[metric_name]
        attack_range = self.attack_params[metric_name]
        progress_factor = (self.attack_progress % self.attack_duration) / self.attack_duration
        
        if self.attack_type == 'gradual':
            # Gradual deviation
            max_change = attack_range['max'] - base_value
            change = max_change * (progress_factor ** 2)
            new_value = base_value + change
            
        elif self.attack_type == 'oscillating':
            # Oscillating pattern
            amplitude = (attack_range['max'] - attack_range['min']) * 0.5
            frequency = 2.0
            new_value = base_value + amplitude * math.sin(progress_factor * 2 * math.pi * frequency)
            
        else:  # sudden
            # Random jumps
            if random.random() < 0.4:
                new_value = random.choice([
                    attack_range['min'],
                    attack_range['max'],
                    base_value * 1.5,
                    base_value * 0.5
                ])
            else:
                deviation = random.uniform(0.5, 1.5)
                new_value = base_value * deviation
        
        return new_value

    def update_metrics(self):
        """Update metrics with attack patterns"""
        try:
            self.attack_progress += 1
            current_values = {}
            
            # Handle attack state changes
            if not self.is_attacking:
                if self.attack_cooldown > 0:
                    self.attack_cooldown -= 1
                elif random.random() < 0.02:  # 2% chance to start attack
                    self.is_attacking = True
                    self.attack_type = random.choice(['gradual', 'oscillating', 'sudden'])
                    self.attack_counts.labels(type=self.attack_type).inc()
                    logger.warning(f"\n!!! CRITICAL ALERT: {self.attack_type.upper()} ATTACK INITIATED !!!")
            
            # Generate and set new values
            for metric_name in self.metrics:
                if self.is_attacking:
                    value = self.generate_attack_value(metric_name)
                else:
                    value = self.add_minimal_noise(self.base_params[metric_name])
                
                # Update current values and Prometheus metrics
                current_values[metric_name] = value
                self.metrics[metric_name].set(value)
                logger.debug(f"Set {metric_name} to {value:.2f}")
            
            # Check for anomalies
            for metric_name, value in current_values.items():
                status = self.detector.get_status(metric_name, value, current_values)
                if status['is_anomaly']:
                    logger.warning(
                        f"Attack detected in {metric_name}: "
                        f"value={value:.2f}, deviation={status['deviation']:.2f}"
                    )
            
            # Increment update counter
            self.metric_updates.inc()
            
            # Check for attack phase end
            if self.is_attacking and self.attack_progress % self.attack_duration == 0:
                self.is_attacking = False
                self.attack_cooldown = self.cooldown_period
                logger.info("\n--- Attack phase ended, systems attempting to stabilize ---")
                
        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}", exc_info=True)

def main():
    try:
        start_http_server(8001)
        logger.info("Started Prometheus metrics server on port 8001")
        
        simulation = ICSAttackSimulation()
        logger.info("Attack simulation initialized and ready")
        
        update_count = 0
        while True:
            simulation.update_metrics()
            update_count += 1
            
            if update_count % 10 == 0 and not simulation.is_attacking:
                logger.info(f"Normal operation continues. Updates: {update_count}")
            
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Fatal error in attack simulation: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
