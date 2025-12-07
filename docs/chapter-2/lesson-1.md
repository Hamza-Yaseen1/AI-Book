---
sidebar_position: 1
---

# Lesson 1: Multi-Sensor Fusion and Data Integration

## Learning Objectives

- Understand the principles of sensor fusion and why it's important
- Implement weighted averaging algorithms for sensor data
- Apply simple Kalman filtering concepts to sensor data
- Create a robust Physical AI system using multiple sensors
- Evaluate the quality and reliability of fused sensor data

## Prerequisites

Before starting this lesson, you should:
- Have completed Chapter 1 of this book
- Understand basic sensor reading and data processing concepts
- Be familiar with Python programming
- Have basic knowledge of data processing and statistics

## Introduction to Sensor Fusion

Sensor fusion is the process of combining data from multiple sensors to achieve better accuracy and reliability than could be achieved by using a single sensor alone. In Physical AI systems, sensor fusion is crucial for creating robust systems that can operate effectively in complex environments.

### Why Sensor Fusion?

1. **Improved Accuracy**: Combining multiple sensors can provide more accurate measurements
2. **Increased Reliability**: If one sensor fails, others can still provide data
3. **Enhanced Coverage**: Different sensors can detect different aspects of the environment
4. **Reduced Uncertainty**: Combining data from multiple sources reduces overall uncertainty

## Weighted Averaging Approach

The simplest form of sensor fusion is weighted averaging, where each sensor reading is assigned a weight based on its reliability or accuracy.

### Implementation

Let's implement a basic sensor fusion algorithm using weighted averaging:

```python
import numpy as np
import time
import random

def simple_sensor_fusion(temperature_sensors, weights=None):
    """
    Combine readings from multiple temperature sensors
    using weighted averaging
    """
    readings = np.array(temperature_sensors)

    if weights is None:
        # Equal weights if none provided
        weights = np.ones(len(readings)) / len(readings)
    else:
        weights = np.array(weights)

    # Normalize weights to sum to 1
    weights = weights / np.sum(weights)

    # Calculate weighted average
    fused_reading = np.average(readings, weights=weights)
    return fused_reading

def simulate_sensor_readings():
    """Simulate readings from multiple sensors with slight variations"""
    base_temp = 22.5  # Base temperature
    return [
        base_temp + random.uniform(-0.2, 0.2),  # Sensor 1 (high reliability)
        base_temp + random.uniform(-0.3, 0.3),  # Sensor 2 (medium reliability)
        base_temp + random.uniform(-0.5, 0.5)   # Sensor 3 (lower reliability)
    ]

# Example usage with equal weights
print("Equal weights fusion:")
for i in range(5):
    readings = simulate_sensor_readings()
    fused = simple_sensor_fusion(readings)
    print(f"Readings: {[round(r, 2) for r in readings]}, Fused: {round(fused, 2)}°C")
    time.sleep(0.1)

print("\nWeighted fusion (first sensor more reliable):")
for i in range(5):
    readings = simulate_sensor_readings()
    weights = [0.5, 0.3, 0.2]  # First sensor has higher weight
    fused = simple_sensor_fusion(readings, weights)
    print(f"Readings: {[round(r, 2) for r in readings]}, Fused: {round(fused, 2)}°C")
    time.sleep(0.1)
```

## Kalman Filter Approach

For more advanced sensor fusion, we can use a simplified Kalman filter approach. The Kalman filter is an optimal estimator that uses a series of measurements observed over time to estimate unknown variables.

### Implementation

```python
class SimpleKalmanFilter:
    def __init__(self, initial_estimate=0, initial_error=1, process_error=0.1, measurement_error=0.1):
        self.estimate = initial_estimate
        self.error = initial_error
        self.process_error = process_error
        self.measurement_error = measurement_error

    def update(self, measurement):
        # Prediction step
        prediction = self.estimate  # In this simple case, prediction is the same as estimate
        prediction_error = self.error + self.process_error

        # Update step
        kalman_gain = prediction_error / (prediction_error + self.measurement_error)
        self.estimate = prediction + kalman_gain * (measurement - prediction)
        self.error = (1 - kalman_gain) * prediction_error

        return self.estimate

# Example usage
print("\nKalman Filter approach:")
kf = SimpleKalmanFilter(initial_estimate=22.0, initial_error=1.0)
base_temp = 22.5

for i in range(10):
    # Simulate noisy sensor reading
    noisy_reading = base_temp + random.uniform(-0.8, 0.8)
    filtered_reading = kf.update(noisy_reading)
    print(f"Raw: {noisy_reading:.2f}°C, Filtered: {filtered_reading:.2f}°C")
    time.sleep(0.1)
```

## Practical Project: Multi-Sensor Environmental Monitoring

Let's create a practical project that combines multiple sensors to create a robust environmental monitoring system.

### Required Materials
- Raspberry Pi (with GPIO pins)
- Multiple temperature sensors (2-3 DS18B20 or DHT22)
- Humidity sensor (DHT22 or similar)
- Light sensor (photoresistor with ADC)
- Breadboard and jumper wires

### Implementation

