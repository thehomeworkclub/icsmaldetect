#!/usr/bin/env python3
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from sklearn.tree import DecisionTreeClassifier
import pandas as pd
from collections import deque
import warnings
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArimaDetector:
    def __init__(self, window_size=30):
        self.detectors = {}
        self.window_size = window_size
        self.api_url = "https://orkes-api-tester.orkesconductor.com/api/detect"
        
        # Train decision tree
        try:
            data = pd.read_csv("data.csv")
            X = data.drop(columns=["is_normal"])
            y = data["is_normal"]
            self.decision_tree = DecisionTreeClassifier(max_depth=6)
            self.decision_tree.fit(X, y)
            logger.info("Decision tree model trained successfully")
            
            # Get feature names for prediction
            self.feature_names = X.columns.tolist()
            logger.info(f"Feature names: {self.feature_names}")
            
        except Exception as e:
            logger.error(f"Failed to train decision tree: {str(e)}")
            self.decision_tree = None
            self.feature_names = None
    
    def _get_detector(self, metric_name):
        """Get or create a detector for a specific metric"""
        if metric_name not in self.detectors:
            self.detectors[metric_name] = {
                'points': deque(maxlen=self.window_size),
                'model': None,
                'is_stationary': None
            }
        return self.detectors[metric_name]
    
    def _check_stationarity(self, data):
        """Check if the time series is stationary using Augmented Dickey-Fuller test"""
        try:
            result = adfuller(data)
            return result[1] <= 0.05
        except:
            return False
    
    def _difference_series(self, data):
        """Apply differencing to make series stationary"""
        return np.diff(data)
    
    def _add_point(self, metric_name, point):
        """Add a new data point to the specified metric's detection window"""
        try:
            point_value = float(point)
            detector = self._get_detector(metric_name)
            detector['points'].append(point_value)
            
            # Update stationarity check when enough points are available
            if len(detector['points']) >= self.window_size:
                data = np.array(detector['points'])
                detector['is_stationary'] = self._check_stationarity(data)
                
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid point value for {metric_name}: {point} - {str(e)}")
    
    def _check_decision_tree(self, current_values):
        """Use decision tree to check if current values are normal"""
        if self.decision_tree is None or self.feature_names is None:
            return True
        
        try:
            # Create input array matching training data format
            input_data = []
            for feature in self.feature_names:
                value = current_values.get(feature, None)
                if value is None:
                    logger.warning(f"Missing feature value: {feature}")
                    return True
                input_data.append(value)
            
            # Predict using decision tree
            prediction = self.decision_tree.predict([input_data])
            return bool(prediction[0])
            
        except Exception as e:
            logger.error(f"Decision tree prediction error: {str(e)}")
            return True
    
    def get_status(self, metric_name, value, all_current_values=None):
        """
        Get anomaly status using both ARIMA and decision tree
        Returns: dict with is_anomaly flag and deviation score
        """
        self._add_point(metric_name, value)
        detector = self._get_detector(metric_name)
        
        if len(detector['points']) < 3:
            return {'is_anomaly': False, 'deviation': None}
        
        try:
            data = np.array(detector['points'])
            last_point = data[-1]
            
            # ARIMA detection
            arima_anomaly = False
            if len(data) >= self.window_size:
                if not detector['is_stationary']:
                    data = self._difference_series(data)
                    if len(data) < 2:
                        return {'is_anomaly': False, 'deviation': None}
                
                try:
                    model = ARIMA(data[:-1], order=(1,1,1))
                    model_fit = model.fit()
                    forecast = model_fit.forecast(steps=1)
                    conf_int = model_fit.get_forecast(steps=1).conf_int(alpha=0.05)
                    
                    arima_anomaly = (last_point < conf_int.iloc[0, 0] or 
                                   last_point > conf_int.iloc[0, 1])
                except:
                    arima_anomaly = False
            
            # Decision tree detection
            tree_normal = True
            if all_current_values:
                tree_normal = self._check_decision_tree(all_current_values)
            
            # Calculate deviation
            if len(data) > 1:
                mean = np.mean(data[:-1])
                deviation = abs(last_point - mean) / mean if mean != 0 else 0
            else:
                deviation = None
            
            # Combine detections (anomaly if either method detects it)
            is_anomaly = arima_anomaly or not tree_normal
            
            if is_anomaly:
                try:
                    response = requests.get(
                        self.api_url,
                        params={
                            "metric": metric_name,
                            "value": last_point,
                            "arima_anomaly": arima_anomaly,
                            "tree_normal": tree_normal,
                            "deviation": deviation
                        },
                        timeout=5
                    )
                    if response.status_code == 200:
                        return {
                            'is_anomaly': response.json().get("is_anomaly", False),
                            'deviation': deviation
                        }
                except requests.exceptions.RequestException:
                    pass
            
            return {
                'is_anomaly': is_anomaly,
                'deviation': deviation
            }
            
        except Exception as e:
            logger.error(f"Detection error for {metric_name}: {str(e)}")
            return {'is_anomaly': False, 'deviation': None}
    
    def get_points(self, metric_name):
        """Return current points for a specific metric"""
        detector = self._get_detector(metric_name)
        return list(detector['points'])
