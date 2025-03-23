#!/usr/bin/env python3
import time
import random
import math
import logging
import threading
import signal
import sys
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
        
        # Attack ranges
        self.attack_params = {
            'rotation_speed': {'max': 20000, 'min': 1000},
            'vibration': {'max': 4.0, 'min': 0.1},
            'temperature': {'max': 85.0, 'min': 65.0},
            'pressure': {'max': 560.0, 'min': 540.0},
            'flow_rate': {'max': 80.0, 'min': 60.0},
            'voltage': {'max': 390.0, 'min': 370.0},
            'current': {'max': 20.0, 'min': 5.0}
        }
        
        # Control flags
        self.is_running = True
        self.is_attacking = False
        self.attack_type = None
        self.attack_progress = 0
        self.metrics_thread = None
        
        # Signal handlers
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        if sys.platform == 'win32':
            signal.signal(signal.SIGBREAK, self.handle_signal)
        
        logger.info("Attack simulation initialized with base values")

    def handle_signal(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Shutdown signal received, stopping attack simulation...")
        self.stop()

    def stop(self):
        """Stop simulation"""
        self.is_running = False
        if self.metrics_thread and self.metrics_thread.is_alive():
            self.metrics_thread.join(timeout=5)
        logger.info("Attack simulation stopped")

    def add_minimal_noise(self, value):
        """Add minimal noise"""
        noise = random.uniform(-0.1, 0.1)
        return value + (value * noise)

    def generate_attack_value(self, metric_name):
        """Generate attack values"""
        base_value = self.base_params[metric_name]
        attack_range = self.attack_params[metric_name]
        progress_factor = (self.attack_progress % 60) / 60.0
        
        if self.attack_type == 'gradual':
            max_change = attack_range['max'] - base_value
            change = max_change * (progress_factor ** 2)
            new_value = base_value + change
            
        elif self.attack_type == 'oscillating':
            amplitude = (attack_range['max'] - attack_range['min']) * 0.5
            frequency = 2.0
            new_value = base_value + amplitude * math.sin(progress_factor * 2 * math.pi * frequency)
            
        else:  # sudden
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
            # Handle attack state changes
            if not self.is_attacking and random.random() < 0.02:
                self.is_attacking = True
                self.attack_type = random.choice(['gradual', 'oscillating', 'sudden'])
                self.attack_counts.labels(type=self.attack_type).inc()
                logger.warning(f"\n!!! CRITICAL ALERT: {self.attack_type.upper()} ATTACK INITIATED !!!")
            
            current_values = {}
            for metric_name in self.metrics:
                if self.is_attacking:
                    value = self.generate_attack_value(metric_name)
                else:
                    value = self.add_minimal_noise(self.base_params[metric_name])
                
                self.metrics[metric_name].set(value)
                current_values[metric_name] = value
            
            # Check for anomalies
            for metric_name, value in current_values.items():
                status = self.detector.get_status(metric_name, value, current_values)
                if status['is_anomaly']:
                    logger.warning(
                        f"Attack detected in {metric_name}: "
                        f"value={value:.2f}, deviation={status['deviation']:.2f}"
                    )
            
            # Handle attack progression
            if self.is_attacking:
                self.attack_progress += 1
                if self.attack_progress % 60 == 0:
                    self.is_attacking = False
                    self.attack_progress = 0
                    logger.info("\n--- Attack phase ended, systems attempting to stabilize ---")
            
            # Increment update counter
            self.metric_updates.inc()
            
        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}", exc_info=True)
            if not self.is_running:
                raise

    def metrics_loop(self):
        """Main metrics update loop"""
        update_count = 0
        logger.info("Starting attack simulation loop")
        
        while self.is_running:
            try:
                self.update_metrics()
                update_count += 1
                
                # Log status every 10 updates
                if update_count % 10 == 0 and not self.is_attacking:
                    logger.info(f"Normal operation continues. Updates: {update_count}")
                
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in metrics loop: {str(e)}")
                if self.is_running:  # Only raise if we're not shutting down
                    raise
                break

    def start(self):
        """Start attack simulation"""
        try:
            # Start Prometheus HTTP server
            logger.info("Starting Prometheus metrics server on port 8001...")
            start_http_server(8001)
            logger.info("Prometheus metrics server started successfully")
            
            # Start metrics update thread
            self.metrics_thread = threading.Thread(target=self.metrics_loop)
            self.metrics_thread.start()
            logger.info("Attack simulation thread started")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start attack simulation: {str(e)}")
            self.stop()
            return False

def main():
    try:
        # Initialize and start attack simulation
        simulation = ICSAttackSimulation()
        if not simulation.start():
            sys.exit(1)
        
        # Keep main thread alive until signal received
        while simulation.is_running:
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Fatal error in attack simulation: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("Shutting down attack simulation...")

if __name__ == '__main__':
    main()
