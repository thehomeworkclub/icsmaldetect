#!/usr/bin/env python3
import time
import random
import logging
from prometheus_client import start_http_server, Gauge, Counter
from arima_detector import ArimaDetector
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")

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
        
        logger.info("Base values set: %s", str(self.normal_params))

    def add_noise(self, value):
        """Add minimal random noise (matching training data)"""
        noise = random.uniform(-0.01, 0.01)  # 0.1% variation
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
                print(status)
                if status['is_anomaly']:
                    logger.warning(
                        f"Anomaly detected in normal metrics - {metric_name}: "
                        f"value={value:.2f}, deviation={status['deviation']:.2f}"
                    )
            
            # Increment update counter
            self.updates.inc()
            
        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}", exc_info=True)

def main():
    try:
        # Start Prometheus HTTP server on port 8000
        start_http_server(8000)
        logger.info("Started Prometheus metrics server on port 8000")
        
        # Initialize metrics
        metrics = ICSMetrics()
        logger.info("ICS Metrics initialized successfully")
        
        # Update metrics every second
        update_count = 0
        while True:
            metrics.update_metrics()
            update_count += 1
            
            # Log status every 10 updates
            if update_count % 10 == 0:
                logger.info(f"Normal operation continues. Updates: {update_count}")
            
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Fatal error in ICS metrics simulation: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
