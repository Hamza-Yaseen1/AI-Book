---
sidebar_position: 2
---

# Lesson 2: Building Your First Physical AI System

## Learning Objectives

- Design and implement a simple Physical AI system
- Integrate sensors with processing algorithms
- Create basic actuation mechanisms
- Understand the feedback loop in Physical AI systems

## System Architecture

A basic Physical AI system consists of three main components:

1. **Sensors**: Collect data from the environment
2. **AI Processing**: Analyze data and make decisions
3. **Actuators**: Execute physical actions based on decisions

### Data Flow

```
Environment → Sensors → Processing → Actuators → Environment
     ↑                                        ↓
     └────────── Feedback Loop ────────────────┘
```

## Hands-On Project: Smart Temperature Monitor

In this lesson, we'll build a Physical AI system that monitors temperature and takes appropriate actions.

### Required Materials
- Raspberry Pi
- Temperature sensor (DS18B20 or DHT22)
- LED indicators (red, green, blue)
- Resistors
- Breadboard and jumper wires

### Implementation Steps

1. **Hardware Setup**
   - Connect temperature sensor to Raspberry Pi
   - Connect LED indicators for different temperature ranges

2. **Software Implementation**
   ```python
   import time
   import Adafruit_DHT
   import RPi.GPIO as GPIO

   # Setup
   sensor = Adafruit_DHT.DHT22
   pin = 4  # GPIO pin for sensor
   led_hot = 17
   led_cold = 18
   led_normal = 19

   GPIO.setmode(GPIO.BCM)
   GPIO.setup(led_hot, GPIO.OUT)
   GPIO.setup(led_cold, GPIO.OUT)
   GPIO.setup(led_normal, GPIO.OUT)

   while True:
       humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
       if temperature is not None:
           print(f"Temperature: {temperature}°C")

           # Control LEDs based on temperature
           if temperature > 25:
               GPIO.output(led_hot, GPIO.HIGH)
               GPIO.output(led_cold, GPIO.LOW)
               GPIO.output(led_normal, GPIO.LOW)
           elif temperature < 18:
               GPIO.output(led_hot, GPIO.LOW)
               GPIO.output(led_cold, GPIO.HIGH)
               GPIO.output(led_normal, GPIO.LOW)
           else:
               GPIO.output(led_hot, GPIO.LOW)
               GPIO.output(led_cold, GPIO.LOW)
               GPIO.output(led_normal, GPIO.HIGH)
       else:
           print("Failed to read sensor data")

       time.sleep(2)
   ```

3. **Testing and Calibration**
   - Test the system under different temperature conditions
   - Adjust thresholds as needed
   - Verify proper LED responses

### Complete Code Example

We've provided a complete, runnable example that demonstrates the concepts covered in this lesson. You can find the code in our examples directory:

[Download Lesson 2 Example Code](/static/examples/lesson-2-smart-temperature-monitor.py)

To run the example:
```bash
# Navigate to the physical-ai directory
cd physical-ai

# Run the example (simulated version)
python static/examples/lesson-2-smart-temperature-monitor.py
```

## Safety Considerations

- Always disconnect power when making hardware connections
- Use appropriate voltage levels for your components
- Test in a controlled environment before deployment

## Summary

This lesson guided you through building your first Physical AI system. You learned how to integrate sensors, process data, and create actuation responses. In the next lesson, we'll explore more advanced concepts.

### Exercises

1. Modify the temperature thresholds to match your local climate
2. Add additional sensors (humidity, light) to the system
3. Implement more sophisticated decision-making logic