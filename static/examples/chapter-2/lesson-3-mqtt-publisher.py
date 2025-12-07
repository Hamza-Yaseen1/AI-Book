#!/usr/bin/env python3
"""
Lesson 3: Collaborative and Networked Physical AI
Example 1: MQTT Publisher for Physical AI Systems
"""

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

class PhysicalAIPublisher:
    """
    A Physical AI system that publishes sensor data and status updates
    """
    def __init__(self, client_id, broker="localhost", port=1883):
        self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish

        self.broker = broker
        self.port = port
        self.connected = False
        self.client_id = client_id

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Publisher {client._client_id.decode()} connected to MQTT broker at {self.broker}:{self.port}")
            self.connected = True
        else:
            print(f"Failed to connect to MQTT broker, return code {rc}")
            self.connected = False

    def on_disconnect(self, client, userdata, rc):
        print(f"Publisher {client._client_id.decode()} disconnected from MQTT broker")
        self.connected = False

    def on_publish(self, client, userdata, mid):
        # Successfully published
        pass

    def connect(self):
        """
        Connect to the MQTT broker

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            # Wait for connection with timeout
            timeout = 5  # 5 seconds timeout
            start_time = time.time()
            while not self.connected and time.time() - start_time < timeout:
                time.sleep(0.1)
            return self.connected
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")
            return False

    def disconnect(self):
        """Disconnect from the MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        print(f"Publisher {self.client_id} disconnected from MQTT broker")

    def publish_sensor_data(self, sensor_type, value, additional_data=None):
        """
        Publish sensor data to MQTT topic

        Args:
            sensor_type: Type of sensor (e.g., 'temperature', 'motion')
            value: Sensor reading value
            additional_data: Additional data to include in message

        Returns:
            bool: True if publication successful, False otherwise
        """
        if not self.connected:
            print("Cannot publish: not connected to broker")
            return False

        data = {
            "sensor_type": sensor_type,
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "device_id": self.client._client_id.decode(),
            "additional_data": additional_data or {},
            "quality": "good"  # Simulated sensor quality
        }

        topic = f"physical_ai/sensor_data/{sensor_type}"
        result = self.client.publish(topic, json.dumps(data))

        if result.rc == 0:
            print(f"Published to {topic}: {data}")
            return True
        else:
            print(f"Failed to publish to {topic}")
            return False

    def publish_status(self, status, message=""):
        """
        Publish device status

        Args:
            status: Status string (e.g., 'operational', 'warning', 'error')
            message: Optional message with status details
        """
        if not self.connected:
            return False

        data = {
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "device_id": self.client._client_id.decode(),
            "uptime_seconds": int(time.time())  # Simulated uptime
        }

        topic = f"physical_ai/status/{self.client._client_id.decode()}"
        result = self.client.publish(topic, json.dumps(data))

        if result.rc == 0:
            print(f"Published status to {topic}: {status}")
            return True
        else:
            print(f"Failed to publish status to {topic}")
            return False

    def publish_location(self, x, y, z=None):
        """
        Publish device location data

        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate (optional)
        """
        if not self.connected:
            return False

        location_data = {
            "x": x,
            "y": y,
            "z": z,
            "timestamp": datetime.now().isoformat(),
            "device_id": self.client._client_id.decode()
        }

        topic = f"physical_ai/location/{self.client._client_id.decode()}"
        result = self.client.publish(topic, json.dumps(location_data))

        if result.rc == 0:
            print(f"Published location to {topic}: ({x}, {y}, {z})")
            return True
        else:
            print(f"Failed to publish location to {topic}")
            return False

def simulate_physical_ai_publisher():
    """
    Simulate a Physical AI publisher sending various types of data
    """
    print("MQTT Publisher for Physical AI Systems")
    print("=======================================")
    print("This example demonstrates how a Physical AI system can publish")
    print("sensor data, status updates, and location information via MQTT.\n")

    # Create a publisher instance
    publisher = PhysicalAIPublisher("sensor_node_001", "localhost", 1883)

    # Attempt to connect to MQTT broker
    print("Connecting to MQTT broker...")
    if not publisher.connect():
        print("Failed to connect to MQTT broker. Please make sure an MQTT broker is running.")
        print("You can install Mosquitto or use a public MQTT broker for testing.")
        return

    print("Connection successful! Starting to publish sensor data...\n")

    try:
        # Publish initial status
        publisher.publish_status("operational", "System initialized and ready")

        # Simulate publishing various sensor data
        for cycle in range(20):
            print(f"\n--- Publishing Cycle {cycle+1} ---")

            # Simulate different sensor readings
            temp_reading = 22.5 + random.uniform(-2, 3)
            humidity_reading = 45.0 + random.uniform(-10, 10)
            motion_detected = 1 if random.random() > 0.8 else 0  # 20% chance of motion
            light_level = 300 + random.uniform(-100, 200)

            # Publish sensor data
            publisher.publish_sensor_data("temperature", round(temp_reading, 2),
                                         {"unit": "celsius", "accuracy": "±0.5°C"})
            publisher.publish_sensor_data("humidity", round(humidity_reading, 2),
                                         {"unit": "percent", "accuracy": "±3%"})
            publisher.publish_sensor_data("motion", motion_detected,
                                         {"status": "motion" if motion_detected else "no_motion"})
            publisher.publish_sensor_data("light", round(light_level, 2),
                                         {"unit": "lux", "range": "0-1000"})

            # Occasionally publish location data (simulating a mobile robot)
            if cycle % 5 == 0:
                x_pos = random.uniform(0, 10)
                y_pos = random.uniform(0, 10)
                publisher.publish_location(round(x_pos, 2), round(y_pos, 2))

            # Randomly publish status updates
            if cycle % 7 == 0:
                statuses = ["operational", "monitoring", "standby", "calibrating"]
                random_status = random.choice(statuses)
                publisher.publish_status(random_status, f"Cycle {cycle+1} status update")

            # Wait before next cycle
            time.sleep(2)

        print("\nSimulation completed successfully!")
        print("Published sensor data, status updates, and location information.")

    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred during simulation: {e}")
    finally:
        # Always disconnect cleanly
        publisher.disconnect()

def main():
    simulate_physical_ai_publisher()

if __name__ == "__main__":
    main()