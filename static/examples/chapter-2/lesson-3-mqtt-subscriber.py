#!/usr/bin/env python3
"""
Lesson 3: Collaborative and Networked Physical AI
Example 2: MQTT Subscriber for Physical AI Systems
"""

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime
import threading

class PhysicalAISubscriber:
    """
    A Physical AI system that subscribes to sensor data and coordinates actions
    """
    def __init__(self, client_id, broker="localhost", port=1883):
        self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.broker = broker
        self.port = port
        self.connected = False
        self.client_id = client_id

        # Data storage
        self.received_messages = []
        self.subscribed_topics = []
        self.device_states = {}  # Track states of other devices
        self.sensor_data_cache = {}  # Cache latest sensor readings

        # Action callbacks
        self.action_callbacks = {
            "temperature": self.handle_temperature_alert,
            "motion": self.handle_motion_alert,
            "humidity": self.handle_humidity_alert,
            "status": self.handle_status_update
        }

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Subscriber {client._client_id.decode()} connected to MQTT broker at {self.broker}:{self.port}")
            self.connected = True

            # Subscribe to previously stored topics
            for topic in self.subscribed_topics:
                client.subscribe(topic)
                print(f"Subscribed to topic: {topic}")
        else:
            print(f"Failed to connect, return code {rc}")
            self.connected = False

    def on_message(self, client, userdata, msg):
        """
        Handle incoming messages
        """
        try:
            data = json.loads(msg.payload.decode())
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Received from {msg.topic}: {data}")

            # Store received message
            message_entry = {
                "topic": msg.topic,
                "data": data,
                "timestamp": time.time(),
                "raw_payload": msg.payload.decode()
            }
            self.received_messages.append(message_entry)

            # Update device states and sensor cache
            self._update_device_state(data)
            self._update_sensor_cache(msg.topic, data)

            # Process the message based on topic and content
            self._process_message(msg.topic, data)

        except json.JSONDecodeError:
            print(f"Received non-JSON message on {msg.topic}: {msg.payload.decode()}")
        except Exception as e:
            print(f"Error processing message from {msg.topic}: {e}")

    def on_disconnect(self, client, userdata, rc):
        print(f"Subscriber {client._client_id.decode()} disconnected from MQTT broker")
        self.connected = False

    def _update_device_state(self, data):
        """
        Update the state of a device based on received data
        """
        device_id = data.get("device_id")
        if device_id:
            self.device_states[device_id] = {
                "last_seen": datetime.now().isoformat(),
                "data": data,
                "topic": data.get("topic", "unknown")
            }

    def _update_sensor_cache(self, topic, data):
        """
        Update the sensor data cache with the latest reading
        """
        if "sensor_data" in topic and "sensor_type" in data:
            sensor_type = data["sensor_type"]
            self.sensor_data_cache[sensor_type] = {
                "value": data["value"],
                "device_id": data["device_id"],
                "timestamp": data["timestamp"],
                "topic": topic
            }

    def _process_message(self, topic, data):
        """
        Process a received message based on its content and topic
        """
        # Determine the type of message
        if "sensor_data" in topic and "sensor_type" in data:
            sensor_type = data["sensor_type"]
            value = data["value"]

            # Call appropriate handler
            if sensor_type in self.action_callbacks:
                self.action_callbacks[sensor_type](data)
            else:
                print(f"No specific handler for sensor type: {sensor_type}")

        elif "status" in topic:
            self.handle_status_update(data)

        elif "location" in topic:
            self.handle_location_update(data)

        else:
            print(f"Unknown message type from topic: {topic}")

    def handle_temperature_alert(self, data):
        """
        Handle temperature sensor alerts

        Args:
            data: Temperature sensor data dictionary
        """
        temp_value = data["value"]
        device_id = data["device_id"]

        print(f"  -> Processing temperature alert from {device_id}: {temp_value}°C")

        # Trigger appropriate action based on temperature
        if temp_value > 25:
            print(f"  -> ACTION: Temperature HIGH ({temp_value}°C) - activating cooling system")
            self._trigger_action("cooling", {"target": device_id, "temperature": temp_value})
        elif temp_value < 18:
            print(f"  -> ACTION: Temperature LOW ({temp_value}°C) - activating heating system")
            self._trigger_action("heating", {"target": device_id, "temperature": temp_value})
        else:
            print(f"  -> INFO: Temperature OK ({temp_value}°C)")

    def handle_motion_alert(self, data):
        """
        Handle motion sensor alerts

        Args:
            data: Motion sensor data dictionary
        """
        motion_value = data["value"]
        device_id = data["device_id"]

        print(f"  -> Processing motion alert from {device_id}: {motion_value}")

        if motion_value == 1:  # Motion detected
            print(f"  -> ACTION: Motion detected at {device_id} - increasing monitoring")
            self._trigger_action("increase_monitoring", {"target": device_id})
        else:
            print(f"  -> INFO: No motion at {device_id}")

    def handle_humidity_alert(self, data):
        """
        Handle humidity sensor alerts

        Args:
            data: Humidity sensor data dictionary
        """
        humidity_value = data["value"]
        device_id = data["device_id"]

        print(f"  -> Processing humidity alert from {device_id}: {humidity_value}%")

        if humidity_value > 70:
            print(f"  -> ACTION: Humidity HIGH ({humidity_value}%) - activating dehumidifier")
            self._trigger_action("dehumidify", {"target": device_id, "humidity": humidity_value})
        elif humidity_value < 30:
            print(f"  -> ACTION: Humidity LOW ({humidity_value}%) - activating humidifier")
            self._trigger_action("humidify", {"target": device_id, "humidity": humidity_value})

    def handle_status_update(self, data):
        """
        Handle status updates from other devices

        Args:
            data: Status update data dictionary
        """
        device_id = data.get("device_id")
        status = data.get("status")
        message = data.get("message", "")

        print(f"  -> Status update from {device_id}: {status} - {message}")

        # Update our knowledge of the device's status
        if device_id and device_id in self.device_states:
            self.device_states[device_id]["status"] = status
            self.device_states[device_id]["status_message"] = message

    def handle_location_update(self, data):
        """
        Handle location updates from mobile devices

        Args:
            data: Location update data dictionary
        """
        device_id = data.get("device_id")
        x = data.get("x")
        y = data.get("y")
        z = data.get("z")

        print(f"  -> Location update from {device_id}: ({x}, {y}, {z})")

        # Could trigger area-based actions
        self._trigger_action("location_update", {
            "device_id": device_id,
            "coordinates": {"x": x, "y": y, "z": z}
        })

    def _trigger_action(self, action_type, params):
        """
        Trigger an action based on sensor data

        Args:
            action_type: Type of action to trigger
            params: Parameters for the action
        """
        # In a real system, this would execute actual control actions
        print(f"  -> TRIGGERED: {action_type.upper()} action with params: {params}")

        # Example: Publish command to actuator
        command_topic = f"physical_ai/commands/{action_type}"
        command_data = {
            "action": action_type,
            "parameters": params,
            "timestamp": datetime.now().isoformat(),
            "initiator": self.client_id
        }

        if self.connected:
            result = self.client.publish(command_topic, json.dumps(command_data))
            if result.rc == 0:
                print(f"  -> Command published to {command_topic}")
            else:
                print(f"  -> Failed to publish command to {command_topic}")

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
        print(f"Subscriber {self.client_id} disconnected from MQTT broker")

    def subscribe_to_topic(self, topic_pattern):
        """
        Subscribe to a specific topic pattern

        Args:
            topic_pattern: Topic pattern to subscribe to (e.g., "physical_ai/sensor_data/#")
        """
        self.subscribed_topics.append(topic_pattern)
        if self.connected:
            self.client.subscribe(topic_pattern)
            print(f"Subscribed to topic: {topic_pattern}")

    def get_recent_messages(self, topic_filter=None, max_age_seconds=30):
        """
        Get recent messages

        Args:
            topic_filter: Filter by topic pattern (None for all topics)
            max_age_seconds: Maximum age of messages to return

        Returns:
            List of recent messages
        """
        current_time = time.time()
        recent_msgs = []

        for msg in self.received_messages:
            if current_time - msg["timestamp"] <= max_age_seconds:
                if topic_filter is None or topic_filter in msg["topic"]:
                    recent_msgs.append(msg)

        return recent_msgs

    def get_device_summary(self):
        """
        Get a summary of all known devices

        Returns:
            dict: Summary of known devices
        """
        summary = {
            "total_devices": len(self.device_states),
            "devices": list(self.device_states.keys()),
            "latest_sensor_readings": self.sensor_data_cache,
            "total_messages_received": len(self.received_messages)
        }
        return summary

