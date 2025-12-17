#!/usr/bin/env python3
"""
Smart Temperature Monitor
Lesson 2: Building Your First Physical AI System

This example demonstrates a complete Physical AI system that monitors
temperature and takes appropriate actions based on the readings.
"""

import time
import random
from datetime import datetime

class TemperatureMonitor:
    def __init__(self):
        self.min_temp = 18.0  # Celsius
        self.max_temp = 25.0  # Celsius
        self.temp_history = []
        self.actions_log = []

    def read_temperature(self):
        """Simulate reading temperature from sensor"""
        # Add some variation to simulate real sensor data
        base_temp = 22.0  # Room temperature
        variation = random.uniform(-5.0, 5.0)
        temp = base_temp + variation
        return round(temp, 2)

    def determine_action(self, temperature):
        """Determine appropriate action based on temperature"""
        if temperature > self.max_temp:
            return "COOLING", "Temperature is too high"
        elif temperature < self.min_temp:
            return "HEATING", "Temperature is too low"
        else:
            return "NORMAL", "Temperature is in normal range"

    def execute_action(self, action, message):
        """Simulate executing an action"""
        print(f"Action: {action}")
        print(f"Message: {message}")

        # Log the action
        self.actions_log.append({
            'timestamp': datetime.now(),
            'action': action,
            'message': message
        })

    def log_temperature(self, temperature):
        """Log temperature reading"""
        self.temp_history.append({
            'timestamp': datetime.now(),
            'temperature': temperature
        })

        # Keep only the last 10 readings
        if len(self.temp_history) > 10:
            self.temp_history = self.temp_history[-10:]

    def get_system_status(self):
        """Get current system status summary"""
        if not self.temp_history:
            return "No data available"

        recent_temps = [entry['temperature'] for entry in self.temp_history[-5:]]
        avg_temp = sum(recent_temps) / len(recent_temps)

        return f"Average temp (last 5 readings): {avg_temp:.2f}°C"

    def run_cycle(self):
        """Run one complete cycle of the Physical AI system"""
        # Sensing: Read temperature
        temperature = self.read_temperature()
        print(f"Temperature reading: {temperature}°C")

        # Log the reading
        self.log_temperature(temperature)

        # Processing: Determine appropriate action
        action, message = self.determine_action(temperature)

        # Actuation: Execute the action
        self.execute_action(action, message)

        # Display system status
        status = self.get_system_status()
        print(f"System status: {status}")

        print("-" * 50)

def main():
    print("Smart Temperature Monitor - Physical AI System")
    print("Lesson 2: Building Your First Physical AI System")
    print("Simulating a complete Physical AI loop...")
    print("Press Ctrl+C to stop")
    print()

    monitor = TemperatureMonitor()

    try:
        cycle_count = 0
        while True:
            monitor.run_cycle()
            cycle_count += 1

            # Print summary every 5 cycles
            if cycle_count % 5 == 0:
                print(f"Summary: {len(monitor.actions_log)} actions taken")
                print()

            time.sleep(4)  # Wait 4 seconds before next cycle

    except KeyboardInterrupt:
        print("\nSmart Temperature Monitor stopped.")
        print(f"Total cycles completed: {cycle_count}")

        if monitor.actions_log:
            print(f"Total actions taken: {len(monitor.actions_log)}")
            print(f"Temperature readings logged: {len(monitor.temp_history)}")

if __name__ == "__main__":
    main()