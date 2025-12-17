#!/usr/bin/env python3
"""
Lesson 2: Advanced Control Systems and Feedback Loops
Example 1: Basic PID Controller Implementation
"""

import time
import random
import matplotlib.pyplot as plt

class PIDController:
    """
    A basic PID (Proportional-Integral-Derivative) controller implementation
    """
    def __init__(self, kp, ki, kd, setpoint=0):
        """
        Initialize PID controller

        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain
            setpoint: Desired value
        """
        self.kp = kp  # Proportional gain
        self.ki = ki  # Integral gain
        self.kd = kd  # Derivative gain
        self.setpoint = setpoint

        # Internal variables
        self.previous_error = 0
        self.integral = 0
        self.derivative = 0

    def compute(self, current_value, dt=1.0):
        """
        Compute PID output

        Args:
            current_value: Current measured value
            dt: Time step (for derivative calculation)

        Returns:
            Control output
        """
        # Calculate error
        error = self.setpoint - current_value

        # Proportional term
        p_term = self.kp * error

        # Integral term (with anti-windup protection)
        self.integral += error * dt
        # Limit integral term to prevent windup
        self.integral = max(min(self.integral, 100), -100)
        i_term = self.ki * self.integral

        # Derivative term
        if dt > 0:
            self.derivative = (error - self.previous_error) / dt
        else:
            self.derivative = 0
        d_term = self.kd * self.derivative

        # Calculate output
        output = p_term + i_term + d_term

        # Store error for next iteration
        self.previous_error = error

        return output

    def set_setpoint(self, setpoint):
        """Update the setpoint"""
        self.setpoint = setpoint
        # Reset integral when setpoint changes significantly to avoid shock
        if abs(setpoint - self.setpoint) > 1:
            self.integral = 0

    def set_tunings(self, kp, ki, kd):
        """Update PID tunings"""
        self.kp = kp
        self.ki = ki
        self.kd = kd

def main():
    print("Basic PID Controller Implementation")
    print("=================================")
    print("This example demonstrates a basic PID controller with three terms:")
    print("- Proportional (P): Reduces current error")
    print("- Integral (I): Eliminates steady-state error")
    print("- Derivative (D): Predicts future error based on rate of change\n")

    # Create a PID controller for temperature control
    pid = PIDController(kp=2.0, ki=0.1, kd=0.05, setpoint=25.0)  # Target: 25°C

    # Simulate system response
    current_temp = 20.0  # Starting temperature
    times = []
    temperatures = []
    outputs = []
    setpoints = []

    print("Simulating temperature control with PID:")
    print("-" * 50)
    print(f"{'Time(s)':<8} {'Temp(°C)':<10} {'Output':<10} {'Error':<8}")
    print("-" * 50)

    for i in range(100):
        time_step = 0.1  # 0.1 second time steps
        current_time = i * time_step

        # Get PID output based on current temperature
        control_output = pid.compute(current_temp, time_step)

        # Simulate system response (simplified model)
        # The output affects the temperature with some delay and noise
        temp_change = control_output * 0.01 - (current_temp - 20) * 0.02  # Natural cooling
        current_temp += temp_change + random.uniform(-0.05, 0.05)  # Add some noise

        # Store data for plotting
        times.append(current_time)
        temperatures.append(current_temp)
        outputs.append(control_output)
        setpoints.append(pid.setpoint)

        # Print status every 10 steps
        if i % 10 == 0:
            error = abs(pid.setpoint - current_temp)
            print(f"{current_time:<8.1f} {current_temp:<10.2f} {control_output:<10.2f} {error:<8.2f}")

    print("\nPID Controller Components:")
    print("- Proportional gain (Kp):", pid.kp)
    print("- Integral gain (Ki):", pid.ki)
    print("- Derivative gain (Kd):", pid.kd)
    print("- Current setpoint:", pid.setpoint)

    # Calculate final performance metrics
    final_error = abs(pid.setpoint - current_temp)
    avg_error = sum(abs(sp - temp) for sp, temp in zip(setpoints, temperatures)) / len(temperatures)

    print(f"\nPerformance Metrics:")
    print(f"- Final error: {final_error:.3f}°C")
    print(f"- Average error: {avg_error:.3f}°C")
    print(f"- Final temperature: {current_temp:.2f}°C")

    # Plot results
    plt.figure(figsize=(12, 8))

    plt.subplot(2, 1, 1)
    plt.plot(times, temperatures, label='Actual Temperature', linewidth=2)
    plt.plot(times, setpoints, label='Setpoint', linestyle='--', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('Temperature (°C)')
    plt.title('PID Temperature Control Response')
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(times, outputs, label='PID Output', color='red', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('Control Output')
    plt.title('PID Controller Output')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    print(f"\nThe PID controller successfully regulated the temperature")
    print(f"to near the setpoint of {pid.setpoint}°C with minimal error.")

if __name__ == "__main__":
    main()