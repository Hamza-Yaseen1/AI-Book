#!/usr/bin/env python3
"""
Lesson 2: Advanced Control Systems and Feedback Loops
Example 4: Safety-Enhanced PID Controller
"""

import time
import random
import matplotlib.pyplot as plt
import numpy as np
from enum import Enum

class SafetyLevel(Enum):
    NORMAL = 1
    WARNING = 2
    EMERGENCY = 3

class SafetyEnhancedPID:
    """
    A PID controller with comprehensive safety features
    """
    def __init__(self, kp, ki, kd, setpoint=0):
        # PID parameters
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint

        # Internal variables
        self.previous_error = 0
        self.integral = 0
        self.derivative = 0

        # Safety parameters
        self.max_output = 100
        self.min_output = 0
        self.max_rate_of_change = 10  # Max change per second
        self.last_output = 0
        self.last_update_time = time.time()

        # Safety limits
        self.safety_limits = {
            'upper_process_limit': float('inf'),
            'lower_process_limit': float('-inf'),
            'upper_output_limit': 100,
            'lower_output_limit': 0,
            'max_error_threshold': float('inf')
        }

        # Safety monitoring
        self.error_history = []
        self.output_history = []
        self.safety_events = []
        self.current_safety_level = SafetyLevel.NORMAL

    def compute(self, current_value, dt=1.0):
        """
        Compute PID output with safety checks

        Args:
            current_value: Current measured value
            dt: Time step in seconds

        Returns:
            Control output (with safety limits applied)
        """
        current_time = time.time()

        # Check process limits
        if not self._check_process_limits(current_value):
            return self._handle_emergency_stop("Process limit exceeded")

        # Calculate error
        error = self.setpoint - current_value
        self.error_history.append(error)

        # Check error threshold
        if abs(error) > self.safety_limits['max_error_threshold']:
            return self._handle_warning("Error threshold exceeded")

        # Calculate PID terms
        p_term = self.kp * error

        # Integral term with anti-windup
        self.integral += error * dt
        # Apply output limits to integral term to prevent windup
        self.integral = max(min(self.integral, 100), -100)
        i_term = self.ki * self.integral

        # Derivative term
        if dt > 0:
            self.derivative = (error - self.previous_error) / dt
        else:
            self.derivative = 0
        d_term = self.kd * self.derivative

        # Calculate raw output
        raw_output = p_term + i_term + d_term

        # Apply output limits
        limited_output = max(
            self.safety_limits['lower_output_limit'],
            min(self.safety_limits['upper_output_limit'], raw_output)
        )

        # Rate limiting to prevent sudden changes
        time_diff = current_time - self.last_update_time if self.last_update_time else dt
        if time_diff > 0:
            max_change = self.max_rate_of_change * time_diff
            limited_output = max(
                self.last_output - max_change,
                min(self.last_output + max_change, limited_output)
            )
        self.last_update_time = current_time

        # Final safety check
        final_output = max(self.min_output, min(self.max_output, limited_output))

        # Update internal values
        self.previous_error = error
        self.last_output = final_output
        self.output_history.append(final_output)

        # Update safety level
        self._update_safety_level()

        return final_output

    def _check_process_limits(self, current_value):
        """Check if process value is within safe limits"""
        return (
            self.safety_limits['lower_process_limit'] <=
            current_value <=
            self.safety_limits['upper_process_limit']
        )

    def _handle_emergency_stop(self, reason):
        """Handle emergency stop situation"""
        self.safety_events.append({
            'time': time.time(),
            'level': SafetyLevel.EMERGENCY,
            'reason': reason
        })
        self.current_safety_level = SafetyLevel.EMERGENCY
        self._reset_integral()
        return 0  # Return safe zero output

    def _handle_warning(self, reason):
        """Handle warning situation"""
        self.safety_events.append({
            'time': time.time(),
            'level': SafetyLevel.WARNING,
            'reason': reason
        })
        self.current_safety_level = SafetyLevel.WARNING
        # Reduce output rather than stopping completely
        return max(0, self.last_output * 0.5)

    def _update_safety_level(self):
        """Update safety level based on current conditions"""
        if self.current_safety_level == SafetyLevel.EMERGENCY:
            return  # Stay in emergency until manually reset

        # Check if conditions have improved
        if len(self.error_history) > 0:
            current_error = abs(self.error_history[-1])
            if current_error < self.safety_limits['max_error_threshold'] * 0.5:
                self.current_safety_level = SafetyLevel.NORMAL

    def _reset_integral(self):
        """Reset integral term (for emergency situations)"""
        self.integral = 0

    def set_safety_limits(self, **kwargs):
        """
        Set safety limits

        Args:
            upper_process_limit: Upper limit for process variable
            lower_process_limit: Lower limit for process variable
            upper_output_limit: Upper limit for controller output
            lower_output_limit: Lower limit for controller output
            max_error_threshold: Maximum allowable error
        """
        for key, value in kwargs.items():
            if key in self.safety_limits:
                self.safety_limits[key] = value

    def set_rate_limit(self, max_rate):
        """Set maximum rate of change for output"""
        self.max_rate_of_change = max_rate

    def get_safety_status(self):
        """Get current safety status"""
        return {
            'current_level': self.current_safety_level,
            'error_count': len(self.error_history),
            'output_count': len(self.output_history),
            'event_count': len(self.safety_events),
            'last_event': self.safety_events[-1] if self.safety_events else None
        }

    def reset_safety(self):
        """Reset safety status after emergency"""
        self.current_safety_level = SafetyLevel.NORMAL
        self.safety_events.clear()

