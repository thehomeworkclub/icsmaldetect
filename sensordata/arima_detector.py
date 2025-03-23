#!/usr/bin/env python3
import numpy as np
from collections import deque
import warnings
import requests
warnings.filterwarnings('ignore')

class ArimaDetector:
    def __init__(self, window_size=10):
        self.detectors = {}
        self.window_size = window_size
        self.api_url = "https://orkes-api-tester.orkesconductor.com/api/detect"
        
        # Define thresholds for different metrics (based on percentage deviation)
        self.thresholds = {
            'rotation_speed': 0.05,  # 5% deviation
            'vibration': 0.10,      # 10% deviation
            'temperature': 0.03,     # 3% deviation
            'pressure': 0.05,        # 5% deviation
            'flow_rate': 0.05,       # 5% deviation
            'voltage': 0.02,         # 2% deviation
            'current': 0.05          # 5% deviation
        }
    
    def _get_detector(self, metric_name):
        """Get or create a detector for a specific metric"""
        if metric_name not in self.detectors:
            self.detectors[metric_name] = {
                'points': deque(maxlen=self.window_size),
                'mean': None,
                'std': None
            }
        return self.detectors[metric_name]
    
    def _add_point(self, metric_name, point):
        """Add a new data point to the specified metric's detection window"""
        try:
            point_value = float(point)
            detector = self._get_detector(metric_name)
            detector['points'].append(point_value)
            
            # Update rolling statistics
            if len(detector['points']) > 1:
                detector['mean'] = np.mean(list(detector['points'])[:-1])
                detector['std'] = np.std(list(detector['points'])[:-1])
        except (ValueError, TypeError):
            warnings.warn(f"Invalid point value for {metric_name}: {point}")
    
    def get_status(self, metric_name, value):
        """
        Get anomaly status for a metric
        Returns: dict with is_anomaly flag and deviation score
        """
        self._add_point(metric_name, value)
        detector = self._get_detector(metric_name)
        
        if len(detector['points']) < 3:
            return {'is_anomaly': False, 'deviation': None}
            
        try:
            last_point = detector['points'][-1]
            deviation = None
            
            # Calculate deviation if we have mean and std
            if detector['mean'] is not None and detector['std'] is not None:
                deviation = abs(last_point - detector['mean']) / detector['mean']
                
                # Check if deviation exceeds threshold
                if deviation > self.thresholds.get(metric_name, 0.05):
                    # Verify with API
                    try:
                        response = requests.get(
                            self.api_url,
                            params={
                                "metric": metric_name,
                                "value": last_point,
                                "mean": detector['mean'],
                                "std": detector['std']
                            },
                            timeout=5
                        )
                        if response.status_code == 200:
                            return {
                                'is_anomaly': response.json().get("is_anomaly", False),
                                'deviation': deviation
                            }
                    except requests.exceptions.RequestException:
                        # If API fails, use local detection
                        pass
                    
                    # Local decision based on threshold
                    return {
                        'is_anomaly': True,
                        'deviation': deviation
                    }
            
            return {
                'is_anomaly': False,
                'deviation': deviation
            }
            
        except Exception as e:
            warnings.warn(f"Detection error for {metric_name}: {str(e)}")
            return {'is_anomaly': False, 'deviation': None}
    
    def get_points(self, metric_name):
        """Return current points for a specific metric"""
        detector = self._get_detector(metric_name)
        return list(detector['points'])
