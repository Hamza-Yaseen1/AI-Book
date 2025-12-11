# Quickstart Guide: Voice Commands, LLM Planning, and Autonomous Humanoid Robot

## Prerequisites

Before starting with Module 4, ensure you have:

- Completed Modules 1-3 (ROS 2, Python agents, URDF modeling)
- Ubuntu 22.04 (Jammy) or compatible Linux distribution
- Python 3.8 or higher
- ROS 2 Humble Hawksbill installed
- OpenAI API key (or local LLM setup)
- Microphone for voice input
- At least 8GB RAM and 20GB free disk space

## Installation

### 1. Install Python Dependencies

```bash
# Create a virtual environment
python3 -m venv voice_llm_env
source voice_llm_env/bin/activate

# Install core dependencies
pip install openai-whisper
pip install openai
pip install pyaudio
pip install sounddevice
pip install numpy
pip install python-dotenv
pip install torch  # For Whisper (if using local models)
```

### 2. Set up OpenAI API Key

Create a `.env` file in your project directory:

```bash
# .env file
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Create Project Structure

```bash
mkdir -p ~/voice_llm_ws/src/voice_control/voice_control
mkdir -p ~/voice_llm_ws/src/llm_planner/llm_planner
mkdir -p ~/voice_llm_ws/src/capstone_project/capstone_project

cd ~/voice_llm_ws
colcon build
source install/setup.bash
```

## First Steps: Basic Voice Recognition

### 1. Create a simple voice processor

Create the file `~/voice_llm_ws/src/voice_control/voice_control/simple_voice_processor.py`:

```python
import pyaudio
import numpy as np
import whisper
import threading
import queue
import time

class SimpleVoiceProcessor:
    def __init__(self):
        # Load Whisper model (start with 'tiny' for testing)
        self.model = whisper.load_model("tiny")

        # Audio configuration
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.audio_queue = queue.Queue()

        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()

        # Start audio capture
        self.start_audio_capture()

    def start_audio_capture(self):
        """Start capturing audio in a separate thread"""
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        def audio_thread():
            while True:
                data = stream.read(self.chunk_size)
                audio_array = np.frombuffer(data, dtype=np.int16)
                self.audio_queue.put(audio_array)

        thread = threading.Thread(target=audio_thread, daemon=True)
        thread.start()

    def process_audio_batch(self, audio_batch):
        """Process a batch of audio data through Whisper"""
        # Convert to float32 and normalize
        audio_float = audio_batch.astype(np.float32) / 32768.0

        # Transcribe using Whisper
        result = self.model.transcribe(audio_float)
        return result["text"]

    def start_continuous_recognition(self):
        """Start continuous voice recognition"""
        buffer = []
        buffer_duration = 2.0  # seconds

        while True:
            if not self.audio_queue.empty():
                audio_chunk = self.audio_queue.get()
                buffer.extend(audio_chunk)

                # Process when buffer is sufficiently filled
                if len(buffer) >= int(self.sample_rate * 0.5):  # 500ms
                    audio_array = np.array(buffer)
                    text = self.process_audio_batch(audio_array)

                    if text.strip():
                        print(f"Recognized: {text}")

                    # Clear buffer after processing
                    buffer = []

            time.sleep(0.01)  # 10ms sleep

if __name__ == "__main__":
    processor = SimpleVoiceProcessor()
    print("Starting voice recognition... Speak now!")
    processor.start_continuous_recognition()
```

### 2. Test voice recognition

```bash
cd ~/voice_llm_ws
source install/setup.bash
python3 src/voice_control/voice_control/simple_voice_processor.py
```

## Second Steps: Basic LLM Integration

### 1. Create a simple LLM planner

Create the file `~/voice_llm_ws/src/llm_planner/llm_planner/simple_planner.py`:

```python
import openai
import os
from dotenv import load_dotenv
import json

load_dotenv()

class SimpleLLMPlanner:
    def __init__(self, model_name="gpt-3.5-turbo"):
        self.model_name = model_name
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        openai.api_key = self.api_key

    def generate_simple_plan(self, goal):
        """Generate a simple plan for a given goal"""
        prompt = f"""
        Generate a simple action plan for a humanoid robot to achieve this goal:
        Goal: {goal}

        Provide the response as a numbered list of actions.
        Each action should be specific and executable.
        """

        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error generating plan: {e}")
            return None

if __name__ == "__main__":
    planner = SimpleLLMPlanner()

    # Test with a simple goal
    goal = "navigate to the kitchen and pick up a cup"
    plan = planner.generate_simple_plan(goal)

    print(f"Goal: {goal}")
    print(f"Plan:\n{plan}")
