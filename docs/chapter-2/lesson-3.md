---
sidebar_position: 3
---

# Lesson 3: Collaborative and Networked Physical AI

## Learning Objectives

- Understand communication protocols for Physical AI systems
- Implement MQTT for device-to-device communication
- Create networked Physical AI systems that coordinate actions
- Handle network failures and implement redundancy
- Design distributed intelligence systems

## Prerequisites

Before starting this lesson, you should:
- Have completed Chapter 1 and Lessons 1-2 of Chapter 2
- Understand basic networking concepts
- Be familiar with Python networking libraries
- Understand system state and coordination concepts

## Introduction to Networked Physical AI

Modern Physical AI systems often need to communicate with other systems or cloud services, making networking capabilities essential for real-world applications. Networked Physical AI enables:

1. **Distributed Intelligence**: Multiple systems working together to solve complex problems
2. **Resource Sharing**: Sharing sensors, actuators, or computational resources
3. **Remote Monitoring**: Supervising and controlling systems from a distance
4. **Coordinated Actions**: Multiple systems working together towards a common goal

## Communication Protocols for Physical AI

### MQTT (Message Queuing Telemetry Transport)

MQTT is a lightweight messaging protocol designed for IoT and Physical AI applications. It uses a publish-subscribe pattern that makes it ideal for distributed Physical AI systems.

#### Key Features:
- Lightweight and efficient
- Designed for unreliable networks
- Supports Quality of Service (QoS) levels
- Built-in support for "last will" messages

### Other Protocols
- **HTTP/REST**: Universal but not optimized for real-time Physical AI
- **WebSocket**: Bi-directional communication but more resource-intensive
- **CoAP**: Constrained Application Protocol for resource-limited devices
- **Custom TCP/UDP**: For specific performance requirements

## MQTT Implementation for Physical AI

Let's implement a basic MQTT publisher and subscriber for Physical AI systems:

```python
import paho.mqtt.client as mqtt
import json
import time
import threading
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

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Publisher {client._client_id.decode()} connected to MQTT broker")
            self.connected = True
        else:
            print(f"Failed to connect, return code {rc}")
            self.connected = False

    def on_disconnect(self, client, userdata, rc):
        print(f"Publisher {client._client_id.decode()} disconnected from MQTT broker")
        self.connected = False

    def on_publish(self, client, userdata, mid):
        pass  # Successfully published

    def connect(self):
        """Connect to the MQTT broker"""
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            # Wait for connection
            timeout = 5  # 5 seconds timeout
            start_time = time.time()
            while not self.connected and time.time() - start_time < timeout:
                time.sleep(0.1)
            return self.connected
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")
            return False

    def publish_sensor_data(self, sensor_type, value, additional_data=None):
        """
        Publish sensor data to MQTT topic

        Args:
            sensor_type: Type of sensor (e.g., 'temperature', 'motion')
            value: Sensor reading value
            additional_data: Additional data to include in message
        """
        if not self.connected:
            print("Cannot publish: not connected to broker")
            return

        data = {
            "sensor_type": sensor_type,
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "device_id": self.client._client_id.decode(),
            "additional_data": additional_data or {}
        }

        topic = f"physical_ai/{sensor_type}"
        self.client.publish(topic, json.dumps(data))
        print(f"Published to {topic}: {data}")

    def publish_status(self, status, message=""):
        """Publish device status"""
        if not self.connected:
            return

        data = {
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "device_id": self.client._client_id.decode()
        }

        topic = f"physical_ai/status"
        self.client.publish(topic, json.dumps(data))
        print(f"Published status: {data}")

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
        self.received_messages = []
        self.subscribed_topics = []

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Subscriber {client._client_id.decode()} connected to MQTT broker")
            self.connected = True
            # Subscribe to topics after connection
            for topic in self.subscribed_topics:
                client.subscribe(topic)
        else:
            print(f"Failed to connect, return code {rc}")
            self.connected = False

    def on_message(self, client, userdata, msg):
        """Handle incoming messages"""
        try:
            data = json.loads(msg.payload.decode())
            print(f"Received from {msg.topic}: {data}")

            # Store received message
            self.received_messages.append({
                "topic": msg.topic,
                "data": data,
                "timestamp": time.time()
            })

            # Process the sensor data
            self.process_sensor_data(data)
        except json.JSONDecodeError:
            print(f"Received non-JSON message: {msg.payload.decode()}")

    def on_disconnect(self, client, userdata, rc):
        print(f"Subscriber {client._client_id.decode()} disconnected from MQTT broker")
        self.connected = False

    def process_sensor_data(self, data):
        """
        Process incoming sensor data and take appropriate action

        Args:
            data: Dictionary containing sensor data
        """
        sensor_type = data.get("sensor_type")
        value = data.get("value")

        # Example processing logic
        if sensor_type == "temperature" and value is not None:
            if value > 25:
                print(f"  -> Action: Temperature too high ({value}°C) - triggering cooling!")
            elif value < 18:
                print(f"  -> Action: Temperature too low ({value}°C) - triggering heating!")

        elif sensor_type == "motion" and value is not None:
            if value == 1:  # Motion detected
                print(f"  -> Action: Motion detected - increasing monitoring!")

    def connect(self):
        """Connect to the MQTT broker"""
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            # Wait for connection
            timeout = 5  # 5 seconds timeout
            start_time = time.time()
            while not self.connected and time.time() - start_time < timeout:
                time.sleep(0.1)
            return self.connected
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")
            return False

    def subscribe_to_topic(self, topic):
        """Subscribe to a specific topic"""
        if self.connected:
            self.client.subscribe(topic)
        else:
            # Store for subscription after connection
            self.subscribed_topics.append(topic)

    def get_recent_messages(self, topic_filter=None, max_age_seconds=30):
        """
        Get recent messages

        Args:
            topic_filter: Filter by topic (None for all topics)
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
```

