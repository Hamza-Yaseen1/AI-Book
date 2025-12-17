#!/usr/bin/env python3
"""
Advanced Adaptive Physical AI System
Lesson 3: Advanced Physical AI Concepts

This example demonstrates an advanced Physical AI system with machine learning
integration, adaptive behavior, and safety mechanisms.
"""

import time
import random
import csv
from datetime import datetime
from collections import deque
import statistics

class AdaptivePhysicalAISystem:
    def __init__(self):
        # System parameters
        self.sensors = ['temperature', 'humidity', 'light', 'motion']
        self.sensor_data_history = deque(maxlen=100)  # Keep last 100 readings
        self.actions_history = deque(maxlen=100)
        self.learning_enabled = True

        # Safety parameters
        self.emergency_thresholds = {
            'temperature': (0, 50),  # Safe range: 0-50°C
            'humidity': (0, 100),    # Safe range: 0-100%
            'light': (0, 1000),      # Safe range: 0-1000 lux
            'motion': (0, 1)         # Safe range: 0-1 (binary)
        }

        # Adaptive thresholds (will be adjusted based on learning)
        self.adaptive_thresholds = {
            'temperature': (18, 25),
            'humidity': (30, 70),
            'light': (100, 500),
            'motion': (0, 1)
        }

        # Performance metrics
        self.performance_score = 0.0
        self.total_decisions = 0

    def read_all_sensors(self):
        """Simulate reading from multiple sensors"""
        sensor_values = {}

        # Simulate realistic sensor data with some correlation
        base_temp = 22.0 + random.uniform(-2, 2)
        sensor_values['temperature'] = round(base_temp + random.uniform(-3, 3), 2)

        # Humidity tends to be inversely related to temperature
        base_humidity = 50 - (sensor_values['temperature'] - 22) * 2
        sensor_values['humidity'] = max(20, min(80, round(base_humidity + random.uniform(-10, 10), 2)))

        # Light level (0-1000 lux)
        sensor_values['light'] = round(random.uniform(50, 800), 2)

        # Motion (binary: 0 or 1)
        sensor_values['motion'] = 1 if random.random() > 0.7 else 0

        return sensor_values

    def validate_sensor_data(self, sensor_values):
        """Validate sensor data against safety thresholds"""
        for sensor, value in sensor_values.items():
            min_val, max_val = self.emergency_thresholds[sensor]

            if sensor == 'motion':
                # Motion is binary
                if value not in [0, 1]:
                    return False, f"Invalid motion value: {value}"
            else:
                if not (min_val <= value <= max_val):
                    return False, f"{sensor} value {value} outside safe range [{min_val}, {max_val}]"

        return True, "Valid"

    def make_adaptive_decision(self, sensor_values):
        """Make decision based on current sensor values and adaptive thresholds"""
        actions = []

        for sensor, value in sensor_values.items():
            if sensor == 'motion':
                # Special handling for binary sensor
                if value == 1:
                    actions.append(f"Motion detected - increase monitoring")
                continue

            min_thresh, max_thresh = self.adaptive_thresholds[sensor]

            if value < min_thresh:
                actions.append(f"{sensor} low: {value} < {min_thresh}")
            elif value > max_thresh:
                actions.append(f"{sensor} high: {value} > {max_thresh}")
            else:
                actions.append(f"{sensor} normal: {value}")

        # Determine primary action based on most critical readings
        critical_actions = [a for a in actions if 'high' in a or 'low' in a]

        if critical_actions:
            primary_action = "WARNING"
            details = ", ".join(critical_actions)
        else:
            primary_action = "NORMAL"
            details = "All sensors within adaptive thresholds"

        return primary_action, details

    def update_adaptive_thresholds(self):
        """Update thresholds based on historical data"""
        if len(self.sensor_data_history) < 10:
            return  # Not enough data to adapt

        # Calculate new thresholds based on historical data
        for sensor in self.sensors:
            if sensor == 'motion':
                continue  # Skip binary sensor

            values = [entry[sensor] for entry in self.sensor_data_history if sensor in entry]
            if not values:
                continue

            # Calculate percentiles for adaptive thresholds
            values.sort()
            p25 = values[int(0.25 * len(values))]
            p75 = values[int(0.75 * len(values))]

            # Set adaptive thresholds (interquartile range with some buffer)
            buffer = (p75 - p25) * 0.1  # 10% buffer
            self.adaptive_thresholds[sensor] = (round(p25 - buffer, 2), round(p75 + buffer, 2))

    def execute_action_safely(self, action, details):
        """Execute action with safety checks"""
        try:
            # Safety check: ensure action is valid
            valid_actions = ['NORMAL', 'WARNING', 'EMERGENCY', 'COOLING', 'HEATING', 'LIGHT_ON', 'LIGHT_OFF']
            if action not in valid_actions:
                raise ValueError(f"Invalid action: {action}")

            # Log the action
            action_record = {
                'timestamp': datetime.now(),
                'action': action,
                'details': details,
                'safety_status': 'OK'
            }

            self.actions_history.append(action_record)

            # Update performance metrics
            self.total_decisions += 1
            if action == 'NORMAL':
                # Normal actions indicate good system performance
                self.performance_score = min(1.0, self.performance_score + 0.01)
            else:
                # Non-normal actions reduce performance score
                self.performance_score = max(0.0, self.performance_score - 0.005)

            return action_record

        except Exception as e:
            # Safety fallback
            emergency_record = {
                'timestamp': datetime.now(),
                'action': 'EMERGENCY',
                'details': f'Safety fallback: {str(e)}',
                'safety_status': 'ERROR'
            }

            self.actions_history.append(emergency_record)
            return emergency_record

    def run_cycle(self):
        """Run one complete cycle of the adaptive Physical AI system"""
        # Sensing: Read all sensors
        sensor_values = self.read_all_sensors()

        # Safety validation
        is_valid, validation_msg = self.validate_sensor_data(sensor_values)
        if not is_valid:
            print(f"ERROR: {validation_msg}")
            # Execute emergency action
            return self.execute_action_safely('EMERGENCY', validation_msg)

        # Store sensor data for learning
        sensor_values['timestamp'] = datetime.now()
        self.sensor_data_history.append(sensor_values)

        # Processing: Make adaptive decision
        action, details = self.make_adaptive_decision(sensor_values)

        # Learning: Update adaptive thresholds periodically
        if len(self.sensor_data_history) % 5 == 0 and self.learning_enabled:
            self.update_adaptive_thresholds()

        # Actuation: Execute action safely
        action_record = self.execute_action_safely(action, details)

        # Display current state
        print(f"Time: {sensor_values['timestamp'].strftime('%H:%M:%S')}")
        print(f"Sensors: {dict((k, v) for k, v in sensor_values.items() if k != 'timestamp')}")
        print(f"Action: {action_record['action']}")
        print(f"Details: {action_record['details']}")
        print(f"Performance: {self.performance_score:.3f}")

        # Display adaptive thresholds
        print("Adaptive thresholds:", end=" ")
        for sensor, (min_val, max_val) in self.adaptive_thresholds.items():
            if sensor != 'motion':
                print(f"{sensor}({min_val},{max_val})", end=" ")
        print()

        print("-" * 70)

        return action_record

    def get_system_summary(self):
        """Get a summary of system performance"""
        return {
            'total_decisions': self.total_decisions,
            'performance_score': self.performance_score,
            'sensor_readings': len(self.sensor_data_history),
            'actions_taken': len(self.actions_history),
            'adaptive_learning': self.learning_enabled
        }

def main():
    print("Advanced Adaptive Physical AI System")
    print("Lesson 3: Advanced Physical AI Concepts")
    print("Simulating an advanced Physical AI system with ML integration...")
    print("Press Ctrl+C to stop")
    print()

    system = AdaptivePhysicalAISystem()

    try:
        cycle_count = 0
        while True:
            system.run_cycle()
            cycle_count += 1

            # Print summary every 10 cycles
            if cycle_count % 10 == 0:
                summary = system.get_system_summary()
                print(f"CYCLE {cycle_count} SUMMARY:")
                for key, value in summary.items():
                    print(f"  {key}: {value}")
                print()

            time.sleep(3)  # Wait 3 seconds before next cycle

    except KeyboardInterrupt:
        print("\nAdvanced Adaptive Physical AI System stopped.")
        print(f"Total cycles completed: {cycle_count}")

        summary = system.get_system_summary()
        print("\nFinal system summary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main()