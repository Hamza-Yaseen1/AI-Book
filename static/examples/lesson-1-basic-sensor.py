#!/usr/bin/env python3
"""
Basic Physical AI Sensor Example
Lesson 1: Introduction to Physical AI

This example demonstrates the fundamental concepts of Physical AI by
reading a sensor and making a simple decision based on the data.
"""

import time
import random

def simulate_sensor_reading():
    """Simulate a sensor reading (e.g., temperature, light, motion)"""
    # In a real implementation, this would read from actual hardware
    # For simulation, we'll generate a random value
    return random.uniform(15.0, 35.0)

def make_decision(sensor_value):
    """Make a simple decision based on sensor data"""
    if sensor_value > 25.0:
        return "HIGH"
    elif sensor_value < 20.0:
        return "LOW"
    else:
        return "NORMAL"

def execute_action(decision):
    """Simulate executing a physical action based on decision"""
    actions = {
        "HIGH": "Activating cooling system",
        "LOW": "Activating heating system",
        "NORMAL": "No action needed"
    }
    print(f"Action: {actions[decision]}")

def main():
    print("Physical AI System - Lesson 1 Example")
    print("Simulating a basic Physical AI loop...")
    print("Press Ctrl+C to stop")
    print()

    try:
        while True:
            # Sensing: Read from sensor
            sensor_value = simulate_sensor_reading()
            print(f"Sensor reading: {sensor_value:.2f}")

            # Processing: Make decision based on sensor data
            decision = make_decision(sensor_value)
            print(f"Decision: {decision}")

            # Actuation: Execute action based on decision
            execute_action(decision)

            print("-" * 40)
            time.sleep(3)  # Wait 3 seconds before next reading

    except KeyboardInterrupt:
        print("\nPhysical AI system stopped.")

if __name__ == "__main__":
    main()