## Practical Project: Networked Sensor Network

Let's create a practical project that demonstrates multiple Physical AI systems communicating and coordinating:

```python
# physical-ai/static/examples/chapter-2/lesson-3-networked-project.py
import paho.mqtt.client as mqtt
import json
import time
import threading
import random
from datetime import datetime

class NetworkedPhysicalAI:
    """
    A networked Physical AI system that can both publish and subscribe
    """
    def __init__(self, device_id, broker="localhost", port=1883):
        self.device_id = device_id
        self.client = mqtt.Client(device_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.broker = broker
        self.port = port
        self.connected = False
        self.received_messages = []

        # Device state
        self.local_sensors = {
            "temperature": 22.0,
            "motion": 0,
            "light": 300
        }
        self.coordinated_devices = {}  # Track other devices

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Device {self.device_id} connected to MQTT broker")
            self.connected = True

            # Subscribe to relevant topics
            client.subscribe("physical_ai/+/+")  # All physical ai topics
            client.subscribe(f"physical_ai/device/{self.device_id}/command")  # Direct commands
        else:
            print(f"Device {self.device_id} failed to connect, return code {rc}")
            self.connected = False

    def on_message(self, client, userdata, msg):
        """Handle incoming messages"""
        try:
            data = json.loads(msg.payload.decode())

            # Add to received messages
            self.received_messages.append({
                "topic": msg.topic,
                "data": data,
                "timestamp": time.time()
            })

            print(f"[{self.device_id}] Received from {msg.topic}: {data}")

            # Process based on topic
            if "command" in msg.topic:
                self.handle_command(data)
            elif "status" in msg.topic:
                self.handle_status(data)
            elif "physical_ai/" in msg.topic:
                self.handle_sensor_data(data)

        except json.JSONDecodeError:
            print(f"[{self.device_id}] Received non-JSON message: {msg.payload.decode()}")

    def on_disconnect(self, client, userdata, rc):
        print(f"Device {self.device_id} disconnected from MQTT broker")
        self.connected = False

    def connect(self):
        """Connect to the MQTT broker"""
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            # Wait for connection
            timeout = 5
            start_time = time.time()
            while not self.connected and time.time() - start_time < timeout:
                time.sleep(0.1)
            return self.connected
        except Exception as e:
            print(f"Error connecting device {self.device_id}: {e}")
            return False

    def handle_command(self, data):
        """Handle direct commands to this device"""
        command = data.get("command")
        if command == "identify":
            self.publish_device_info()
        elif command == "sync":
            self.sync_with_network()

    def handle_status(self, data):
        """Handle status updates from other devices"""
        device_id = data.get("device_id")
        if device_id and device_id != self.device_id:
            self.coordinated_devices[device_id] = {
                "status": data.get("status"),
                "last_seen": data.get("timestamp"),
                "message": data.get("message", "")
            }

    def handle_sensor_data(self, data):
        """Handle sensor data from other devices"""
        device_id = data.get("device_id")
        sensor_type = data.get("sensor_type")
        value = data.get("value")

        if device_id and device_id != self.device_id and sensor_type and value is not None:
            # Store in coordinated devices
            if device_id not in self.coordinated_devices:
                self.coordinated_devices[device_id] = {}

            self.coordinated_devices[device_id][sensor_type] = {
                "value": value,
                "timestamp": data.get("timestamp")
            }

            # Take coordinated action based on combined data
            self.take_coordinated_action(sensor_type, value, device_id)

    def take_coordinated_action(self, sensor_type, value, source_device):
        """Take coordinated action based on combined data from multiple devices"""
        if sensor_type == "temperature":
            # Check if this is an extreme value that requires coordinated response
            if value > 30:  # High temperature
                print(f"[{self.device_id}] Coordinated response: High temperature detected by {source_device}")
                # Could trigger coordinated cooling across multiple devices
                self.trigger_coordinated_response("cooling", {"target_device": source_device, "temperature": value})

        elif sensor_type == "motion":
            if value == 1:  # Motion detected
                print(f"[{self.device_id}] Coordinated response: Motion detected by {source_device}")
                # Could trigger coordinated lighting across multiple devices
                self.trigger_coordinated_response("lighting", {"target_area": source_device})

    def trigger_coordinated_response(self, action_type, params):
        """Trigger a coordinated response across the network"""
        command = {
            "command": "coordinated_action",
            "action_type": action_type,
            "params": params,
            "originator": self.device_id,
            "timestamp": datetime.now().isoformat()
        }

        topic = "physical_ai/network/action"
        self.client.publish(topic, json.dumps(command))
        print(f"[{self.device_id}] Published coordinated action: {command}")

    def publish_sensor_data(self, sensor_type, value):
        """Publish sensor data to the network"""
        if not self.connected:
            return

        data = {
            "sensor_type": sensor_type,
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "device_id": self.device_id,
            "location": f"area_{random.randint(1, 5)}"  # Simulate different locations
        }

        topic = f"physical_ai/{sensor_type}"
        self.client.publish(topic, json.dumps(data))

    def publish_device_info(self):
        """Publish device information"""
        info = {
            "device_id": self.device_id,
            "capabilities": ["temperature", "motion", "light"],
            "location": f"area_{random.randint(1, 5)}",
            "timestamp": datetime.now().isoformat()
        }

        topic = f"physical_ai/device/{self.device_id}/info"
        self.client.publish(topic, json.dumps(info))

    def sync_with_network(self):
        """Request synchronization with the network"""
        sync_request = {
            "request": "sync",
            "device_id": self.device_id,
            "timestamp": datetime.now().isoformat()
        }

        topic = "physical_ai/network/sync"
        self.client.publish(topic, json.dumps(sync_request))

def run_networked_ai_demo():
    """Run a demonstration of networked Physical AI systems"""
    print("Networked Physical AI Systems Demo")
    print("==================================")
    print("This example demonstrates multiple Physical AI systems communicating")
    print("and coordinating their actions through MQTT messaging.\n")

    # Create multiple networked devices
    devices = []
    for i in range(3):
        device = NetworkedPhysicalAI(f"device_{i+1}")
        devices.append(device)

    # Connect all devices
    for device in devices:
        if device.connect():
            print(f"Connected {device.device_id}")
        else:
            print(f"Failed to connect {device.device_id}")

    print(f"\nStarting simulation with {len(devices)} networked devices...")

    # Simulate sensor readings and network activity
    for cycle in range(10):
        print(f"\n--- Cycle {cycle+1} ---")

        for device in devices:
            # Simulate sensor readings
            temp_reading = 20 + random.uniform(-3, 5)
            motion_reading = 1 if random.random() > 0.7 else 0
            light_reading = 200 + random.uniform(-50, 100)

            # Publish sensor data
            device.publish_sensor_data("temperature", round(temp_reading, 2))
            device.publish_sensor_data("motion", motion_reading)
            device.publish_sensor_data("light", round(light_reading, 2))

            time.sleep(0.1)  # Small delay between publications

        # Print network status
        print(f"Network status: {len(devices[0].coordinated_devices)} other devices seen")

        # Show recent messages for first device
        recent_msgs = devices[0].received_messages[-3:]  # Last 3 messages
        if recent_msgs:
            print("Recent network activity:")
            for msg in recent_msgs:
                print(f"  {msg['topic']}: {msg['data']}")

        time.sleep(2)  # Wait between cycles

    # Print final summary
    print(f"\nFinal network status:")
    for device in devices:
        print(f"- {device.device_id}: {len(device.coordinated_devices)} other devices known")
        print(f"  Messages received: {len(device.received_messages)}")

if __name__ == "__main__":
    run_networked_ai_demo()
```