def simulate_physical_ai_subscriber():
    """
    Simulate a Physical AI subscriber receiving and processing sensor data
    """
    print("MQTT Subscriber for Physical AI Systems")
    print("=======================================")
    print("This example demonstrates how a Physical AI system can subscribe")
    print("to sensor data, process it, and trigger appropriate actions.\n")

    # Create a subscriber instance
    subscriber = PhysicalAISubscriber("control_center_001", "localhost", 1883)

    # Subscribe to relevant topics
    subscriber.subscribe_to_topic("physical_ai/sensor_data/#")  # All sensor data
    subscriber.subscribe_to_topic("physical_ai/status/#")       # All status updates
    subscriber.subscribe_to_topic("physical_ai/location/#")     # All location updates

    # Attempt to connect to MQTT broker
    print("Connecting to MQTT broker...")
    if not subscriber.connect():
        print("Failed to connect to MQTT broker. Please make sure an MQTT broker is running.")
        print("You can install Mosquitto or use a public MQTT broker for testing.")
        return

    print("Connection successful! Ready to receive sensor data...\n")
    print("Waiting for incoming messages. Press Ctrl+C to stop.\n")

    try:
        # Keep the subscriber running to receive messages
        print("Subscriber is now listening for messages...")

        # Print summary periodically
        start_time = time.time()
        while True:
            current_time = time.time()

            # Print summary every 10 seconds
            if int(current_time - start_time) % 10 == 0 and int(current_time - start_time) > 0:
                summary = subscriber.get_device_summary()
                print(f"\n--- SYSTEM SUMMARY (Runtime: {int(current_time - start_time)}s) ---")
                print(f"Known devices: {summary['total_devices']}")
                print(f"Latest sensor readings: {len(summary['latest_sensor_readings'])}")
                print(f"Messages received: {summary['total_messages_received']}")

                # Show latest sensor readings
                for sensor_type, data in subscriber.sensor_data_cache.items():
                    print(f"  {sensor_type}: {data['value']} from {data['device_id']}")
                print("-" * 50)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nSimulation stopped by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        # Print final summary
        final_summary = subscriber.get_device_summary()
        print(f"\nFINAL SUMMARY:")
        print(f"- Total devices discovered: {final_summary['total_devices']}")
        print(f"- Total messages received: {final_summary['total_messages_received']}")
        print(f"- Latest sensor readings: {len(final_summary['latest_sensor_readings'])}")

        # Disconnect cleanly
        subscriber.disconnect()

def main():
    simulate_physical_ai_subscriber()

if __name__ == "__main__":
    main()