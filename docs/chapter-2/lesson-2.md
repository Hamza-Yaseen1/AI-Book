---
sidebar_position: 2
---

# Lesson 2: Advanced Control Systems and Feedback Loops

## Learning Objectives

- Understand PID (Proportional-Integral-Derivative) control principles
- Implement PID controllers for Physical AI systems
- Tune PID parameters for optimal system performance
- Apply control theory to real physical systems
- Implement safety mechanisms in control systems

## Prerequisites

Before starting this lesson, you should:
- Have completed Chapter 1 and Lesson 1 of Chapter 2
- Understand basic sensor reading and data processing concepts
- Be familiar with Python programming
- Have basic understanding of feedback concepts from Lesson 1

## Introduction to Control Systems

Control systems are fundamental to Physical AI, allowing systems to respond appropriately to sensor inputs and maintain desired behaviors. A control system continuously measures the output of a process and adjusts the input to achieve a desired outcome.

### Types of Control Systems

1. **Open-loop Control**: Control action is independent of output
2. **Closed-loop Control (Feedback)**: Control action depends on output measurement
3. **Feedforward Control**: Anticipates disturbances before they affect the system

## PID Controller Theory

The PID (Proportional-Integral-Derivative) controller is the most common feedback controller. It calculates an error value as the difference between a desired setpoint and a measured process variable, then applies a correction based on proportional, integral, and derivative terms.

### PID Equation

The PID controller output is calculated as:

```
u(t) = Kp * e(t) + Ki * ∫e(t)dt + Kd * de(t)/dt
```

Where:
- `u(t)` is the controller output
- `e(t)` is the error (setpoint - process variable)
- `Kp`, `Ki`, `Kd` are the proportional, integral, and derivative gains

### The Three Terms

1. **Proportional (P)**: Reduces current error, but may have steady-state error
2. **Integral (I)**: Eliminates steady-state error by considering past errors
3. **Derivative (D)**: Predicts future error based on current rate of change

## PID Controller Implementation

Let's implement a basic PID controller:

```python
class PIDController:
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
        # Reset integral when setpoint changes significantly
        if abs(setpoint - self.setpoint) > 1:
            self.integral = 0

    def set_tunings(self, kp, ki, kd):
        """Update PID tunings"""
        self.kp = kp
        self.ki = ki
        self.kd = kd
```

## Practical Example: Temperature Control System

Let's implement a complete temperature control system using PID:

