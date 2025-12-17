#!/usr/bin/env python3
"""
Lesson 3: Collaborative and Networked Physical AI
Project: Networked Sensor Network with Coordinated Response
"""

import paho.mqtt.client as mqtt
import json
import time
import threading
import random
from datetime import datetime
import copy

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
            "humidity": 45.0,
            "motion": 0,
            "light": 300
        }
        self.coordinated_devices = {}  # Track other devices
        self.network_topology = {}  # Track network connections
        self.local_actions = []  # Track actions taken by this device
        self.global_objectives = {}  # Global objectives for coordinated behavior

        # Communication settings
        self.message_history = []  # Keep track of sent messages
        self.heartbeat_interval = 10  # Send heartbeat every 10 seconds
        self.last_heartbeat = 0

        # Thread management
        self.running = False
        self.heartbeat_thread = None

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Device {self.device_id} connected to MQTT broker at {self.broker}:{self.port}")
            self.connected = True

            # Subscribe to relevant topics
            client.subscribe("physical_ai/sensor_data/+")
            client.subscribe("physical_ai/coordinated_action")
            client.subscribe("physical_ai/heartbeat/+")
            client.subscribe("physical_ai/objective/+")  # Global objectives
            client.subscribe(f"physical_ai/device/{self.device_id}/command")  # Direct commands
            client.subscribe("physical_ai/emergency/+")  # Emergency broadcasts
        else:
            print(f"Device {self.device_id} failed to connect, return code {rc}")
            self.connected = False

    def on_message(self, client, userdata, msg):
        """Handle incoming messages"""
        try:
            data = json.loads(msg.payload.decode())

            # Add to received messages
            message_entry = {
                "topic": msg.topic,
                "data": data,
                "timestamp": time.time(),
                "sender": data.get("device_id", "unknown")
            }
            self.received_messages.append(message_entry)

            print(f"[{self.device_id}] Received from {msg.topic}: {data}")

            # Process based on topic
            if "command" in msg.topic:
                self.handle_direct_command(data)
            elif "heartbeat" in msg.topic:
                self.handle_heartbeat(data)
            elif "sensor_data" in msg.topic:
                self.handle_sensor_data(data)
            elif "coordinated_action" in msg.topic:
                self.handle_coordinated_action(data)
            elif "objective" in msg.topic:
                self.handle_global_objective(data)
            elif "emergency" in msg.topic:
                self.handle_emergency(data)

        except json.JSONDecodeError:
            print(f"[{self.device_id}] Received non-JSON message: {msg.payload.decode()}")
        except Exception as e:
            print(f"[{self.device_id}] Error processing message: {e}")

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

            if self.connected:
                # Start heartbeat thread
                self.running = True
                self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
                self.heartbeat_thread.start()

                # Announce presence
                self.announce_presence()

            return self.connected
        except Exception as e:
            print(f"Error connecting device {self.device_id}: {e}")
            return False

    def disconnect(self):
        """Disconnect from the MQTT broker"""
        self.running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=2)

        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        print(f"Device {self.device_id} disconnected from MQTT broker")

    def _heartbeat_loop(self):
        """Send periodic heartbeats to maintain presence in network"""
        while self.running and self.connected:
            current_time = time.time()
            if current_time - self.last_heartbeat >= self.heartbeat_interval:
                self.send_heartbeat()
                self.last_heartbeat = current_time

            time.sleep(1)  # Check every second

    def announce_presence(self):
        """Announce device presence to the network"""
        presence_data = {
            "device_id": self.device_id,
            "timestamp": datetime.now().isoformat(),
            "capabilities": list(self.local_sensors.keys()),
            "location": f"area_{random.randint(1, 10)}",  # Simulate different locations
            "status": "operational"
        }

        topic = f"physical_ai/presence/{self.device_id}"
        self.client.publish(topic, json.dumps(presence_data))
        print(f"[{self.device_id}] Announced presence: {presence_data}")

    def send_heartbeat(self):
        """Send heartbeat to maintain network presence"""
        heartbeat_data = {
            "device_id": self.device_id,
            "timestamp": datetime.now().isoformat(),
            "status": "operational",
            "uptime": time.time(),  # Simulated uptime
            "load": random.uniform(0.1, 0.8)  # Simulated system load
        }

        topic = f"physical_ai/heartbeat/{self.device_id}"
        self.client.publish(topic, json.dumps(heartbeat_data))

    def handle_direct_command(self, data):
        """Handle direct commands to this device"""
        command = data.get("command")
        if command == "identify":
            self.publish_device_info()
        elif command == "sync":
            self.sync_with_network()
        elif command == "status_request":
            self.publish_status_report()
        elif command == "calibrate":
            self.calibrate_sensors()
        elif command == "emergency_stop":
            self.emergency_procedure()

    def handle_heartbeat(self, data):
        """Handle heartbeat messages from other devices"""
        sender_id = data.get("device_id")
        if sender_id and sender_id != self.device_id:
            self.coordinated_devices[sender_id] = {
                "status": data.get("status"),
                "last_seen": data.get("timestamp"),
                "load": data.get("load", 0),
                "uptime": data.get("uptime", 0)
            }

    def handle_sensor_data(self, data):
        """Handle sensor data from other devices"""
        sender_id = data.get("device_id")
        sensor_type = data.get("sensor_type")
        value = data.get("value")

        if sender_id and sender_id != self.device_id and sensor_type and value is not None:
            # Store in coordinated devices
            if sender_id not in self.coordinated_devices:
                self.coordinated_devices[sender_id] = {}

            self.coordinated_devices[sender_id][sensor_type] = {
                "value": value,
                "timestamp": data.get("timestamp"),
                "quality": data.get("quality", "unknown")
            }

            # Take coordinated action based on combined data
            self.take_coordinated_action(sensor_type, value, sender_id)

    def handle_coordinated_action(self, data):
        """Handle coordinated action requests from the network"""
        action_type = data.get("action_type")
        params = data.get("params", {})
        originator = data.get("originator")

        if originator != self.device_id:  # Don't process own actions
            print(f"[{self.device_id}] Received coordinated action: {action_type} from {originator}")

            # Execute action if it's relevant to this device
            if self.should_execute_action(action_type, params):
                self.execute_coordinated_action(action_type, params)

    def handle_global_objective(self, data):
        """Handle global objectives broadcast to the network"""
        objective_id = data.get("objective_id")
        objective = data.get("objective")
        priority = data.get("priority", "normal")

        self.global_objectives[objective_id] = {
            "objective": objective,
            "priority": priority,
            "timestamp": data.get("timestamp"),
            "originator": data.get("originator")
        }

        print(f"[{self.device_id}] Received global objective: {objective} (Priority: {priority})")

    def handle_emergency(self, data):
        """Handle emergency broadcasts"""
        emergency_type = data.get("type")
        severity = data.get("severity", "medium")
        affected_area = data.get("affected_area")

        print(f"[{self.device_id}] EMERGENCY ALERT: {emergency_type} (Severity: {severity})")

        # Execute emergency procedure
        self.emergency_procedure(emergency_type, severity)

    def take_coordinated_action(self, sensor_type, value, source_device):
        """Take coordinated action based on combined data from multiple devices"""
        if sensor_type == "temperature":
            # Check if this is an extreme value that requires coordinated response
            if value > 30:  # High temperature
                print(f"[{self.device_id}] Coordinated response: High temperature ({value}°C) detected by {source_device}")
                # Trigger coordinated cooling across multiple devices
                self.trigger_coordinated_response("cooling", {
                    "target_device": source_device,
                    "temperature": value,
                    "response_type": "temperature_alert"
                })
            elif value < 15:  # Low temperature
                print(f"[{self.device_id}] Coordinated response: Low temperature ({value}°C) detected by {source_device}")
                self.trigger_coordinated_response("heating", {
                    "target_device": source_device,
                    "temperature": value,
                    "response_type": "temperature_alert"
                })

        elif sensor_type == "motion":
            if value == 1:  # Motion detected
                print(f"[{self.device_id}] Coordinated response: Motion detected by {source_device}")
                # Trigger coordinated lighting across multiple devices
                self.trigger_coordinated_response("lighting", {
                    "target_area": source_device,
                    "response_type": "motion_alert"
                })

        elif sensor_type == "humidity":
            if value > 80:  # High humidity
                print(f"[{self.device_id}] Coordinated response: High humidity ({value}%) detected by {source_device}")
                self.trigger_coordinated_response("dehumidify", {
                    "target_device": source_device,
                    "humidity": value,
                    "response_type": "humidity_alert"
                })

    def trigger_coordinated_response(self, action_type, params):
        """Trigger a coordinated response across the network"""
        command = {
            "command": "coordinated_action",
            "action_type": action_type,
            "params": params,
            "originator": self.device_id,
            "timestamp": datetime.now().isoformat(),
            "coordination_level": "network"  # Could be 'local', 'regional', 'global'
        }

        topic = "physical_ai/coordinated_action"
        self.client.publish(topic, json.dumps(command))
        print(f"[{self.device_id}] Published coordinated action: {action_type}")

    def should_execute_action(self, action_type, params):
        """Determine if this device should execute a coordinated action"""
        # For now, execute all relevant actions
        # In a real system, this would consider device capabilities, location, etc.
        return True

    def execute_coordinated_action(self, action_type, params):
        """Execute a coordinated action"""
        # Log the action
        action_log = {
            "action_type": action_type,
            "params": params,
            "timestamp": datetime.now().isoformat(),
            "executor": self.device_id
        }
        self.local_actions.append(action_log)

        # Execute the action (in simulation, just print)
        print(f"[{self.device_id}] Executing coordinated action: {action_type} with params: {params}")

        # In a real system, this would control actual devices
        if action_type == "cooling":
            self._simulate_cooling_action(params)
        elif action_type == "heating":
            self._simulate_heating_action(params)
        elif action_type == "lighting":
            self._simulate_lighting_action(params)
        elif action_type == "dehumidify":
            self._simulate_dehumidify_action(params)

    def _simulate_cooling_action(self, params):
        """Simulate cooling action"""
        print(f"[{self.device_id}] Simulating cooling action for {params.get('target_device')}")

    def _simulate_heating_action(self, params):
        """Simulate heating action"""
        print(f"[{self.device_id}] Simulating heating action for {params.get('target_device')}")

    def _simulate_lighting_action(self, params):
        """Simulate lighting action"""
        print(f"[{self.device_id}] Simulating lighting action for {params.get('target_area')}")

    def _simulate_dehumidify_action(self, params):
        """Simulate dehumidifying action"""
        print(f"[{self.device_id}] Simulating dehumidifying action for {params.get('target_device')}")

    def publish_sensor_data(self, sensor_type, value, additional_data=None):
        """Publish sensor data to the network"""
        if not self.connected:
            return False

        data = {
            "sensor_type": sensor_type,
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "device_id": self.device_id,
            "location": f"area_{random.randint(1, 10)}",  # Simulate different locations
            "quality": "good",
            "additional_data": additional_data or {}
        }

        topic = f"physical_ai/sensor_data/{sensor_type}"
        result = self.client.publish(topic, json.dumps(data))

        if result.rc == 0:
            print(f"[{self.device_id}] Published sensor data: {sensor_type} = {value}")
            return True
        else:
            print(f"[{self.device_id}] Failed to publish sensor data")
            return False

    def publish_device_info(self):
        """Publish device information"""
        info = {
            "device_id": self.device_id,
            "capabilities": list(self.local_sensors.keys()),
            "location": f"area_{random.randint(1, 10)}",
            "timestamp": datetime.now().isoformat(),
            "status": "operational",
            "firmware_version": "1.0.0",
            "manufacturer": "PhysicalAI Corp"
        }

        topic = f"physical_ai/device/{self.device_id}/info"
        self.client.publish(topic, json.dumps(info))
        print(f"[{self.device_id}] Published device info: {info}")

    def publish_status_report(self):
        """Publish comprehensive status report"""
        status_report = {
            "device_id": self.device_id,
            "timestamp": datetime.now().isoformat(),
            "status": "operational",
            "sensors": copy.deepcopy(self.local_sensors),
            "connected_devices": len(self.coordinated_devices),
            "messages_received": len(self.received_messages),
            "actions_executed": len(self.local_actions),
            "system_load": random.uniform(0.1, 0.8)
        }

        topic = f"physical_ai/status/{self.device_id}/report"
        self.client.publish(topic, json.dumps(status_report))
        print(f"[{self.device_id}] Published status report")

    def sync_with_network(self):
        """Request synchronization with the network"""
        sync_request = {
            "request": "sync",
            "device_id": self.device_id,
            "timestamp": datetime.now().isoformat(),
            "request_type": "full_sync"
        }

        topic = "physical_ai/network/sync"
        self.client.publish(topic, json.dumps(sync_request))
        print(f"[{self.device_id}] Sent sync request")

    def calibrate_sensors(self):
        """Calibrate local sensors"""
        print(f"[{self.device_id}] Calibrating sensors...")
        # Simulate calibration
        for sensor in self.local_sensors:
            self.local_sensors[sensor] = random.uniform(20, 25)  # Reset to normal values
        print(f"[{self.device_id}] Sensor calibration complete")

    def emergency_procedure(self, emergency_type="general", severity="medium"):
        """Execute emergency procedure"""
        print(f"[{self.device_id}] EXECUTING EMERGENCY PROCEDURE: {emergency_type} (Severity: {severity})")

        # Log emergency
        emergency_log = {
            "type": emergency_type,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "device_id": self.device_id
        }

        # Publish emergency notification
        topic = "physical_ai/emergency/alert"
        self.client.publish(topic, json.dumps(emergency_log))

        # In a real system, this would execute safety protocols
        print(f"[{self.device_id}] Emergency procedure completed")

    def get_network_status(self):
        """Get current network status"""
        return {
            "connected": self.connected,
            "coordinated_devices": len(self.coordinated_devices),
            "messages_received": len(self.received_messages),
            "actions_executed": len(self.local_actions),
            "known_devices": list(self.coordinated_devices.keys()),
            "global_objectives": len(self.global_objectives)
        }

