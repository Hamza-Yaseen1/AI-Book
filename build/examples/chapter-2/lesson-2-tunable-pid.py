#!/usr/bin/env python3
"""
Lesson 2: Advanced Control Systems and Feedback Loops
Example 2: Tunable PID Controller with Parameter Adjustment
"""

import time
import random
import matplotlib.pyplot as plt
import numpy as np

class TunablePIDController:
    """
    A PID controller with tunable parameters and performance monitoring
    """
    def __init__(self, kp=1.0, ki=0.0, kd=0.0, setpoint=0):
        """
        Initialize tunable PID controller

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
        self.output_limits = (-100, 100)  # Output limits

        # Performance tracking
        self.error_history = []
        self.output_history = []
        self.setpoint_history = []

    def compute(self, current_value, dt=1.0):
        """
        Compute PID output with output limiting

        Args:
            current_value: Current measured value
            dt: Time step (for derivative calculation)

        Returns:
            Control output
        """
        # Calculate error
        error = self.setpoint - current_value
        self.error_history.append(error)

        # Proportional term
        p_term = self.kp * error

        # Integral term with anti-windup protection
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

        # Calculate output
        output = p_term + i_term + d_term

        # Apply output limits
        output = max(min(output, self.output_limits[1]), self.output_limits[0])

        # Store values for next iteration
        self.previous_error = error
        self.output_history.append(output)
        self.setpoint_history.append(self.setpoint)

        return output

    def set_setpoint(self, setpoint):
        """Update the setpoint"""
        self.setpoint = setpoint

    def set_tunings(self, kp, ki, kd):
        """Update PID tunings"""
        self.kp = kp
        self.ki = ki
        self.kd = kd
        print(f"PID parameters updated - P:{kp}, I:{ki}, D:{kd}")

    def set_output_limits(self, min_val, max_val):
        """Set output limits"""
        self.output_limits = (min_val, max_val)

    def get_performance_metrics(self):
        """
        Calculate performance metrics for the controller

        Returns:
            dict: Performance metrics
        """
        if not self.error_history:
            return {}

        errors = np.array(self.error_history)
        outputs = np.array(self.output_history)

        metrics = {
            'settling_time': self._calculate_settling_time(errors),
            'overshoot': self._calculate_overshoot(errors),
            'steady_state_error': np.mean(np.abs(errors[-20:])),  # Last 20 samples
            'integral_absolute_error': np.sum(np.abs(errors)) * 0.1,  # Approximate integral
            'output_variance': np.var(outputs),
            'max_error': np.max(np.abs(errors))
        }

        return metrics

    def _calculate_settling_time(self, errors, threshold=0.05):
        """Calculate settling time (time to stay within threshold of final value)"""
        # Find when error first enters and stays within threshold
        abs_errors = np.abs(errors)
        final_value = abs_errors[-1] if len(abs_errors) > 0 else 0

        # Look for when error stays within threshold of final value
        threshold_met = abs_errors <= (final_value + threshold)
        for i in range(len(threshold_met) - 1, -1, -1):
            if not threshold_met[i]:
                return i * 0.1  # Assuming 0.1s time steps
        return 0

    def _calculate_overshoot(self, errors):
        """Calculate overshoot as percentage of setpoint change"""
        if len(errors) < 2:
            return 0

        # For this example, we'll calculate overshoot based on error magnitude
        max_error = np.max(np.abs(errors))
        final_error = np.abs(errors[-1]) if len(errors) > 0 else 0

        # Overshoot relative to final error
        if final_error != 0:
            overshoot = (max_error - final_error) / final_error * 100
        else:
            overshoot = max_error * 100

        return overshoot

def compare_pid_settings():
    """
    Compare different PID parameter sets
    """
    print("Comparing Different PID Parameter Sets")
    print("=====================================")
    print("This example shows how different PID parameters affect system response.\n")

    # Different parameter sets to compare
    parameter_sets = [
        {"name": "Conservative", "kp": 1.0, "ki": 0.05, "kd": 0.01},
        {"name": "Aggressive", "kp": 3.0, "ki": 0.2, "kd": 0.05},
        {"name": "Balanced", "kp": 2.0, "ki": 0.1, "kd": 0.02}
    ]

    results = {}

    for params in parameter_sets:
        print(f"Testing {params['name']} PID parameters...")
        pid = TunablePIDController(
            kp=params['kp'], ki=params['ki'], kd=params['kd'], setpoint=50.0
        )

        # Simulate system response
        current_value = 0.0
        for i in range(100):
            time_step = 0.1
            output = pid.compute(current_value, time_step)

            # Simulate system response (simplified model)
            # The output affects the value with some delay and noise
            value_change = output * 0.02 - current_value * 0.01  # Natural decay
            current_value += value_change + random.uniform(-0.1, 0.1) * time_step

        # Calculate performance metrics
        metrics = pid.get_performance_metrics()
        results[params['name']] = {
            'params': params,
            'metrics': metrics
        }

        print(f"  Final error: {abs(pid.setpoint - current_value):.3f}")
        print(f"  Steady-state error: {metrics.get('steady_state_error', 0):.3f}")
        print(f"  Max error: {metrics.get('max_error', 0):.3f}")
        print()

    # Display comparison
    print("Parameter Comparison Summary:")
    print("-" * 80)
    print(f"{'Setting':<12} {'Kp':<6} {'Ki':<6} {'Kd':<6} {'Final Err':<10} {'Steady Err':<12} {'Max Err':<10}")
    print("-" * 80)

    for name, data in results.items():
        params = data['params']
        metrics = data['metrics']
        final_error = abs(params['setpoint'] - current_value)  # Approximate
        steady_error = metrics.get('steady_state_error', 0)
        max_error = metrics.get('max_error', 0)

        print(f"{name:<12} {params['kp']:<6.2f} {params['ki']:<6.2f} {params['kd']:<6.2f} "
              f"{final_error:<10.3f} {steady_error:<12.3f} {max_error:<10.3f}")

    return results

def main():
    print("Tunable PID Controller with Performance Analysis")
    print("===============================================")
    print("This example demonstrates how to tune PID parameters and analyze performance.\n")

    # Compare different parameter sets
    results = compare_pid_settings()

    print("\nTuning Guidelines:")
    print("-" * 50)
    print("Increase Kp: Reduces rise time, increases overshoot")
    print("Increase Ki: Eliminates steady-state error, may increase overshoot/oscillation")
    print("Increase Kd: Reduces overshoot and settling time, improves stability")
    print("\nFor temperature control systems:")
    print("- Start with conservative parameters")
    print("- Increase Kp until oscillation occurs, then reduce by 50%")
    print("- Add small Ki to eliminate steady-state error")
    print("- Add Kd to reduce overshoot if needed")

if __name__ == "__main__":
    main()