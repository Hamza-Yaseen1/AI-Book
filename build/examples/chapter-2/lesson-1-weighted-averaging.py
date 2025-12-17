#!/usr/bin/env python3
"""
Lesson 1: Multi-Sensor Fusion and Data Integration
Example 1: Weighted Averaging Algorithm
"""

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

def main():
    print("Multi-Sensor Fusion with Weighted Averaging")
    print("===========================================")
    print("This example demonstrates how to combine readings from multiple sensors")
    print("using weighted averaging based on sensor reliability.\n")

    print("Equal weights fusion (all sensors treated equally):")
    print("-" * 50)
    for i in range(5):
        readings = simulate_sensor_readings()
        fused = simple_sensor_fusion(readings)
        print(f"Cycle {i+1}: Readings: {[round(r, 2) for r in readings]}, Fused: {round(fused, 2)}°C")
        time.sleep(0.1)

    print("\nWeighted fusion (first sensor more reliable):")
    print("-" * 50)
    for i in range(5):
        readings = simulate_sensor_readings()
        weights = [0.5, 0.3, 0.2]  # First sensor has higher weight
        fused = simple_sensor_fusion(readings, weights)
        print(f"Cycle {i+1}: Readings: {[round(r, 2) for r in readings]}, Fused: {round(fused, 2)}°C")
        time.sleep(0.1)

    print("\nComparison of approaches:")
    print("-" * 50)
    print("Equal weights: Each sensor contributes equally to the final result")
    print("Weighted fusion: More reliable sensors contribute more to the final result")
    print("This approach improves accuracy when sensor quality varies")

if __name__ == "__main__":
    main()