```python
import time
import matplotlib.pyplot as plt
import random

class TemperatureControlSystem:
    def __init__(self, initial_temp=20.0):
        # Initialize PID controller for temperature control
        self.pid = PIDController(kp=2.0, ki=0.1, kd=0.05, setpoint=25.0)  # Target: 25°C
        self.current_temp = initial_temp
        self.heat_output = 0  # Output to heating element (0-100%)

        # System characteristics
        self.thermal_mass = 5.0  # How slowly temperature changes
        self.heat_loss_rate = 0.1  # Rate of heat loss to environment

    def update(self, dt=0.1):
        """
        Update the temperature control system

        Args:
            dt: Time step in seconds
        """
        # Get PID output based on current temperature
        control_signal = self.pid.compute(self.current_temp, dt)

        # Apply limits to heating output (0-100%)
        self.heat_output = max(0, min(100, control_signal))

        # Simulate temperature change based on heating and cooling
        heating_effect = (self.heat_output / 100.0) * 2.0 * dt  # Heat added
        cooling_effect = (self.current_temp - 20.0) * self.heat_loss_rate * dt  # Heat lost

        # Update temperature with some noise to simulate real system
        temp_change = heating_effect - cooling_effect + random.uniform(-0.1, 0.1) * dt
        self.current_temp += temp_change / self.thermal_mass

        return self.current_temp, self.heat_output

def run_temperature_control():
    """Run the temperature control simulation"""
    system = TemperatureControlSystem(initial_temp=20.0)

    # Data storage for plotting
    times = []
    temperatures = []
    heat_outputs = []
    setpoints = []

    print("Temperature Control System Simulation")
    print("=====================================")
    print("Target temperature: 25°C")
    print("Initial temperature: 20°C")
    print("\nTime(s)\tTemp(°C)\tHeat(%)\tError")
    print("-" * 40)

    start_time = time.time()

    for i in range(200):  # Run for 200 steps (20 seconds at 0.1s intervals)
        current_time = i * 0.1
        temp, heat_output = system.update(dt=0.1)

        # Calculate error
        error = abs(system.pid.setpoint - temp)

        # Print status every 10 steps
        if i % 10 == 0:
            print(f"{current_time:5.1f}\t{temp:6.2f}\t{heat_output:6.2f}\t{error:6.2f}")

        # Store data for plotting
        times.append(current_time)
        temperatures.append(temp)
        heat_outputs.append(heat_output)
        setpoints.append(system.pid.setpoint)

        time.sleep(0.01)  # Small delay to simulate real-time operation

    # Plot results
    plt.figure(figsize=(12, 8))

    plt.subplot(2, 1, 1)
    plt.plot(times, temperatures, label='Actual Temperature', linewidth=2)
    plt.plot(times, setpoints, label='Setpoint', linestyle='--', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('Temperature (°C)')
    plt.title('Temperature Control System Response')
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(times, heat_outputs, label='Heat Output', color='red', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('Heat Output (%)')
    plt.title('Heating Element Output')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    final_error = abs(system.pid.setpoint - system.current_temp)
    print(f"\nFinal temperature: {system.current_temp:.2f}°C")
    print(f"Final error: {final_error:.2f}°C")
    print(f"Steady-state error: {final_error:.2f}°C")

# Run the simulation
if __name__ == "__main__":
    run_temperature_control()
```

## PID Tuning Methods

Properly tuning PID parameters is crucial for system performance. Here are common tuning methods:

### 1. Ziegler-Nichols Method

This method involves finding the ultimate gain (Ku) and ultimate period (Pu) where the system oscillates with constant amplitude.

### 2. Trial and Error

Start with conservative values and adjust based on system response:
- Start with P only, increase until oscillation occurs
- Add I to eliminate steady-state error
- Add D to reduce overshoot

### 3. Software-based Tuning

Use automated tools to find optimal parameters based on system response.

## Safety Considerations in Control Systems

When implementing control systems, especially for physical systems, safety is paramount:

### 1. Limits and Constraints
- Set output limits to prevent damage
- Implement rate limiting to prevent sudden changes
- Use position and velocity limits for mechanical systems

### 2. Fail-Safe Mechanisms
- Default to safe state if sensors fail
- Implement watchdog timers
- Use redundant sensors for critical systems

### 3. Monitoring and Logging
- Log all control actions for debugging
- Monitor system health continuously
- Alert when parameters exceed safe ranges

## Practical Project: Motor Speed Control

Let's create a practical project implementing PID control for motor speed:

```python
# physical-ai/static/examples/chapter-2/lesson-2-motor-control.py
import time
import random
import matplotlib.pyplot as plt

class MotorControlSystem:
    def __init__(self, initial_speed=0):
        # Initialize PID controller for motor speed control
        self.pid = PIDController(kp=1.5, ki=0.2, kd=0.01, setpoint=100)  # Target: 100 RPM
        self.current_speed = initial_speed
        self.motor_output = 0  # Motor output (0-100%)

        # Motor characteristics
        self.motor_inertia = 3.0  # How slowly speed changes
        self.friction = 0.05  # Friction losses

        # Safety limits
        self.max_speed = 200  # Maximum RPM
        self.max_output = 100  # Maximum output percentage

    def update(self, dt=0.05):
        """
        Update the motor control system

        Args:
            dt: Time step in seconds
        """
        # Get PID output based on current speed
        control_signal = self.pid.compute(self.current_speed, dt)

        # Apply limits to motor output
        self.motor_output = max(0, min(self.max_output, control_signal))

        # Simulate motor response with some delay and friction
        target_change = (self.motor_output / 100.0) * 50.0 * dt  # Max 50 RPM change per second
        friction_loss = self.current_speed * self.friction * dt

        # Apply changes with motor inertia
        speed_change = (target_change - friction_loss) / self.motor_inertia
        self.current_speed += speed_change

        # Apply limits
        self.current_speed = max(0, min(self.max_speed, self.current_speed))

        # Add some noise to simulate real motor
        self.current_speed += random.uniform(-0.5, 0.5) * dt

        return self.current_speed, self.motor_output

    def emergency_stop(self):
        """Emergency stop function"""
        self.pid.set_setpoint(0)
        self.motor_output = 0
        print("Emergency stop activated!")

def run_motor_control():
    """Run the motor control simulation"""
    system = MotorControlSystem(initial_speed=0)

    # Data storage for plotting
    times = []
    speeds = []
    outputs = []
    setpoints = []

    print("Motor Speed Control System Simulation")
    print("=====================================")
    print("Target speed: 100 RPM")
    print("Initial speed: 0 RPM")
    print("\nTime(s)\tSpeed(RPM)\tOutput(%)\tError")
    print("-" * 45)

    # Change setpoint during simulation to test response
    setpoint_changes = [(50, 2.0), (150, 6.0), (100, 10.0)]  # (setpoint, time)

    start_time = time.time()

    for i in range(200):  # Run for 200 steps (10 seconds at 0.05s intervals)
        current_time = i * 0.05

        # Check for setpoint changes
        for new_setpoint, change_time in setpoint_changes:
            if abs(current_time - change_time) < 0.05:  # Within time threshold
                system.pid.set_setpoint(new_setpoint)
                print(f"Setpoint changed to {new_setpoint} RPM at {current_time:.2f}s")

        speed, output = system.update(dt=0.05)

        # Calculate error
        error = abs(system.pid.setpoint - speed)

        # Print status every 20 steps
        if i % 20 == 0:
            print(f"{current_time:5.2f}\t{speed:8.2f}\t{output:8.2f}\t{error:6.2f}")

        # Store data for plotting
        times.append(current_time)
        speeds.append(speed)
        outputs.append(output)
        setpoints.append(system.pid.setpoint)

        time.sleep(0.001)  # Small delay

    # Plot results
    plt.figure(figsize=(12, 8))

    plt.subplot(2, 1, 1)
    plt.plot(times, speeds, label='Actual Speed', linewidth=2)
    plt.plot(times, setpoints, label='Setpoint', linestyle='--', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('Speed (RPM)')
    plt.title('Motor Speed Control System Response')
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(times, outputs, label='Motor Output', color='red', linewidth=2)
    plt.xlabel('Time (s)')
    plt.ylabel('Motor Output (%)')
    plt.title('Motor Output Signal')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    final_error = abs(system.pid.setpoint - system.current_speed)
    print(f"\nFinal speed: {system.current_speed:.2f} RPM")
    print(f"Final error: {final_error:.2f} RPM")
    print(f"System stability: {'Good' if final_error < 5 else 'Needs tuning'}")

if __name__ == "__main__":
    run_motor_control()
```

## Exercises

1. **Temperature Control Tuning**: Implement different PID tuning methods and compare their performance
2. **Cascade Control**: Create a cascade control system with inner and outer loops
3. **Adaptive PID**: Implement a PID controller that adjusts its parameters based on system conditions
4. **Multi-Variable Control**: Extend the system to control multiple variables simultaneously

## Summary

In this lesson, we explored advanced control systems, focusing on PID controllers. We implemented a complete temperature control system and motor speed control project, demonstrating how PID controllers can be used to maintain desired system behaviors.

Control systems are essential for Physical AI applications, providing the feedback mechanisms needed to respond to environmental changes and maintain desired states. Proper tuning and safety considerations are crucial for reliable operation.

In the next lesson, we'll explore networked Physical AI systems that can communicate and coordinate with each other.