class SafeTemperatureControl:
    """
    A safe temperature control system using the safety-enhanced PID
    """
    def __init__(self, initial_temp=20.0):
        # Initialize safety-enhanced PID controller
        self.pid = SafetyEnhancedPID(kp=2.0, ki=0.1, kd=0.05, setpoint=25.0)

        # Set safety limits for temperature control
        self.pid.set_safety_limits(
            upper_process_limit=75.0,  # Max safe temperature
            lower_process_limit=0.0,   # Min safe temperature
            max_error_threshold=10.0   # Max allowable error
        )

        self.current_temp = initial_temp
        self.heat_output = 0
        self.is_operational = True

        # System characteristics
        self.thermal_mass = 5.0
        self.heat_loss_rate = 0.1
        self.max_power = 100

    def update(self, dt=0.1):
        """Update the safe temperature control system"""
        if not self.is_operational:
            return self.current_temp, 0

        # Get PID output with safety checks
        control_signal = self.pid.compute(self.current_temp, dt)

        # Check safety status
        status = self.pid.get_safety_status()
        if status['current_level'] == SafetyLevel.EMERGENCY:
            self.is_operational = False
            print("EMERGENCY: Temperature control system shut down!")

        # Apply limits to heating output
        self.heat_output = max(0, min(self.max_power, control_signal))

        # Simulate temperature change
        heating_effect = (self.heat_output / 100.0) * 2.0 * dt
        cooling_effect = (self.current_temp - 20.0) * self.heat_loss_rate * dt

        # Update temperature with noise
        temp_change = heating_effect - cooling_effect + random.uniform(-0.1, 0.1) * dt
        self.current_temp += temp_change / self.thermal_mass

        return self.current_temp, self.heat_output

    def introduce_fault(self):
        """Introduce a fault condition for testing"""
        # Simulate a sensor fault that causes a sudden temperature reading
        self.current_temp = 80.0  # Very high temperature reading
        print("FAULT: Simulated temperature sensor fault - very high reading")

def run_safety_enhanced_simulation():
    """
    Run the safety-enhanced PID simulation
    """
    print("Safety-Enhanced PID Controller Simulation")
    print("=========================================")
    print("This example demonstrates a PID controller with comprehensive safety features")
    print("including limits, rate limiting, and emergency handling.\n")

    system = SafeTemperatureControl(initial_temp=20.0)

    print("System initialized with safety limits:")
    print("- Max safe temperature: 75°C")
    print("- Min safe temperature: 0°C")
    print("- Max allowable error: 10°C")
    print("- Max output rate of change: 10 units/s\n")

    print("Time(s)\tTemp(°C)\tOutput(%)\tSafety Level")
    print("-" * 50)

    for i in range(150):
        current_time = i * 0.1

        # Introduce a fault at specific time to test safety system
        if i == 50:
            print("\nINTRODUCING FAULT AT t=5.0s:")
            system.introduce_fault()

        temp, output = system.update(dt=0.1)

        # Get safety status
        status = system.pid.get_safety_status()

        # Print status every 10 steps
        if i % 10 == 0:
            print(f"{current_time:5.1f}\t{temp:6.2f}\t{output:8.2f}\t{status['current_level'].name}")

        time.sleep(0.001)

    final_status = system.pid.get_safety_status()
    print(f"\nFinal Safety Status:")
    print(f"- Current safety level: {final_status['current_level'].name}")
    print(f"- Total safety events: {final_status['event_count']}")
    print(f"- System operational: {system.is_operational}")
    print(f"- Final temperature: {system.current_temp:.2f}°C")

    print(f"\nSafety Features Demonstrated:")
    print(f"- Process variable limits (0-75°C)")
    print(f"- Error threshold protection (10°C)")
    print(f"- Rate limiting to prevent sudden changes")
    print(f"- Emergency shutdown on critical faults")
    print(f"- Warning system for approaching limits")

def main():
    run_safety_enhanced_simulation()

if __name__ == "__main__":
    main()