## Network Fallback and Redundancy

When designing networked Physical AI systems, it's important to implement fallback mechanisms for when network communication fails:

```python
class NetworkWithFallback:
    """
    A Physical AI system with network fallback capabilities
    """
    def __init__(self, device_id, broker="localhost", port=1883):
        self.device_id = device_id
        self.main_broker = broker
        self.main_port = port
        self.fallback_brokers = [("backup-server", 1883), ("cloud-mqtt", 1884)]

        self.primary_client = mqtt.Client(f"{device_id}_primary")
        self.connected = False
        self.network_status = "primary"
        self.fallback_active = False

        # Local data storage for offline operation
        self.local_data_buffer = []
        self.local_decision_cache = {}

    def connect_with_fallback(self):
        """Attempt to connect with fallback options"""
        # Try primary connection
        if self._attempt_connection(self.main_broker, self.main_port):
            self.network_status = "primary"
            self.fallback_active = False
            return True

        # Try fallback connections
        for fallback_broker, fallback_port in self.fallback_brokers:
            if self._attempt_connection(fallback_broker, fallback_port):
                self.network_status = f"fallback_{fallback_broker}"
                self.fallback_active = True
                print(f"Using fallback connection to {fallback_broker}:{fallback_port}")
                return True

        # If all connections fail, operate in offline mode
        self.network_status = "offline"
        self.fallback_active = True
        print("Operating in offline mode - using local data and decisions")
        return False

    def _attempt_connection(self, broker, port):
        """Attempt to connect to a specific broker"""
        try:
            self.primary_client.connect(broker, port, 60)
            self.primary_client.loop_start()
            # Verify connection
            time.sleep(0.5)
            return True
        except Exception as e:
            print(f"Failed to connect to {broker}:{port} - {e}")
            return False

    def publish_with_buffering(self, topic, data):
        """Publish data with buffering for offline operation"""
        if self.network_status == "offline":
            # Buffer data for later transmission
            self.local_data_buffer.append({
                "topic": topic,
                "data": data,
                "timestamp": time.time()
            })
            print(f"Buffered message for offline transmission: {topic}")
            return False
        else:
            # Publish normally
            result = self.primary_client.publish(topic, json.dumps(data))
            return result.rc == 0

    def sync_buffered_data(self):
        """Sync buffered data when network becomes available"""
        if self.network_status != "offline" and self.local_data_buffer:
            print(f"Syncing {len(self.local_data_buffer)} buffered messages...")
            successful_syncs = 0

            for buffered_item in self.local_data_buffer[:]:  # Copy list to iterate safely
                result = self.primary_client.publish(buffered_item["topic"],
                                                   json.dumps(buffered_item["data"]))
                if result.rc == 0:
                    self.local_data_buffer.remove(buffered_item)
                    successful_syncs += 1

            print(f"Synced {successful_syncs} messages, {len(self.local_data_buffer)} remain")
```

