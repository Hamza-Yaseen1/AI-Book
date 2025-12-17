#!/usr/bin/env python3
"""
Lesson 1: Multi-Sensor Fusion and Data Integration
Example 3: Confidence Metrics for Fused Data
"""

import numpy as np
import time
import random
from datetime import datetime

class ConfidenceBasedFusion:
    """
    A class that implements sensor fusion with confidence metrics
    """
    def __init__(self):
        self.weights = [0.4, 0.3, 0.3]  # Initial weights for 3 sensors
        self.confidence_history = []
        self.fusion_history = []

    def calculate_confidence(self, readings):
        """
        Calculate confidence in the fused reading based on sensor agreement

        Args:
            readings: List of sensor readings

        Returns:
            float: Confidence score between 0 and 1
        """
        if len(readings) < 2:
            return 1.0  # Perfect confidence if only one sensor

        # Calculate variance among readings (lower variance = higher confidence)
        variance = np.var(readings)

        # Convert variance to confidence (inverse relationship)
        # Using exponential decay to map variance to confidence
        confidence = np.exp(-variance)

        return min(confidence, 1.0)  # Cap at 1.0

    def calculate_dynamic_weights(self, readings):
        """
        Calculate dynamic weights based on sensor reliability

        Args:
            readings: List of sensor readings

        Returns:
            list: Updated weights for each sensor
        """
        # For this example, we'll adjust weights based on how much each reading
        # deviates from the group mean (less deviation = higher weight)
        mean_reading = np.mean(readings)
        deviations = [abs(r - mean_reading) for r in readings]

        # Invert deviations to get reliability scores (higher reliability for lower deviation)
        reliability_scores = [1 / (1 + dev) for dev in deviations]

        # Normalize to get weights
        total_reliability = sum(reliability_scores)
        new_weights = [score / total_reliability for score in reliability_scores]

        return new_weights

    def confidence_based_fusion(self, readings):
        """
        Perform sensor fusion with confidence-based weighting

        Args:
            readings: List of sensor readings

        Returns:
            tuple: (fused_value, confidence_score)
        """
        # Calculate dynamic weights based on current readings
        dynamic_weights = self.calculate_dynamic_weights(readings)

        # Calculate weighted average
        fused_value = np.average(readings, weights=dynamic_weights)

        # Calculate confidence in the fused result
        confidence = self.calculate_confidence(readings)

        # Store in history
        self.confidence_history.append(confidence)
        self.fusion_history.append(fused_value)

        return fused_value, confidence, dynamic_weights

    def adaptive_fusion(self, readings, threshold=0.6):
        """
        Perform adaptive fusion that changes strategy based on confidence

        Args:
            readings: List of sensor readings
            threshold: Confidence threshold for switching strategies

        Returns:
            tuple: (fused_value, confidence_score, strategy_used)
        """
        fused_value, confidence, weights = self.confidence_based_fusion(readings)

        if confidence > threshold:
            strategy = "weighted_average"
        else:
            # Use median instead of weighted average for low confidence situations
            # (median is more robust to outliers)
            fused_value = np.median(readings)
            strategy = "median_fallback"

        return fused_value, confidence, strategy

def main():
    print("Confidence Metrics for Sensor Fusion")
    print("====================================")
    print("This example demonstrates how to calculate and use confidence metrics")
    print("in sensor fusion to improve system reliability.\n")

    fusion_system = ConfidenceBasedFusion()

    print("Simulating sensor fusion with confidence metrics:")
    print("-" * 70)
    print(f"{'Cycle':<6} {'Readings':<25} {'Fused':<8} {'Confidence':<12} {'Strategy':<15}")
    print("-" * 70)

    for cycle in range(12):
        # Simulate different scenarios
        if cycle < 4:
            # Good agreement scenario (sensors reading similar values)
            base_value = 22.0
            readings = [base_value + random.uniform(-0.1, 0.1) for _ in range(3)]
        elif cycle < 8:
            # Moderate disagreement scenario
            base_value = 22.0
            readings = [
                base_value + random.uniform(-0.2, 0.2),  # Sensor 1
                base_value + random.uniform(-0.3, 0.3),  # Sensor 2
                base_value + random.uniform(-0.4, 0.4)   # Sensor 3
            ]
        else:
            # High disagreement scenario (potential sensor failure)
            base_value = 22.0
            readings = [
                base_value + random.uniform(-0.1, 0.1),   # Good sensor
                base_value + random.uniform(-0.2, 0.2),   # Good sensor
                base_value + random.uniform(-2.0, 2.0)    # Potentially faulty sensor
            ]

        # Perform adaptive fusion
        fused_value, confidence, strategy = fusion_system.adaptive_fusion(readings)

        # Format readings for display
        readings_str = "[" + ", ".join([f"{r:.2f}" for r in readings]) + "]"

        print(f"{cycle+1:<6} {readings_str:<25} {fused_value:<8.2f} {confidence:<12.3f} {strategy:<15}")

        time.sleep(0.1)

    print("\n" + "="*70)
    print("ANALYSIS OF CONFIDENCE METRICS")
    print("="*70)

    # Analyze confidence history
    confidences = np.array(fusion_system.confidence_history)
    print(f"Average confidence: {confidences.mean():.3f}")
    print(f"Min confidence: {confidences.min():.3f}")
    print(f"Max confidence: {confidences.max():.3f}")
    print(f"Confidence standard deviation: {confidences.std():.3f}")

    # Show strategy distribution
    strategies = ['weighted_average' if conf > 0.6 else 'median_fallback'
                  for conf in fusion_system.confidence_history]
    weighted_count = strategies.count('weighted_average')
    median_count = strategies.count('median_fallback')

    print(f"\nStrategy distribution:")
    print(f"  Weighted average: {weighted_count} cycles")
    print(f"  Median fallback: {median_count} cycles")

    print(f"\nConfidence metrics help the system:")
    print(f"  - Identify when sensor readings disagree significantly")
    print(f"  - Switch to more robust fusion strategies when confidence is low")
    print(f"  - Provide reliability indicators for downstream systems")
    print(f"  - Enable intelligent sensor failure detection")

if __name__ == "__main__":
    main()