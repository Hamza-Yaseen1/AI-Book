#!/usr/bin/env python3
"""
Lesson 3: Collaborative and Networked Physical AI
Example 4: Coordinated Response System for Networked Physical AI
"""

import paho.mqtt.client as mqtt
import json
import time
import threading
import random
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

class CoordinationAction(Enum):
    """Types of coordinated actions that can be taken"""
    LIGHTING_CONTROL = "lighting_control"
    TEMPERATURE_ADJUSTMENT = "temperature_adjustment"
    SECURITY_RESPONSE = "security_response"
    EMERGENCY_PROCEDURE = "emergency_procedure"
    RESOURCE_SHARING = "resource_sharing"
    LOAD_BALANCING = "load_balancing"

class CoordinatedResponseSystem:
    """
    A system for coordinating responses across multiple networked Physical AI devices
    """
    def __init__(self, device_id: str, broker: str = "localhost", port: int = 1883):
        self.device_id = device_id
        self.client = mqtt.Client(device_id)

        # MQTT callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.broker = broker
        self.port = port
        self.connected = False

        # Coordination data
        self.registered_devices = {}  # {device_id: device_info}
        self.active_coordination_tasks = {}  # {task_id: task_info}
        self.coordination_history = []  # Historical coordination records
        self.device_capabilities = {}  # {device_id: [capabilities]}
        self.pending_requests = {}  # {request_id: request_info}

        # Coordination parameters
        self.coordination_threshold = 0.7  # Threshold for coordination participation
        self.response_timeout = 5.0  # Timeout for coordination responses
        self.max_participants = 10  # Maximum participants in coordination

    def on_connect(self, client, userdata, flags, rc):
        """Handle MQTT connection"""
        if rc == 0:
            print(f"[{self.device_id}] Connected to MQTT broker at {self.broker}:{self.port}")
            self.connected = True

            # Subscribe to coordination topics
            client.subscribe("physical_ai/coordination/request/+")
            client.subscribe("physical_ai/coordination/response/+")
            client.subscribe("physical_ai/coordination/task/+")
            client.subscribe("physical_ai/coordination/status")
            client.subscribe(f"physical_ai/devices/{self.device_id}/register")

        else:
            print(f"[{self.device_id}] Failed to connect to MQTT broker, return code {rc}")
            self.connected = False

    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        try:
            data = json.loads(msg.payload.decode())
            print(f"[{self.device_id}] Received message on {msg.topic}: {data}")

            # Route message based on topic
            if "coordination/request" in msg.topic:
                self.handle_coordination_request(data)
            elif "coordination/response" in msg.topic:
                self.handle_coordination_response(data)
            elif "coordination/task" in msg.topic:
                self.handle_coordination_task(data)
            elif "coordination/status" in msg.topic:
                self.handle_coordination_status(data)
            elif f"devices/{self.device_id}/register" in msg.topic:
                self.handle_device_registration(data)

        except json.JSONDecodeError:
            print(f"[{self.device_id}] Received non-JSON message: {msg.payload.decode()}")
        except Exception as e:
            print(f"[{self.device_id}] Error processing message: {e}")

    def on_disconnect(self, client, userdata, rc):
        """Handle MQTT disconnection"""
        print(f"[{self.device_id}] Disconnected from MQTT broker")
        self.connected = False

    def connect(self) -> bool:
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
            print(f"[{self.device_id}] Error connecting to MQTT broker: {e}")
            return False

    def disconnect(self):
        """Disconnect from the MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        print(f"[{self.device_id}] Disconnected from MQTT broker")

    def register_device(self, capabilities: List[str]):
        """Register this device with the coordination network"""
        registration_data = {
            "device_id": self.device_id,
            "capabilities": capabilities,
            "timestamp": datetime.now().isoformat(),
            "status": "online",
            "location": f"zone_{random.randint(1, 5)}"  # Simulate location
        }

        topic = f"physical_ai/devices/{self.device_id}/register"
        self.client.publish(topic, json.dumps(registration_data))
        print(f"[{self.device_id}] Registered with capabilities: {capabilities}")

        # Store local capabilities
        self.device_capabilities[self.device_id] = capabilities

    def initiate_coordination(self, action_type: CoordinationAction, parameters: Dict,
                           priority: str = "normal") -> str:
        """
        Initiate a coordination task across the network

        Args:
            action_type: Type of action to coordinate
            parameters: Parameters for the action
            priority: Priority level of the coordination request

        Returns:
            str: Task ID for the coordination
        """
        task_id = f"task_{int(time.time())}_{random.randint(1000, 9999)}"

        coordination_request = {
            "task_id": task_id,
            "action_type": action_type.value,
            "parameters": parameters,
            "initiator": self.device_id,
            "timestamp": datetime.now().isoformat(),
            "priority": priority,
            "required_capabilities": self._get_required_capabilities(action_type)
        }

        # Publish coordination request
        topic = f"physical_ai/coordination/request/{action_type.value}"
        self.client.publish(topic, json.dumps(coordination_request))

        # Store as active task
        self.active_coordination_tasks[task_id] = {
            "request": coordination_request,
            "participants": [],
            "responses": {},
            "status": "initiated"
        }

        print(f"[{self.device_id}] Initiated coordination task {task_id} for {action_type.value}")
        return task_id

    def _get_required_capabilities(self, action_type: CoordinationAction) -> List[str]:
        """Get required capabilities for a specific action type"""
        capability_map = {
            CoordinationAction.LIGHTING_CONTROL: ["lighting", "dimming"],
            CoordinationAction.TEMPERATURE_ADJUSTMENT: ["heating", "cooling", "temperature_control"],
            CoordinationAction.SECURITY_RESPONSE: ["camera", "alarm", "motion_detection"],
            CoordinationAction.EMERGENCY_PROCEDURE: ["emergency_stop", "notification"],
            CoordinationAction.RESOURCE_SHARING: ["shared_resource", "load_handling"],
            CoordinationAction.LOAD_BALANCING: ["power_management", "efficiency"]
        }

        return capability_map.get(action_type, [])

    def handle_coordination_request(self, data: Dict):
        """Handle incoming coordination requests"""
        task_id = data["task_id"]
        action_type = data["action_type"]
        required_capabilities = data.get("required_capabilities", [])
        initiator = data["initiator"]

        # Check if this device can participate
        if self._can_participate(required_capabilities):
            print(f"[{self.device_id}] Can participate in coordination task {task_id}")

            # Send response indicating participation
            response = {
                "task_id": task_id,
                "device_id": self.device_id,
                "status": "ready",
                "capabilities": self.device_capabilities.get(self.device_id, []),
                "timestamp": datetime.now().isoformat(),
                "initiator": initiator
            }

            response_topic = f"physical_ai/coordination/response/{task_id}"
            self.client.publish(response_topic, json.dumps(response))

            # Update local coordination task
            if task_id in self.active_coordination_tasks:
                self.active_coordination_tasks[task_id]["participants"].append(self.device_id)
            else:
                self.active_coordination_tasks[task_id] = {
                    "request": data,
                    "participants": [self.device_id],
                    "responses": {},
                    "status": "waiting_participants"
                }

    def _can_participate(self, required_capabilities: List[str]) -> bool:
        """Check if this device can participate in coordination"""
        if not required_capabilities:
            return True  # No specific capabilities required

        device_caps = self.device_capabilities.get(self.device_id, [])
        return any(cap in device_caps for cap in required_capabilities)

    def handle_coordination_response(self, data: Dict):
        """Handle responses to coordination requests"""
        task_id = data["task_id"]
        responder = data["device_id"]

        if task_id in self.active_coordination_tasks:
            # Add responder to participants
            if responder not in self.active_coordination_tasks[task_id]["participants"]:
                self.active_coordination_tasks[task_id]["participants"].append(responder)

            # Store response
            self.active_coordination_tasks[task_id]["responses"][responder] = data

            print(f"[{self.device_id}] Received coordination response from {responder} for task {task_id}")

    def execute_coordination_task(self, task_id: str):
        """Execute a coordination task with all participants"""
        if task_id not in self.active_coordination_tasks:
            print(f"[{self.device_id}] Task {task_id} not found")
            return False

        task = self.active_coordination_tasks[task_id]
        if len(task["participants"]) < 2:  # Need at least 2 participants for coordination
            print(f"[{self.device_id}] Not enough participants for coordination task {task_id}")
            return False

        # Prepare task execution
        action_type = task["request"]["action_type"]
        parameters = task["request"]["parameters"]

        coordination_task = {
            "task_id": task_id,
            "action_type": action_type,
            "parameters": parameters,
            "participants": task["participants"],
            "execution_time": datetime.now().isoformat(),
            "initiator": task["request"]["initiator"]
        }

        # Publish coordination task to all participants
        task_topic = f"physical_ai/coordination/task/{task_id}"
        self.client.publish(task_topic, json.dumps(coordination_task))

        # Execute locally if this device is a participant
        if self.device_id in task["participants"]:
            self._execute_local_coordination(action_type, parameters)

        # Update task status
        task["status"] = "executing"

        print(f"[{self.device_id}] Executing coordination task {task_id} with {len(task['participants'])} participants")
        return True

    def _execute_local_coordination(self, action_type: str, parameters: Dict):
        """Execute coordination action locally"""
        print(f"[{self.device_id}] Executing local coordination action: {action_type}")

        # Simulate different coordination actions
        if action_type == "lighting_control":
            self._execute_lighting_coordination(parameters)
        elif action_type == "temperature_adjustment":
            self._execute_temperature_coordination(parameters)
        elif action_type == "security_response":
            self._execute_security_coordination(parameters)
        elif action_type == "emergency_procedure":
            self._execute_emergency_coordination(parameters)
        else:
            print(f"[{self.device_id}] Unknown action type: {action_type}")

    def _execute_lighting_coordination(self, parameters: Dict):
        """Execute coordinated lighting action"""
        brightness = parameters.get("brightness", 50)
        duration = parameters.get("duration", 10)

        print(f"[{self.device_id}] Coordinated lighting: Setting brightness to {brightness}% for {duration}s")
        # In a real system, this would control actual lights

    def _execute_temperature_coordination(self, parameters: Dict):
        """Execute coordinated temperature action"""
        target_temp = parameters.get("target_temperature", 22)
        zone = parameters.get("zone", "all")

        print(f"[{self.device_id}] Coordinated temperature: Setting to {target_temp}°C in zone {zone}")
        # In a real system, this would control HVAC systems

    def _execute_security_coordination(self, parameters: Dict):
        """Execute coordinated security action"""
        area = parameters.get("area", "common")
        response_type = parameters.get("response_type", "monitor")

        print(f"[{self.device_id}] Coordinated security: {response_type} in area {area}")
        # In a real system, this would activate security systems

    def _execute_emergency_coordination(self, parameters: Dict):
        """Execute coordinated emergency procedure"""
        emergency_type = parameters.get("type", "general")
        evacuation_route = parameters.get("evacuation_route", "primary")

        print(f"[{self.device_id}] Coordinated emergency: {emergency_type} - using {evacuation_route} route")
        # In a real system, this would trigger emergency protocols

    def handle_coordination_task(self, data: Dict):
        """Handle coordination tasks assigned to this device"""
        task_id = data["task_id"]
        action_type = data["action_type"]
        parameters = data["parameters"]

        print(f"[{self.device_id}] Received coordination task {task_id}: {action_type}")

        # Execute the task locally
        self._execute_local_coordination(action_type, parameters)

        # Send completion confirmation
        completion_data = {
            "task_id": task_id,
            "device_id": self.device_id,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type
        }

        completion_topic = f"physical_ai/coordination/completion/{task_id}"
        self.client.publish(completion_topic, json.dumps(completion_data))

    def handle_coordination_status(self, data: Dict):
        """Handle coordination status updates"""
        status_type = data.get("status_type")
        message = data.get("message", "")

        print(f"[{self.device_id}] Coordination status: {status_type} - {message}")

    def handle_device_registration(self, data: Dict):
        """Handle device registration messages"""
        device_id = data["device_id"]
        capabilities = data["capabilities"]

        self.registered_devices[device_id] = data
        self.device_capabilities[device_id] = capabilities

        print(f"[{self.device_id}] Registered device {device_id} with capabilities: {capabilities}")

    def get_network_status(self) -> Dict:
        """Get current coordination network status"""
        return {
            "device_id": self.device_id,
            "connected": self.connected,
            "registered_devices": len(self.registered_devices),
            "active_coordination_tasks": len(self.active_coordination_tasks),
            "coordination_history_count": len(self.coordination_history),
            "pending_requests": len(self.pending_requests),
            "my_capabilities": self.device_capabilities.get(self.device_id, [])
        }

    def request_resource_sharing(self, resource_type: str, quantity: float) -> bool:
        """Request sharing of resources from the network"""
        request_data = {
            "request_id": f"req_{int(time.time())}_{random.randint(1000, 9999)}",
            "resource_type": resource_type,
            "quantity": quantity,
            "requester": self.device_id,
            "timestamp": datetime.now().isoformat(),
            "priority": "normal"
        }

        topic = "physical_ai/resources/request"
        self.client.publish(topic, json.dumps(request_data))
        print(f"[{self.device_id}] Requested {quantity} of {resource_type}")

        return True

def run_coordinated_response_demo():
    """Run a demonstration of coordinated response systems"""
    print("Coordinated Response System Demo")
    print("==============================")
    print("This example demonstrates how multiple Physical AI systems can coordinate")
    print("their responses to events and share resources across the network.\n")

    # Create multiple coordinated response systems
    devices = []
    for i in range(3):
        device = CoordinatedResponseSystem(f"coord_device_{i+1}")
        devices.append(device)

    # Connect all devices
    print("Connecting coordinated response systems...")
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

    # Register devices with their capabilities
    capabilities_map = [
        ["lighting", "temperature_control", "motion_detection"],
        ["heating", "cooling", "humidity_control"],
        ["camera", "alarm", "security_monitoring"]
    ]

    print(f"\nRegistering devices with capabilities...")
    for device, caps in zip(connected_devices, capabilities_map):
        device.register_device(caps)

    print(f"\nStarting coordinated response simulation...")

    try:
        # Simulate different coordination scenarios
        for cycle in range(5):
            print(f"\n--- Coordination Cycle {cycle+1} ---")

            # Scenario 1: Lighting coordination
            if cycle == 0:
                print("Initiating coordinated lighting control...")
                coordinator = connected_devices[0]
                task_id = coordinator.initiate_coordination(
                    CoordinationAction.LIGHTING_CONTROL,
                    {"brightness": 75, "duration": 30, "area": "common_space"},
                    "normal"
                )
                time.sleep(2)
                coordinator.execute_coordination_task(task_id)

            # Scenario 2: Temperature coordination
            elif cycle == 1:
                print("Initiating coordinated temperature adjustment...")
                coordinator = connected_devices[1]
                task_id = coordinator.initiate_coordination(
                    CoordinationAction.TEMPERATURE_ADJUSTMENT,
                    {"target_temperature": 23.5, "zone": "office", "duration": 3600},
                    "normal"
                )
                time.sleep(2)
                coordinator.execute_coordination_task(task_id)

            # Scenario 3: Security response
            elif cycle == 2:
                print("Initiating coordinated security response...")
                coordinator = connected_devices[2]
                task_id = coordinator.initiate_coordination(
                    CoordinationAction.SECURITY_RESPONSE,
                    {"area": "entrance", "response_type": "monitor_and_alert", "duration": 600},
                    "high"
                )
                time.sleep(2)
                coordinator.execute_coordination_task(task_id)

            # Scenario 4: Resource sharing request
            elif cycle == 3:
                print("Requesting resource sharing...")
                requester = connected_devices[0]
                requester.request_resource_sharing("computing_power", 0.5)

            # Scenario 5: Emergency procedure
            elif cycle == 4:
                print("Initiating coordinated emergency procedure...")
                coordinator = connected_devices[0]
                task_id = coordinator.initiate_coordination(
                    CoordinationAction.EMERGENCY_PROCEDURE,
                    {"type": "fire_drill", "evacuation_route": "primary", "assembly_point": "parking_lot"},
                    "critical"
                )
                time.sleep(2)
                coordinator.execute_coordination_task(task_id)

            # Print network status periodically
            print(f"\nNetwork Status:")
            for device in connected_devices:
                status = device.get_network_status()
                print(f"  {device.device_id}: {status['registered_devices']} registered, "
                      f"{status['active_coordination_tasks']} active tasks")

            time.sleep(3)  # Wait between scenarios

        # Final summary
        print(f"\n=== FINAL COORDINATION SUMMARY ===")
        for device in connected_devices:
            status = device.get_network_status()
            print(f"\nDevice {device.device_id}:")
            print(f"  - Registered devices: {status['registered_devices']}")
            print(f"  - Active tasks: {status['active_coordination_tasks']}")
            print(f"  - My capabilities: {status['my_capabilities']}")
            print(f"  - Connected: {status['connected']}")

    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        # Clean shutdown
        print("\nShutting down coordinated response systems...")
        for device in connected_devices:
            device.disconnect()
        print("All coordinated systems disconnected.")

def main():
    run_coordinated_response_demo()

if __name__ == "__main__":
    main()