```python
# physical-ai/static/examples/chapter-2/lesson-1-environmental-monitor.py
import numpy as np
import time
import random
from datetime import datetime

class MultiSensorFusion:
    def __init__(self):
        self.sensor_weights = {
            'temperature': [0.4, 0.4, 0.2],  # 3 temp sensors, first 2 more reliable
            'humidity': [0.6, 0.4]          # 2 humidity sensors, first more reliable
        }
        self.confidence_threshold = 0.7
        self.data_history = {'temperature': [], 'humidity': [], 'light': []}

    def fuse_temperature_data(self, readings):
        """Fuse temperature data from multiple sensors"""
        if len(readings) != len(self.sensor_weights['temperature']):
            raise ValueError("Number of readings doesn't match number of weights")

        weights = np.array(self.sensor_weights['temperature'])
        readings_array = np.array(readings)

        # Normalize weights
        weights = weights / np.sum(weights)

        # Calculate weighted average
        fused_temp = np.average(readings_array, weights=weights)

        # Calculate confidence based on sensor agreement
        variance = np.var(readings_array)
        confidence = max(0, 1 - variance)  # Simple confidence metric

        return fused_temp, confidence

    def fuse_humidity_data(self, readings):
        """Fuse humidity data from multiple sensors"""
        if len(readings) != len(self.sensor_weights['humidity']):
            raise ValueError("Number of readings doesn't match number of weights")

        weights = np.array(self.sensor_weights['humidity'])
        readings_array = np.array(readings)

        # Normalize weights
        weights = weights / np.sum(weights)

        # Calculate weighted average
        fused_humidity = np.average(readings_array, weights=weights)

        # Calculate confidence based on sensor agreement
        variance = np.var(readings_array)
        confidence = max(0, 1 - variance * 0.5)  # Adjusted for humidity

        return fused_humidity, confidence

    def detect_sensor_failure(self, readings, threshold=2.0):
        """Detect if any sensor is likely failing by comparing to others"""
        if len(readings) < 2:
            return [False] * len(readings)

        mean_val = np.mean(readings)
        deviations = [abs(r - mean_val) for r in readings]
        failures = [dev > threshold for dev in deviations]

        return failures

    def monitor_environment(self):
        """Simulate monitoring environment with sensor fusion"""
        print("Multi-Sensor Environmental Monitoring System")
        print("============================================")

        for cycle in range(10):
            # Simulate sensor readings (in a real system, these would come from actual sensors)
            temp_readings = [
                22.5 + random.uniform(-0.3, 0.3),  # Sensor 1
                22.7 + random.uniform(-0.4, 0.4),  # Sensor 2
                22.2 + random.uniform(-0.6, 0.6)   # Sensor 3
            ]

            humidity_readings = [
                45.0 + random.uniform(-2, 2),      # Sensor 1
                44.5 + random.uniform(-3, 3)       # Sensor 2
            ]

            light_reading = 300 + random.uniform(-50, 50)  # Light sensor reading

            # Check for sensor failures
            temp_failures = self.detect_sensor_failure(temp_readings)
            humidity_failures = self.detect_sensor_failure(humidity_readings)

            # Apply sensor fusion
            fused_temp, temp_confidence = self.fuse_temperature_data(temp_readings)
            fused_humidity, humidity_confidence = self.fuse_humidity_data(humidity_readings)

            # Display results
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] Cycle {cycle+1}")
            print(f"  Temperature readings: {[round(r, 2) for r in temp_readings]}")
            print(f"  Temperature failures: {temp_failures}")
            print(f"  Fused temperature: {round(fused_temp, 2)}°C (confidence: {round(temp_confidence, 2)})")

            print(f"  Humidity readings: {[round(r, 2) for r in humidity_readings]}")
            print(f"  Humidity failures: {humidity_failures}")
            print(f"  Fused humidity: {round(fused_humidity, 2)}% (confidence: {round(humidity_confidence, 2)})")

            print(f"  Light reading: {round(light_reading, 2)} lux")

            # Store in history
            self.data_history['temperature'].append(fused_temp)
            self.data_history['humidity'].append(fused_humidity)
            self.data_history['light'].append(light_reading)

            # Alert if confidence is low
            if temp_confidence < self.confidence_threshold:
                print("  ⚠️  Low confidence in temperature fusion - check sensors!")
            if humidity_confidence < self.confidence_threshold:
                print("  ⚠️  Low confidence in humidity fusion - check sensors!")

            time.sleep(1)  # Wait 1 second between readings

# Run the simulation
if __name__ == "__main__":
    monitor = MultiSensorFusion()
    monitor.monitor_environment()
```

## Safety Considerations

When implementing sensor fusion systems:

1. **Validation**: Always validate fused data against expected ranges
2. **Failure Detection**: Implement mechanisms to detect sensor failures
3. **Fallback Systems**: Have backup systems when sensor fusion fails
4. **Calibration**: Regularly calibrate sensors to maintain accuracy

## Exercises

1. **Basic Fusion**: Implement a sensor fusion system for pressure sensors
2. **Advanced Weighting**: Create a system that dynamically adjusts weights based on sensor performance
3. **Confidence Metrics**: Implement more sophisticated confidence metrics for fused data
4. **Sensor Diagnostics**: Add diagnostic capabilities to identify failing sensors

## Summary

In this lesson, we explored the fundamentals of sensor fusion, implementing both weighted averaging and simplified Kalman filter approaches. We created a practical multi-sensor environmental monitoring system that demonstrates the benefits of combining data from multiple sources.

Sensor fusion is a critical component of advanced Physical AI systems, providing increased accuracy, reliability, and robustness. The techniques learned in this lesson form the foundation for more complex Physical AI applications.

In the next lesson, we'll explore advanced control systems that use these fused sensor readings to make intelligent decisions and control physical systems.