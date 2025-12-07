#!/usr/bin/env python3
"""
Lesson 3: Collaborative and Networked Physical AI
Example 3: Network Fallback and Redundancy for Physical AI Systems
"""

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime
import threading
import queue
import os

class NetworkWithFallback:
    """
    A Physical AI system with network fallback capabilities
    """
    def __init__(self, device_id, primary_broker="localhost", primary_port=1883):
        self.device_id = device_id
        self.primary_broker = primary_broker
        self.primary_port = primary_port

        # Fallback configuration
        self.fallback_brokers = [
            ("backup-server", 1883),
            ("cloud-mqtt", 1884),
            ("local-mesh", 1883)
        ]

        # Client setup
        self.primary_client = mqtt.Client(f"{device_id}_primary")
        self.fallback_clients = []

        # Connection status
        self.connected = False
        self.network_status = "disconnected"
        self.fallback_active = False
        self.current_broker = None
        self.current_port = None

        # Data storage for offline operation
        self.local_data_buffer = queue.Queue(maxsize=1000)  # Buffer for offline data
        self.local_decision_cache = {}
        self.offline_mode = False

        # Connection management
        self.connection_lock = threading.Lock()
        self.retry_timer = None
        self.retry_delay = 5  # seconds
        self.max_retries = 3

        # Callbacks
        self.primary_client.on_connect = self._on_primary_connect
        self.primary_client.on_disconnect = self._on_primary_disconnect
        self.primary_client.on_publish = self._on_publish
        self.primary_client.on_subscribe = self._on_subscribe

    def _on_primary_connect(self, client, userdata, flags, rc):
        """Handle primary broker connection"""
        if rc == 0:
            print(f"[{self.device_id}] Connected to primary broker {self.current_broker}:{self.current_port}")
            self.connected = True
            self.network_status = "primary"
            self.fallback_active = False
            self.offline_mode = False

            # Try to sync buffered data
            self._sync_buffered_data()
        else:
            print(f"[{self.device_id}] Failed to connect to primary broker, return code {rc}")
            self._switch_to_fallback()

    def _on_primary_disconnect(self, client, userdata, rc):
        """Handle primary broker disconnection"""
        print(f"[{self.device_id}] Disconnected from primary broker {self.current_broker}:{self.current_port}")
        self.connected = False
        self.network_status = "disconnected"

        # Attempt to reconnect or switch to fallback
        self._attempt_reconnection()

    def _on_publish(self, client, userdata, mid):
        """Handle successful publication"""
        pass  # Successfully published

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """Handle successful subscription"""
        pass  # Successfully subscribed

    def connect_with_fallback(self):
        """
        Attempt to connect with fallback options

        Returns:
            bool: True if connection successful, False otherwise
        """
        print(f"[{self.device_id}] Attempting to connect with fallback options...")

        # Try primary connection first
        if self._attempt_connection(self.primary_broker, self.primary_port):
            self.current_broker = self.primary_broker
            self.current_port = self.primary_port
            self.network_status = "primary"
            self.fallback_active = False
            return True

        # If primary fails, try fallback connections
        for fallback_broker, fallback_port in self.fallback_brokers:
            if self._attempt_connection(fallback_broker, fallback_port):
                self.current_broker = fallback_broker
                self.current_port = fallback_port
                self.network_status = f"fallback_{fallback_broker}"
                self.fallback_active = True
                print(f"[{self.device_id}] Using fallback connection to {fallback_broker}:{fallback_port}")
                return True

        # If all connections fail, activate offline mode
        print(f"[{self.device_id}] All connection attempts failed. Activating offline mode.")
        self.network_status = "offline"
        self.fallback_active = True
        self.offline_mode = True
        return False

    def _attempt_connection(self, broker, port):
        """
        Attempt to connect to a specific broker

        Args:
            broker: Broker address
            port: Broker port

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            print(f"[{self.device_id}] Attempting connection to {broker}:{port}...")
            self.primary_client.connect(broker, port, 60)
            self.primary_client.loop_start()

            # Wait briefly to see if connection succeeds
            time.sleep(1.5)  # Allow time for connection callback

            # Check if we're connected
            # Note: We can't directly check the connection status, so we'll use our own flag
            # In a real implementation, you'd need to implement a more robust connection check
            # For this example, we'll assume connection worked if we got this far
            return True
        except Exception as e:
            print(f"[{self.device_id}] Failed to connect to {broker}:{port} - {e}")
            return False

    def _switch_to_fallback(self):
        """Switch to fallback connection"""
        print(f"[{self.device_id}] Switching to fallback connection...")
        for fallback_broker, fallback_port in self.fallback_brokers:
            if self._attempt_connection(fallback_broker, fallback_port):
                self.current_broker = fallback_broker
                self.current_port = fallback_port
                self.network_status = f"fallback_{fallback_broker}"
                self.fallback_active = True
                print(f"[{self.device_id}] Successfully switched to fallback {fallback_broker}:{fallback_port}")
                return True

        # If all fallbacks fail, go to offline mode
        self.network_status = "offline"
        self.fallback_active = True
        self.offline_mode = True
        print(f"[{self.device_id}] All fallback connections failed. Operating in offline mode.")
        return False

    def _attempt_reconnection(self):
        """Attempt to reconnect to the network"""
        print(f"[{self.device_id}] Attempting to reconnect to network...")

        # Try primary first, then fallback
        if self._attempt_connection(self.primary_broker, self.primary_port):
            self.current_broker = self.primary_broker
            self.current_port = self.primary_port
            self.network_status = "primary"
            self.fallback_active = False
            self.offline_mode = False
            print(f"[{self.device_id}] Reconnected to primary broker")
            return True

        # Try fallback brokers
        for fallback_broker, fallback_port in self.fallback_brokers:
            if self._attempt_connection(fallback_broker, fallback_port):
                self.current_broker = fallback_broker
                self.current_port = fallback_port
                self.network_status = f"fallback_{fallback_broker}"
                self.fallback_active = True
                self.offline_mode = False
                print(f"[{self.device_id}] Reconnected to fallback {fallback_broker}:{fallback_port}")
                return True

        # If reconnection fails, stay in offline mode
        print(f"[{self.device_id}] Reconnection attempts failed, staying in offline mode")
        self.offline_mode = True
        return False

    def publish_with_buffering(self, topic, data):
        """
        Publish data with buffering for offline operation

        Args:
            topic: MQTT topic to publish to
            data: Data to publish

        Returns:
            bool: True if published (or buffered), False if failed
        """
        if self.offline_mode:
            # Buffer data for later transmission
            try:
                buffer_item = {
                    "topic": topic,
                    "data": data,
                    "timestamp": time.time(),
                    "attempts": 0
                }
                self.local_data_buffer.put(buffer_item, block=False)
                print(f"[{self.device_id}] Buffered message for offline transmission: {topic}")
                return True
            except queue.Full:
                print(f"[{self.device_id}] Buffer full, dropping message: {topic}")
                return False
        else:
            # Publish normally
            try:
                result = self.primary_client.publish(topic, json.dumps(data))
                if result.rc == 0:
                    print(f"[{self.device_id}] Published to {topic}")
                    return True
                else:
                    print(f"[{self.device_id}] Failed to publish to {topic}, buffering for retry")
                    # Buffer for retry if network issue
                    self._buffer_for_retry(topic, data)
                    return False
            except Exception as e:
                print(f"[{self.device_id}] Exception during publish: {e}, buffering for retry")
                self._buffer_for_retry(topic, data)
                return False

    def _buffer_for_retry(self, topic, data):
        """Buffer data for retry later"""
        try:
            buffer_item = {
                "topic": topic,
                "data": data,
                "timestamp": time.time(),
                "attempts": 0
            }
            self.local_data_buffer.put(buffer_item, block=False)
            print(f"[{self.device_id}] Buffered message for retry: {topic}")
        except queue.Full:
            print(f"[{self.device_id}] Retry buffer full, dropping message: {topic}")

    def _sync_buffered_data(self):
        """Sync buffered data when network becomes available"""
        if not self.offline_mode and not self.local_data_buffer.empty():
            print(f"[{self.device_id}] Syncing {self.local_data_buffer.qsize()} buffered messages...")

            synced_count = 0
            failed_count = 0

            # Create a temporary list to hold items while processing
            temp_items = []
            while not self.local_data_buffer.empty():
                try:
                    item = self.local_data_buffer.get_nowait()
                    temp_items.append(item)
                except queue.Empty:
                    break

            # Process each buffered item
            for item in temp_items:
                try:
                    result = self.primary_client.publish(item["topic"], json.dumps(item["data"]))
                    if result.rc == 0:
                        synced_count += 1
                        print(f"[{self.device_id}] Synced: {item['topic']}")
                    else:
                        # Put back for another retry
                        item["attempts"] += 1
                        if item["attempts"] < 5:  # Retry up to 5 times
                            self.local_data_buffer.put(item)
                        else:
                            print(f"[{self.device_id}] Failed to sync after 5 attempts: {item['topic']}")
                            failed_count += 1
                except Exception as e:
                    print(f"[{self.device_id}] Error syncing item: {e}")
                    # Put back for retry
                    item["attempts"] += 1
                    if item["attempts"] < 5:
                        self.local_data_buffer.put(item)
                    else:
                        failed_count += 1

            print(f"[{self.device_id}] Sync complete: {synced_count} synced, {failed_count} failed")
        else:
            print(f"[{self.device_id}] No buffered data to sync")

    def get_network_status(self):
        """
        Get current network status

        Returns:
            dict: Network status information
        """
        return {
            "device_id": self.device_id,
            "connected": self.connected,
            "network_status": self.network_status,
            "fallback_active": self.fallback_active,
            "offline_mode": self.offline_mode,
            "current_broker": self.current_broker,
            "current_port": self.current_port,
            "buffered_messages": self.local_data_buffer.qsize(),
            "primary_broker": self.primary_broker,
            "fallback_brokers": self.fallback_brokers
        }

    def enter_offline_mode(self):
        """Manually enter offline mode"""
        self.offline_mode = True
        self.connected = False
        self.network_status = "offline_manual"
        print(f"[{self.device_id}] Manually entered offline mode")

    def exit_offline_mode(self):
        """Try to exit offline mode by reconnecting"""
        self.offline_mode = False
        return self.connect_with_fallback()

    def get_local_data(self, data_type=None):
        """
        Get locally cached data for offline operation

        Args:
            data_type: Type of data to retrieve (None for all)

        Returns:
            dict: Local data cache
        """
        if data_type and data_type in self.local_decision_cache:
            return self.local_decision_cache[data_type]
        elif data_type is None:
            return self.local_decision_cache
        else:
            return {}

    def set_local_decision(self, decision_key, decision_value):
        """
        Set a local decision for offline operation

        Args:
            decision_key: Key for the decision
            decision_value: Value of the decision
        """
        self.local_decision_cache[decision_key] = {
            "value": decision_value,
            "timestamp": time.time(),
            "valid_until": time.time() + 3600  # Valid for 1 hour
        }

    def disconnect(self):
        """Cleanly disconnect from the broker"""
        if not self.offline_mode:
            self.primary_client.loop_stop()
            self.primary_client.disconnect()

        self.connected = False
        print(f"[{self.device_id}] Disconnected from network")

class SafeNetworkedSystem:
    """
    A safe networked Physical AI system with comprehensive fallback mechanisms
    """
    def __init__(self, device_id, primary_broker="localhost", primary_port=1883):
        self.fallback_system = NetworkWithFallback(device_id, primary_broker, primary_port)
        self.device_id = device_id

        # Safety parameters
        self.safety_thresholds = {
            "temperature": {"min": 10, "max": 80},
            "humidity": {"min": 0, "max": 100},
            "pressure": {"min": 900, "max": 1100}
        }

        # Local sensors for offline operation
        self.local_sensors = {
            "temperature": 22.0,
            "humidity": 45.0,
            "pressure": 1013.0
        }

        # Safety states
        self.emergency_shutdown_active = False
        self.safety_override = False

    def connect(self):
        """Connect with fallback"""
        return self.fallback_system.connect_with_fallback()

    def publish_sensor_data_with_safety(self, sensor_type, value):
        """
        Publish sensor data with safety checks

        Args:
            sensor_type: Type of sensor
            value: Sensor value

        Returns:
            bool: True if published successfully, False otherwise
        """
        # Update local sensor value
        self.local_sensors[sensor_type] = value

        # Check safety thresholds
        if sensor_type in self.safety_thresholds:
            thresholds = self.safety_thresholds[sensor_type]
            if value < thresholds["min"] or value > thresholds["max"]:
                print(f"[{self.device_id}] SAFETY ALERT: {sensor_type} value {value} outside safe range [{thresholds['min']}, {thresholds['max']}]")

                # Trigger safety action
                self._trigger_safety_action(sensor_type, value, thresholds)

                if self.safety_override:
                    # Override: don't publish dangerous values
                    print(f"[{self.device_id}] Safety override active: not publishing dangerous value {value}")
                    return False

        # Prepare data packet
        data = {
            "sensor_type": sensor_type,
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "device_id": self.device_id,
            "safety_status": "normal" if not self.safety_override else "safety_limited",
            "quality": "good"
        }

        # Publish with fallback
        return self.fallback_system.publish_with_buffering(
            f"physical_ai/sensor_data/{sensor_type}",
            data
        )

    def _trigger_safety_action(self, sensor_type, value, thresholds):
        """Trigger safety action based on sensor readings"""
        if not self.emergency_shutdown_active:
            print(f"[{self.device_id}] Initiating safety protocol for {sensor_type}")

            # In a real system, this would trigger actual safety mechanisms
            # For simulation, we'll just log the action
            safety_data = {
                "alert_type": "safety_threshold_exceeded",
                "sensor_type": sensor_type,
                "value": value,
                "thresholds": thresholds,
                "timestamp": datetime.now().isoformat(),
                "device_id": self.device_id
            }

            # Publish safety alert (even in emergency, try to notify)
            if not self.fallback_system.offline_mode:
                self.fallback_system.primary_client.publish(
                    f"physical_ai/safety_alert/{sensor_type}",
                    json.dumps(safety_data)
                )
            else:
                # Buffer for when network is available
                self.fallback_system.local_data_buffer.put({
                    "topic": f"physical_ai/safety_alert/{sensor_type}",
                    "data": safety_data,
                    "timestamp": time.time(),
                    "attempts": 0
                })

            # Activate safety override if needed
            if abs(value - ((thresholds["min"] + thresholds["max"]) / 2)) > (thresholds["max"] - thresholds["min"]) * 0.8:
                # Value is dangerously close to limit, activate override
                self.safety_override = True
                print(f"[{self.device_id}] Safety override activated due to critical value")

    def get_system_status(self):
        """Get comprehensive system status"""
        network_status = self.fallback_system.get_network_status()
        return {
            **network_status,
            "local_sensors": self.local_sensors.copy(),
            "safety_override": self.safety_override,
            "emergency_shutdown": self.emergency_shutdown_active,
            "safety_thresholds": self.safety_thresholds
        }

    def emergency_stop(self):
        """Activate emergency stop procedures"""
        print(f"[{self.device_id}] EMERGENCY STOP ACTIVATED")
        self.emergency_shutdown_active = True
        self.safety_override = True

        # Publish emergency stop notification
        emergency_data = {
            "event": "emergency_stop",
            "device_id": self.device_id,
            "timestamp": datetime.now().isoformat(),
            "reason": "manual_emergency_activation"
        }

        # Try to publish emergency notification
        if not self.fallback_system.offline_mode:
            self.fallback_system.primary_client.publish(
                "physical_ai/emergency/stop",
                json.dumps(emergency_data)
            )
        else:
            # Buffer for when network is available
            self.fallback_system.local_data_buffer.put({
                "topic": "physical_ai/emergency/stop",
                "data": emergency_data,
                "timestamp": time.time(),
                "attempts": 0
            })

def simulate_network_fallback_system():
    """
    Simulate a networked Physical AI system with fallback capabilities
    """
    print("Network Fallback and Redundancy Simulation")
    print("===========================================")
    print("This example demonstrates a Physical AI system with comprehensive")
    print("network fallback mechanisms and safety features.\n")

    # Create a safe networked system
    system = SafeNetworkedSystem("safe_ai_001", "localhost", 1883)

    print("System initialized with:")
    print("- Primary broker: localhost:1883")
    print("- Fallback brokers: backup-server:1883, cloud-mqtt:1884, local-mesh:1883")
    print("- Safety thresholds for temperature, humidity, and pressure")
    print("- Automatic buffering for offline operation\n")

    # Connect to network
    print("Attempting to connect to network...")
    connected = system.connect()

    if not connected:
        print("Could not connect to any broker. This is expected if no MQTT broker is running.")
        print("System will operate in offline mode with local decision making.\n")
    else:
        print("Successfully connected to network.\n")

    # Simulate normal operation
    print("Simulating normal operation with sensor readings...")
    for cycle in range(10):
        print(f"\n--- Cycle {cycle+1} ---")

        # Simulate sensor readings
        temp_reading = 22 + random.uniform(-2, 3)  # Normal temperature
        humidity_reading = 45 + random.uniform(-10, 10)  # Normal humidity
        pressure_reading = 1013 + random.uniform(-20, 20)  # Normal pressure

        # Publish sensor data with safety checks
        temp_ok = system.publish_sensor_data_with_safety("temperature", round(temp_reading, 2))
        humidity_ok = system.publish_sensor_data_with_safety("humidity", round(humidity_reading, 2))
        pressure_ok = system.publish_sensor_data_with_safety("pressure", round(pressure_reading, 2))

        print(f"  Temperature: {temp_reading:.2f}°C - Published: {temp_ok}")
        print(f"  Humidity: {humidity_reading:.2f}% - Published: {humidity_ok}")
        print(f"  Pressure: {pressure_reading:.2f} hPa - Published: {pressure_ok}")

        # Occasionally simulate a safety event
        if cycle == 4:
            print(f"\n--- SIMULATING SAFETY EVENT ---")
            print("Injecting high temperature reading to test safety system...")
            high_temp_ok = system.publish_sensor_data_with_safety("temperature", 85.0)  # Dangerous temperature
            print(f"  High temperature (85°C) - Published: {high_temp_ok}")
            print(f"  Safety override now active: {system.safety_override}")

        # Check system status
        status = system.get_system_status()
        print(f"\n  System Status: {status['network_status']}")
        print(f"  Buffered messages: {status['buffered_messages']}")
        print(f"  Safety override: {status['safety_override']}")
        print(f"  Connected: {status['connected']}")

        time.sleep(2)  # Wait between cycles

    # Simulate entering offline mode
    print(f"\n--- ENTERING OFFLINE MODE ---")
    system.fallback_system.enter_offline_mode()
    print("System now operating in offline mode with local decision making")

    # Continue operation in offline mode
    for cycle in range(3):
        print(f"\n--- Offline Cycle {cycle+1} ---")

        # These will be buffered since we're offline
        offline_temp = 20 + random.uniform(-1, 2)
        offline_humidity = 50 + random.uniform(-5, 5)

        temp_buffered = system.publish_sensor_data_with_safety("temperature", round(offline_temp, 2))
        humidity_buffered = system.publish_sensor_data_with_safety("humidity", round(offline_humidity, 2))

        print(f"  Offline temperature: {offline_temp:.2f}°C - Buffered: {temp_buffered}")
        print(f"  Offline humidity: {offline_humidity:.2f}% - Buffered: {humidity_buffered}")

        status = system.get_system_status()
        print(f"  Buffered messages now: {status['buffered_messages']}")

        time.sleep(1)

    # Try to reconnect and sync
    print(f"\n--- ATTEMPTING TO RECONNECT AND SYNC ---")
    reconnected = system.fallback_system.exit_offline_mode()
    if reconnected:
        print("Reconnected successfully! Syncing buffered data...")
        system.fallback_system._sync_buffered_data()
    else:
        print("Could not reconnect to network")

    # Final status
    final_status = system.get_system_status()
    print(f"\n=== FINAL SYSTEM STATUS ===")
    print(f"Network status: {final_status['network_status']}")
    print(f"Connected: {final_status['connected']}")
    print(f"Offline mode: {final_status['offline_mode']}")
    print(f"Buffered messages: {final_status['buffered_messages']}")
    print(f"Local sensors: {final_status['local_sensors']}")
    print(f"Safety override: {final_status['safety_override']}")
    print(f"Emergency shutdown: {final_status['emergency_shutdown']}")

    print(f"\nThis simulation demonstrates:")
    print("- Network fallback to backup brokers")
    print("- Data buffering during network outages")
    print("- Safety checks and overrides")
    print("- Automatic resynchronization when network is restored")
    print("- Safe operation in offline mode")

def main():
    simulate_network_fallback_system()

if __name__ == "__main__":
    main()