## Safety Considerations for Networked AI

When implementing networked Physical AI systems, safety is crucial:

1. **Network Isolation**: Use separate networks for critical systems
2. **Authentication**: Implement device authentication to prevent unauthorized access
3. **Encryption**: Encrypt communications for sensitive data
4. **Rate Limiting**: Prevent network flooding that could overwhelm systems
5. **Fail-Safe Defaults**: Ensure systems default to safe states when network fails

## Exercises

1. **Network Topology**: Design different network topologies (star, mesh, hybrid) for Physical AI systems
2. **Leader Election**: Implement a leader election algorithm for distributed decision making
3. **Security Enhancement**: Add authentication and encryption to the communication protocol
4. **Scalability**: Create a system that can handle hundreds of networked devices efficiently

## Summary

In this lesson, we explored networked Physical AI systems that can communicate and coordinate with each other. We implemented MQTT-based communication protocols, demonstrated networked sensor coordination, and discussed fallback mechanisms for network failures.

Networked Physical AI systems enable distributed intelligence and coordinated actions across multiple devices, opening up possibilities for complex, large-scale Physical AI applications. Proper safety considerations and fallback mechanisms are essential for reliable operation.

The concepts learned in this chapter complete the advanced Physical AI systems curriculum, providing a solid foundation for developing sophisticated Physical AI applications that combine sensor fusion, advanced control, and networked coordination.