#!/usr/bin/env python3
"""
Lesson 1: Multi-Sensor Fusion and Data Integration
Project: Multi-Sensor Environmental Monitoring System
"""

import numpy as np
import time
import random
from datetime import datetime

class MultiSensorFusion:
    """
    A class to implement multi-sensor fusion for environmental monitoring
    """
    def __init__(self):
        # Define sensor weights based on reliability
        self.sensor_weights = {
            'temperature': [0.4, 0.4, 0.2],  # 3 temp sensors, first 2 more reliable
            'humidity': [0.6, 0.4]          # 2 humidity sensors, first more reliable
        }
        self.confidence_threshold = 0.7
        self.data_history = {'temperature': [], 'humidity': [], 'light': []}
        self.sensor_failures = {'temperature': [False, False, False], 'humidity': [False, False]}

    def fuse_temperature_data(self, readings):
        """
        Fuse temperature data from multiple sensors using weighted averaging

        Args:
            readings: List of temperature readings from multiple sensors

        Returns:
            tuple: (fused_temperature, confidence)
        """
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
        """
        Fuse humidity data from multiple sensors using weighted averaging

        Args:
            readings: List of humidity readings from multiple sensors

        Returns:
            tuple: (fused_humidity, confidence)
        """
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
        """
        Detect if any sensor is likely failing by comparing to others

        Args:
            readings: List of sensor readings
            threshold: Threshold for detecting failures

        Returns:
            list: Boolean list indicating which sensors are failing
        """
        if len(readings) < 2:
            return [False] * len(readings)

        mean_val = np.mean(readings)
        deviations = [abs(r - mean_val) for r in readings]
        failures = [dev > threshold for dev in deviations]

        return failures

    def get_sensor_status(self):
        """
        Get current status of all sensors

        Returns:
            dict: Status information for all sensors
        """
        return {
            'temperature': self.sensor_failures['temperature'],
            'humidity': self.sensor_failures['humidity']
        }

    def monitor_environment(self, cycles=10):
        """
        Simulate monitoring environment with sensor fusion

        Args:
            cycles: Number of monitoring cycles to run
        """
        print("Multi-Sensor Environmental Monitoring System")
        print("============================================")
        print("This project demonstrates sensor fusion with failure detection")
        print("and confidence metrics for robust environmental monitoring.\n")

        for cycle in range(cycles):
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

            # Update failure tracking
            self.sensor_failures['temperature'] = temp_failures
            self.sensor_failures['humidity'] = humidity_failures

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

            # Alert if sensor failures detected
            if any(temp_failures):
                print("  ⚠️  Temperature sensor failure detected!")
            if any(humidity_failures):
                print("  ⚠️  Humidity sensor failure detected!")

            time.sleep(1)  # Wait 1 second between readings

        # Display summary statistics
        self.display_summary()

    def display_summary(self):
        """
        Display summary statistics for the monitoring session
        """
        print("\n" + "="*50)
        print("MONITORING SESSION SUMMARY")
        print("="*50)

        if self.data_history['temperature']:
            temp_data = np.array(self.data_history['temperature'])
            print(f"Temperature - Average: {temp_data.mean():.2f}°C, Range: {temp_data.min():.2f}°C - {temp_data.max():.2f}°C")

        if self.data_history['humidity']:
            humidity_data = np.array(self.data_history['humidity'])
            print(f"Humidity - Average: {humidity_data.mean():.2f}%, Range: {humidity_data.min():.2f}% - {humidity_data.max():.2f}%")

        if self.data_history['light']:
            light_data = np.array(self.data_history['light'])
            print(f"Light - Average: {light_data.mean():.2f} lux, Range: {light_data.min():.2f} - {light_data.max():.2f} lux")

        # Display sensor status summary
        sensor_status = self.get_sensor_status()
        print(f"\nSensor Status Summary:")
        for sensor_type, failures in sensor_status.items():
            failed_count = sum(failures)
            total_count = len(failures)
            print(f"  {sensor_type.capitalize()}: {failed_count}/{total_count} sensors failed")

def main():
    """
    Main function to run the multi-sensor environmental monitoring system
    """
    monitor = MultiSensorFusion()
    monitor.monitor_environment(cycles=10)  # Run for 10 cycles

if __name__ == "__main__":
    main()