def run_networked_ai_simulation():
    """Run a demonstration of networked Physical AI systems"""
    print("Networked Physical AI Systems Simulation")
    print("========================================")
    print("This example demonstrates multiple Physical AI systems communicating")
    print("and coordinating their actions through MQTT messaging.\n")

    # Create multiple networked devices
    num_devices = 4
    devices = []

    for i in range(num_devices):
        device = NetworkedPhysicalAI(f"device_{i+1}_{random.randint(100, 999)}")  # Add random number to make unique
        devices.append(device)

    # Connect all devices
    print("Connecting devices to MQTT network...")
    connected_devices = []
    for device in devices:
        if device.connect():
            connected_devices.append(device)
            print(f"✓ Connected {device.device_id}")
        else:
            print(f"✗ Failed to connect {device.device_id}")

    if not connected_devices:
        print("No devices connected. Please ensure MQTT broker is running.")
        return

    print(f"\nStarting simulation with {len(connected_devices)} networked devices...")

    try:
        # Simulate the network operation
        for cycle in range(15):
            print(f"\n--- Network Operation Cycle {cycle+1} ---")

            for device in connected_devices:
                # Simulate sensor readings
                temp_reading = 20 + random.uniform(-5, 8)  # Range: 15-28°C
                humidity_reading = 40 + random.uniform(-15, 20)  # Range: 25-60%
                motion_reading = 1 if random.random() > 0.85 else 0  # 15% chance of motion
                light_reading = 200 + random.uniform(-100, 300)  # Range: 100-500 lux

                # Update local sensors
                device.local_sensors["temperature"] = temp_reading
                device.local_sensors["humidity"] = humidity_reading
                device.local_sensors["motion"] = motion_reading
                device.local_sensors["light"] = light_reading

                # Publish sensor data
                device.publish_sensor_data("temperature", round(temp_reading, 2))
                device.publish_sensor_data("humidity", round(humidity_reading, 2))
                device.publish_sensor_data("motion", motion_reading)
                device.publish_sensor_data("light", round(light_reading, 2))

                # Occasionally publish additional info
                if cycle % 3 == 0:
                    device.publish_status_report()

                time.sleep(0.2)  # Small delay between publications

            # Print network status periodically
            if cycle % 3 == 0:
                print(f"\nNetwork Status:")
                for device in connected_devices[:2]:  # Show first 2 devices for brevity
                    status = device.get_network_status()
                    print(f"  {device.device_id}: {status['coordinated_devices']} peers, "
                          f"{status['messages_received']} msgs, {status['actions_executed']} actions")

            time.sleep(3)  # Wait between cycles

        # Simulate an emergency scenario
        print(f"\n--- EMERGENCY SCENARIO ---")
        print("Simulating high temperature emergency...")
        emergency_device = connected_devices[0]
        emergency_device.handle_emergency({
            "type": "high_temperature",
            "severity": "high",
            "affected_area": "area_5"
        })

        # Final network status
        print(f"\n=== FINAL NETWORK STATUS ===")
        for device in connected_devices:
            status = device.get_network_status()
            print(f"\nDevice {device.device_id}:")
            print(f"  - Connected: {status['connected']}")
            print(f"  - Known devices: {status['coordinated_devices']}")
            print(f"  - Messages received: {status['messages_received']}")
            print(f"  - Actions executed: {status['actions_executed']}")
            print(f"  - Global objectives: {status['global_objectives']}")

    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        # Clean shutdown
        print("\nShutting down networked devices...")
        for device in connected_devices:
            device.disconnect()
        print("All devices disconnected.")

def main():
    run_networked_ai_simulation()

if __name__ == "__main__":
    main()