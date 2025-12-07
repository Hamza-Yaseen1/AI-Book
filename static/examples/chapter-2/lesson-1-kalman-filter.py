#!/usr/bin/env python3
"""
Lesson 1: Multi-Sensor Fusion and Data Integration
Example 2: Simple Kalman Filter Implementation
"""

import numpy as np
import time
import random

class SimpleKalmanFilter:
    """
    A simplified Kalman filter implementation for sensor fusion
    """
    def __init__(self, initial_estimate=0, initial_error=1, process_error=0.1, measurement_error=0.1):
        """
        Initialize the Kalman filter

        Args:
            initial_estimate: Initial estimate of the value
            initial_error: Initial uncertainty in the estimate
            process_error: Uncertainty in the process model
            measurement_error: Uncertainty in the measurements
        """
        self.estimate = initial_estimate
        self.error = initial_error
        self.process_error = process_error
        self.measurement_error = measurement_error

    def update(self, measurement):
        """
        Update the estimate based on a new measurement

        Args:
            measurement: New sensor measurement

        Returns:
            Updated estimate
        """
        # Prediction step
        prediction = self.estimate  # In this simple case, prediction is the same as estimate
        prediction_error = self.error + self.process_error

        # Update step - calculate Kalman gain
        kalman_gain = prediction_error / (prediction_error + self.measurement_error)

        # Update estimate with measurement
        self.estimate = prediction + kalman_gain * (measurement - prediction)

        # Update error estimate
        self.error = (1 - kalman_gain) * prediction_error

        return self.estimate

def main():
    print("Simple Kalman Filter for Sensor Fusion")
    print("======================================")
    print("This example demonstrates a simplified Kalman filter that")
    print("smooths noisy sensor readings to provide more accurate estimates.\n")

    # Create a Kalman filter instance
    kf = SimpleKalmanFilter(initial_estimate=22.0, initial_error=1.0)
    base_temp = 22.5

    print("Simulating noisy temperature sensor readings with Kalman filtering:")
    print("-" * 65)
    print(f"{'Cycle':<6} {'Raw Reading':<12} {'Filtered':<12} {'Error Reduction':<15}")
    print("-" * 65)

    for i in range(15):
        # Simulate noisy sensor reading
        noisy_reading = base_temp + random.uniform(-0.8, 0.8)
        filtered_reading = kf.update(noisy_reading)

        # Calculate how much the filter reduced the error
        error_reduction = abs(noisy_reading - base_temp) - abs(filtered_reading - base_temp)

        print(f"{i+1:<6} {noisy_reading:<12.2f} {filtered_reading:<12.2f} {error_reduction:<15.2f}")
        time.sleep(0.05)  # Small delay to simulate real-time readings

    print("\nBenefits of Kalman Filtering:")
    print("- Smooths out noisy measurements")
    print("- Provides more accurate estimates over time")
    print("- Adapts to changing conditions")
    print("- Reduces the impact of sensor noise")

if __name__ == "__main__":
    main()