#!/usr/bin/env python3
import time
import random
import logging
import threading
import signal
import sys
from prometheus_client import start_http_server, Gauge, Counter
from arima_detector import ArimaDetector
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ICSMetrics:
    def __init__(self):
        logger.info("Initializing ICS Metrics...")
        
        # Initialize ARIMA detector
        self.detector = ArimaDetector()
        
        # Base metrics (Prometheus will add normal_ prefix)
        self.metrics = {
            'rotation_speed': Gauge('centrifuge_rotation_speed', 'Centrifuge rotation speed in RPM'),
            'vibration': Gauge('centrifuge_vibration', 'Vibration amplitude in mm/s'),
            'temperature': Gauge('centrifuge_temperature', 'Temperature in Celsius'),
            'pressure': Gauge('centrifuge_pressure', 'Process gas pressure in Pa'),
            'flow_rate': Gauge('gas_flow_rate', 'UF6 gas flow rate in g/min'),
            'voltage': Gauge('power_voltage', 'Operating voltage in V'),
            'current': Gauge('power_current', 'Operating current in A')
        }
        
        # Base parameters (matching training data)
        self.normal_params = {
            'rotation_speed': 10000,  # RPM
            'vibration': 2.0,         # mm/s
            'temperature': 75.0,      # °C
            'pressure': 550.0,        # Pa
            'flow_rate': 70.0,        # g/min
            'voltage': 380.0,         # V
            'current': 10.0           # A
        }
        
        # Update counter
        self.updates = Counter('metric_updates_total', 'Total number of metric updates')
        
        # Control flags
        self.is_running = True
        self.metrics_thread = None
        
        # Signal handlers
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        if sys.platform == 'win32':
            signal.signal(signal.SIGBREAK, self.handle_signal)
        
        logger.info("Base values set: %s", str(self.normal_params))

    def handle_signal(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Shutdown signal received, stopping metrics collection...")
        self.stop()

    def stop(self):
        """Stop metrics collection"""
        self.is_running = False
        if self.metrics_thread and self.metrics_thread.is_alive():
            self.metrics_thread.join(timeout=5)
        logger.info("Metrics collection stopped")

    def add_noise(self, value):
        """Add minimal random noise (matching training data)"""
        noise = random.uniform(-0.1, 0.1)  # 0.1% variation
        return value + (value * noise)

    def update_metrics(self):
        """Update all metrics with new values"""
        try:
            # Generate new values with minimal noise
            current_values = {}
            
            # Update each metric
            for metric_name, base_value in self.normal_params.items():
                value = self.add_noise(base_value)
                current_values[metric_name] = value
                
                # Set the metric value
                self.metrics[metric_name].set(value)
                logger.debug(f"Set {metric_name} to {value:.2f}")
            
            # Check for anomalies
            for metric_name, value in current_values.items():
                status = self.detector.get_status(metric_name, value, current_values)
                if status['is_anomaly']:
                    logger.warning(
                        f"Anomaly detected in normal metrics - {metric_name}: "
                        f"value={value:.2f}, deviation={status['deviation']:.2f}"
                    )
            
            # Increment update counter
            self.updates.inc()
            
        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}", exc_info=True)
            if not self.is_running:
                raise

    def metrics_loop(self):
        """Main metrics update loop"""
        update_count = 0
        logger.info("Starting metrics collection loop")
        
        while self.is_running:
            try:
                self.update_metrics()
                update_count += 1
                
                # Log status every 10 updates
                if update_count % 10 == 0:
                    logger.info(f"Normal operation continues. Updates: {update_count}")
                
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in metrics loop: {str(e)}")
                if self.is_running:  # Only raise if we're not shutting down
                    raise
                break

    def start(self):
        """Start metrics collection"""
        try:
            # Start Prometheus HTTP server
            logger.info("Starting Prometheus metrics server on port 8000...")
            start_http_server(8000)
            logger.info("Prometheus metrics server started successfully")
            
            # Start metrics update thread
            self.metrics_thread = threading.Thread(target=self.metrics_loop)
            self.metrics_thread.start()
            logger.info("Metrics collection thread started")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start metrics collection: {str(e)}")
            self.stop()
            return False

def main():
    try:
        # Initialize and start metrics collection
        metrics = ICSMetrics()
        if not metrics.start():
            sys.exit(1)
        
        # Keep main thread alive until signal received
        while metrics.is_running:
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Fatal error in ICS metrics simulation: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("Shutting down ICS metrics simulation...")

if __name__ == '__main__':
    main()
