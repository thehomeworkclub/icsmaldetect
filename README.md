## ICS Malware Detection based on ANIMA for anomaly detection

**ICS Malware Detector** is a tool designed during the Crack The Code 2025 Concordia Hackathon to enhance the security of Industrial Control Systems (ICS) through advanced anomaly detection. By leveraging ARIMA (AutoRegressive Integrated Moving Average) models and machine learning, we provide real-time monitoring and detection of potential cyber attacks targeting critical infrastructure components.

**Our Mission:** To protect Industrial Control Systems from cyber attacks by detecting anomalous behavior patterns in system metrics and providing early warning of potential security breaches.

## The Problem

Industrial Control Systems face significant security challenges due to their critical nature and potential vulnerability to cyber attacks. Traditional signature-based detection methods often fail to identify novel attacks or subtle manipulations of system parameters. This is particularly evident in 24hr running systems like centrifuge controls in stuxnet attack, which our project and demo are based around.

ICS Malware Detector tackles this challenge through a multi-layered approach:

- **Time Series Analysis:** Using ARIMA models to detect anomalies in metric patterns
- **Machine Learning:** Employing decision trees to identify abnormal system states
- **Real-time Monitoring:** Continuous tracking of critical system parameters via Grafana panel

## Features

- **Advanced Anomaly Detection:** Combines ARIMA time-series analysis with machine learning to detect suspicious patterns in system metrics.
- **Real-time Monitoring:** Continuously monitors critical ICS parameters including:
  - Centrifuge rotation speed (RPM)
  - Vibration amplitude (mm/s)
  - Temperature (Celsius)
  - Process gas pressure (kPa)
  - Gas flow rate (g^3/min)
  - Operating voltage (V)
  - Operating current (A)
- **Attack Simulation:** Built-in capability to simulate various types of attacks:
  - Gradual parameter manipulation
  - Oscillating value attacks
  - Sudden system changes
- **Prometheus Integration:** Native support for Prometheus metrics collection and monitoring.
- **Grafana Dashboards:** Pre-configured visualization of system metrics and attack detection.
- **Extensible Architecture:** Easy integration with existing ICS monitoring systems.

## How It Works

The system operates through multiple coordinated components:

1. **Metric Collection:** Continuous monitoring of critical ICS parameters through Prometheus.
2. **Anomaly Detection:** 
   - ARIMA models analyze time-series patterns
   - Decision trees evaluate overall system state
   - Combined analysis for robust detection
3. **Alert Generation:** Real-time alerts when anomalies are detected.
4. **Visualization:** Grafana dashboards for monitoring system state and attack detection.

## Steps to Use

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Monitoring System:**
   - Launch the Prometheus server
   - Start the metrics collection service
   - Access the Grafana dashboard

3. **Configure Monitoring:**
   - Set up metric thresholds based on initial data points, continously updating.
   - Adjust detection sensitivity
   - Configure alert notifications

4. **Monitor and Respond:**
   - Attacks are detected and Orkes conductor is called
   - Conductor calls Twilio and email systems, notifying of potential attack

## Troubleshooting Guidance

- **False Positives:** Adjust detection thresholds in the ARIMA model parameters
- **Missing Data:** Check Prometheus endpoint connectivity
- **Performance Issues:** Monitor system resource usage and adjust collection intervals
- **Alert Delays:** Verify network connectivity and alert configuration, unless you opt to use Orkes OSS. Current implementation relies on Orkes cloud workflow.

## Technical Details

The system utilizes several key technologies:

- **ARIMA Models:** For time-series analysis of system metrics
- **Decision Trees:** For machine learning-based anomaly detection
- **Prometheus:** For metrics collection and storage
- **Grafana:** For visualization and alerting
- **Python:** Core implementation language with key libraries:
  - prometheus_client (≥0.16.0)
  - numpy (≥1.24.0)
  - statsmodels (≥0.14.0)
  - requests (≥2.31.0)
- **Orkes Condutor:** For alerting cybersecurity professionals following detecting attacks.

## Contributing

This is an open-source project, and we welcome contributions from the cybersecurity and ICS community. Key areas for contribution include:

- Additional attack detection methods
- New metric monitoring capabilities
- Improved visualization components
- Documentation and examples

## Contact

For questions, contributions, or security concerns, please open an issue in the GitHub repository.