```

### 2. Test LLM planning

```bash
cd ~/voice_llm_ws
source install/setup.bash
python3 src/llm_planner/llm_planner/simple_planner.py
```

## Third Steps: Integration with ROS 2

### 1. Create a ROS 2 node that combines voice and LLM

Create the file `~/voice_llm_ws/src/capstone_project/capstone_project/integrated_node.py`:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import threading
import queue
import pyaudio
import numpy as np
import whisper
import openai
import os
from dotenv import load_dotenv

load_dotenv()

class IntegratedAutonomousNode(Node):
    def __init__(self):
        super().__init__('integrated_autonomous_node')

        # Publishers
        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.status_publisher = self.create_publisher(String, '/system_status', 10)

        # Initialize Whisper model
        self.whisper_model = whisper.load_model("tiny")

        # Initialize OpenAI
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        else:
            self.get_logger().warning("OpenAI API key not found")

        # Audio configuration
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.audio_queue = queue.Queue()

        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()

        # Start audio capture in a separate thread
        self.start_audio_capture()

        # Command callbacks
        self.command_callbacks = {
            "forward": self.move_forward,
            "backward": self.move_backward,
            "stop": self.stop_robot,
            "dance": self.perform_dance,
        }

        # Start processing in a separate thread
        processing_thread = threading.Thread(target=self.process_audio_continuously)
        processing_thread.daemon = True
        processing_thread.start()

        self.get_logger().info("Integrated Autonomous Node initialized")

    def start_audio_capture(self):
        """Start capturing audio in a separate thread"""
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )

        def audio_thread():
            while True:
                data = stream.read(self.chunk_size)
                audio_array = np.frombuffer(data, dtype=np.int16)
                self.audio_queue.put(audio_array)

        thread = threading.Thread(target=audio_thread, daemon=True)
        thread.start()

    def process_audio_continuously(self):
        """Process audio continuously and handle voice commands"""
        buffer = []

        while True:
            if not self.audio_queue.empty():
                audio_chunk = self.audio_queue.get()
                buffer.extend(audio_chunk)

                # Process when buffer is sufficiently filled
                if len(buffer) >= int(self.sample_rate * 0.5):  # 500ms
                    audio_array = np.array(buffer)
                    text = self.process_audio_batch(audio_array)

                    if text.strip():
                        self.handle_recognized_command(text.strip())

                    # Clear buffer after processing
                    buffer = []

            # Small delay to prevent busy waiting
            time.sleep(0.01)

    def process_audio_batch(self, audio_batch):
        """Process a batch of audio data through Whisper"""
        try:
            # Convert to float32 and normalize
            audio_float = audio_batch.astype(np.float32) / 32768.0

            # Transcribe using Whisper
            result = self.whisper_model.transcribe(audio_float)
            return result["text"]
        except Exception as e:
            self.get_logger().error(f"Error processing audio: {e}")
            return ""

    def handle_recognized_command(self, text):
        """Process recognized text and trigger appropriate actions"""
        self.get_logger().info(f"Recognized: {text}")

        # Update status
        status_msg = String()
        status_msg.data = f"Recognized: {text}"
        self.status_publisher.publish(status_msg)

        # Simple keyword matching
        for keyword, callback in self.command_callbacks.items():
            if keyword in text.lower():
                callback(text)
                return

        # If not a direct command, try LLM planning
        if self.api_key:  # Only if API key is available
            self.handle_complex_command(text)

    def handle_complex_command(self, command_text):
        """Handle complex commands using LLM planning"""
        # For this example, we'll just log the complex command
        self.get_logger().info(f"Complex command received: {command_text}")
        # In a full implementation, this would call the LLM planner

    def move_forward(self, command_text):
        """Move robot forward"""
        msg = Twist()
        msg.linear.x = 0.3  # Adjust speed as needed
        self.cmd_vel_publisher.publish(msg)
        self.get_logger().info("Moving forward")

    def move_backward(self, command_text):
        """Move robot backward"""
        msg = Twist()
        msg.linear.x = -0.3
        self.cmd_vel_publisher.publish(msg)
        self.get_logger().info("Moving backward")

    def stop_robot(self, command_text):
        """Stop robot movement"""
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.cmd_vel_publisher.publish(msg)
        self.get_logger().info("Stopping robot")

    def perform_dance(self, command_text):
        """Perform a simple dance movement"""
        self.get_logger().info("Performing dance")
        # This would implement dance movements in a real robot

def main(args=None):
    rclpy.init(args=args)

    node = IntegratedAutonomousNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 2. Update setup.py for the package

Create or update `~/voice_llm_ws/src/capstone_project/setup.py`:

```python
from setuptools import setup
import os
from glob import glob

package_name = 'capstone_project'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Capstone project for voice and LLM integration',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'integrated_node = capstone_project.integrated_node:main',
        ],
    },
)
```

### 3. Create package.xml

Create `~/voice_llm_ws/src/capstone_project/package.xml`:

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>capstone_project</name>
  <version>0.0.0</version>
  <description>Capstone project for voice and LLM integration</description>
  <maintainer email="your.email@example.com">Your Name</maintainer>
  <license>Apache License 2.0</license>

  <depend>rclpy</depend>
  <depend>std_msgs</depend>
  <depend>geometry_msgs</depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

### 4. Build and run the integrated system

```bash
cd ~/voice_llm_ws
colcon build --packages-select capstone_project
source install/setup.bash

# Run the integrated node
ros2 run capstone_project integrated_node
```

## Next Steps

After completing the quickstart:

1. **Enhance voice recognition**: Add noise reduction and better command parsing
2. **Improve LLM integration**: Add context awareness and plan validation
3. **Add safety features**: Implement comprehensive safety monitoring
4. **Create capstone project**: Build a complete autonomous task
5. **Test with simulation**: Use Gazebo to test without physical robot

## Troubleshooting

- **No audio input**: Check microphone permissions and connections
- **API errors**: Verify OpenAI API key is correctly set in .env file
- **ROS 2 connection issues**: Ensure ROS_DOMAIN_ID is consistent across terminals
- **High CPU usage**: Consider using smaller Whisper models for initial testing
- **Permission errors**: Make sure all files have proper execute permissions

## Performance Tips

- Start with Whisper "tiny" model for testing, upgrade to larger models as needed
- Use temperature=0.3 for more consistent LLM outputs in planning
- Implement audio buffering to reduce processing overhead
- Add cooldown periods between voice commands to prevent overload