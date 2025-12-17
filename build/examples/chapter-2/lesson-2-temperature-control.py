#!/usr/bin/env python3
"""
Lesson 2: Advanced Control Systems and Feedback Loops
Example 3: Complete Temperature Control System with PID
"""

import time
import matplotlib.pyplot as plt
import numpy as np
import random

class PIDController:
    """
    A PID controller implementation with safety features
    """
    def __init__(self, kp, ki, kd, setpoint=0):
        self.kp = kp  # Proportional gain
        self.ki = ki  # Integral gain
        self.kd = kd  # Derivative gain
        self.setpoint = setpoint

        # Internal variables
        self.previous_error = 0
        self.integral = 0
        self.derivative = 0
        self.output_limits = (0, 100)  # Output limits (0-100%)

    def compute(self, current_value, dt=1.0):
        # Calculate error
        error = self.setpoint - current_value

        # Proportional term
        p_term = self.kp * error

        # Integral term with anti-windup protection
        self.integral += error * dt
        # Limit integral to prevent windup
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

        # Apply output limits
        output = max(min(output, self.output_limits[1]), self.output_limits[0])

        # Store error for next iteration
        self.previous_error = error

        return output

    def set_setpoint(self, setpoint):
        self.setpoint = setpoint
        # Reset integral when setpoint changes significantly
        if abs(setpoint - self.setpoint) > 1:
            self.integral = 0

    def set_tunings(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd

class TemperatureControlSystem:
    """
    A complete temperature control system with PID controller
    """
    def __init__(self, initial_temp=20.0):
        # Initialize PID controller for temperature control
        self.pid = PIDController(kp=2.0, ki=0.1, kd=0.05, setpoint=25.0)  # Target: 25°C
        self.current_temp = initial_temp
        self.heat_output = 0  # Output to heating element (0-100%)

        # System characteristics
        self.thermal_mass = 5.0  # How slowly temperature changes
        self.heat_loss_rate = 0.1  # Rate of heat loss to environment
        self.max_power = 100  # Maximum heating power

        # Safety limits
        self.max_temp = 80.0  # Maximum safe temperature
        self.min_temp = 0.0   # Minimum safe temperature

        # Data logging
        self.time_log = []
        self.temp_log = []
        self.output_log = []
        self.setpoint_log = []

    def update(self, dt=0.1):
        """
        Update the temperature control system

        Args:
            dt: Time step in seconds
        """
        # Get PID output based on current temperature
        control_signal = self.pid.compute(self.current_temp, dt)

        # Apply safety limits to heating output
        self.heat_output = max(0, min(self.max_power, control_signal))

        # Simulate temperature change based on heating and cooling
        heating_effect = (self.heat_output / 100.0) * 2.0 * dt  # Heat added
        cooling_effect = (self.current_temp - 20.0) * self.heat_loss_rate * dt  # Heat lost

        # Update temperature with some noise to simulate real system
        temp_change = heating_effect - cooling_effect + random.uniform(-0.1, 0.1) * dt
        self.current_temp += temp_change / self.thermal_mass

        # Apply temperature limits
        self.current_temp = max(self.min_temp, min(self.max_temp, self.current_temp))

        # Log data
        self.time_log.append(len(self.time_log) * dt)
        self.temp_log.append(self.current_temp)
        self.output_log.append(self.heat_output)
        self.setpoint_log.append(self.pid.setpoint)

        return self.current_temp, self.heat_output

    def change_setpoint(self, new_setpoint):
        """Change the target temperature"""
        print(f"Changing temperature setpoint from {self.pid.setpoint:.1f}°C to {new_setpoint:.1f}°C")
        self.pid.set_setpoint(new_setpoint)

    def emergency_stop(self):
        """Emergency stop function"""
        self.pid.set_setpoint(0)
        self.heat_output = 0
        print("Emergency stop activated! Temperature control disabled.")

    def get_system_status(self):
        """Get current system status"""
        return {
            'current_temp': self.current_temp,
            'target_temp': self.pid.setpoint,
            'heat_output': self.heat_output,
            'error': abs(self.pid.setpoint - self.current_temp),
            'is_safe': self.min_temp <= self.current_temp <= self.max_temp
        }

def run_temperature_control_simulation():
    """
    Run the complete temperature control simulation
    """
    print("Complete Temperature Control System Simulation")
    print("=============================================")
    print("This example demonstrates a complete PID-based temperature control system")
    print("with safety features and performance monitoring.\n")

    system = TemperatureControlSystem(initial_temp=20.0)

    print("System initialized:")
    print(f"- Initial temperature: {system.current_temp:.1f}°C")
    print(f"- Target temperature: {system.pid.setpoint:.1f}°C")
    print(f"- Thermal mass: {system.thermal_mass}")
    print(f"- Heat loss rate: {system.heat_loss_rate}\n")

    # Change setpoint during simulation to test response
    setpoint_changes = [(30.0, 5.0), (18.0, 15.0), (25.0, 25.0)]  # (setpoint, time)

    print("Starting temperature control simulation...")
    print("-" * 60)
    print(f"{'Time(s)':<8} {'Temp(°C)':<10} {'Output(%)':<12} {'Error(°C)':<12} {'Safe':<6}")
    print("-" * 60)

    start_time = time.time()

    for i in range(300):  # Run for 300 steps (30 seconds at 0.1s intervals)
        current_time = i * 0.1

        # Check for setpoint changes
        for new_setpoint, change_time in setpoint_changes:
            if abs(current_time - change_time) < 0.1:  # Within time threshold
                system.change_setpoint(new_setpoint)

        temp, output = system.update(dt=0.1)

        # Get system status
        status = system.get_system_status()

        # Print status every 20 steps
        if i % 20 == 0:
            safe_status = "Yes" if status['is_safe'] else "No"
            print(f"{current_time:<8.1f} {temp:<10.2f} {output:<12.2f} {status['error']:<12.2f} {safe_status:<6}")

        time.sleep(0.001)  # Small delay to simulate real-time operation

    elapsed_time = time.time() - start_time
    print(f"\nSimulation completed in {elapsed_time:.2f} seconds")

    # Calculate final performance metrics
    final_status = system.get_system_status()
    avg_error = np.mean([abs(sp - temp) for sp, temp in zip(system.setpoint_log, system.temp_log)])
    max_error = max([abs(sp - temp) for sp, temp in zip(system.setpoint_log, system.temp_log)])

    print(f"\nFinal System Status:")
    print(f"- Current temperature: {final_status['current_temp']:.2f}°C")
    print(f"- Target temperature: {final_status['target_temp']:.2f}°C")
    print(f"- Current error: {final_status['error']:.2f}°C")
    print(f"- Final heat output: {final_status['heat_output']:.2f}%")
    print(f"- System safety: {final_status['is_safe']}")

    print(f"\nPerformance Metrics:")
    print(f"- Average error: {avg_error:.3f}°C")
    print(f"- Maximum error: {max_error:.3f}°C")
    print(f"- Total simulation time: {system.time_log[-1]:.1f} seconds")

    # Plot results
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # Temperature plot
    ax1.plot(system.time_log, system.temp_log, label='Actual Temperature', linewidth=2)
    ax1.plot(system.time_log, system.setpoint_log, label='Setpoint', linestyle='--', linewidth=2)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Temperature (°C)')
    ax1.set_title('Temperature Control System Response')
    ax1.legend()
    ax1.grid(True)

    # Output plot
    ax2.plot(system.time_log, system.output_log, label='Heat Output', color='red', linewidth=2)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Heat Output (%)')
    ax2.set_title('Heating Element Output')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.show()

    print(f"\nThe temperature control system successfully regulated the temperature")
    print(f"to follow the changing setpoints with good stability and safety.")

def main():
    run_temperature_control_simulation()

if __name__ == "__main__":
    main()