# Quickstart Guide: ROS 2 Learning Environment

## Prerequisites

Before starting with the ROS 2 educational content, ensure you have:

- Ubuntu 22.04 (Jammy) or compatible Linux distribution
- Python 3.8 or higher
- Basic understanding of Python programming
- Familiarity with command-line interface
- At least 4GB RAM and 20GB free disk space

## Installation

### 1. Install ROS 2 Humble Hawksbill

```bash
# Set locale
locale  # check for UTF-8

sudo locale-gen en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# Add ROS 2 apt repository
sudo apt update && sudo apt install -y curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install ROS 2 packages
sudo apt update
sudo apt install ros-humble-desktop
sudo apt install python3-rosdep2
sudo apt install python3-colcon-common-extensions
sudo apt install ros-humble-rclpy
```

### 2. Set up ROS 2 environment

```bash
source /opt/ros/humble/setup.bash
```

To make this permanent, add to your `~/.bashrc`:

```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
```

### 3. Create a workspace for learning

```bash
mkdir -p ~/ros2_learning_ws/src
cd ~/ros2_learning_ws
colcon build
source install/setup.bash
```

## First Steps: Hello World with ROS 2

### 1. Create your first ROS 2 package

```bash
cd ~/ros2_learning_ws/src
ros2 pkg create --build-type ament_python py_publisher_subscriber_01 --dependencies rclpy std_msgs
```

### 2. Create a simple publisher node

Create the file `~/ros2_learning_ws/src/py_publisher_subscriber_01/py_publisher_subscriber_01/publisher_member_function.py`:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()
    rclpy.spin(minimal_publisher)
    minimal_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 3. Create a simple subscriber node

Create the file `~/ros2_learning_ws/src/py_publisher_subscriber_01/py_publisher_subscriber_01/subscriber_member_function.py`:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalSubscriber(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    minimal_subscriber = MinimalSubscriber()
    rclpy.spin(minimal_subscriber)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 4. Update the setup.py file

Modify `~/ros2_learning_ws/src/py_publisher_subscriber_01/setup.py` to include the entry points:

```python
from setuptools import setup
import os
from glob import glob

package_name = 'py_publisher_subscriber_01'

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
    description='Simple publisher and subscriber example',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'talker = py_publisher_subscriber_01.publisher_member_function:main',
            'listener = py_publisher_subscriber_01.subscriber_member_function:main',
        ],
    },
)
```

### 5. Build and run your first example

```bash
cd ~/ros2_learning_ws
colcon build --packages-select py_publisher_subscriber_01
source install/setup.bash

# Terminal 1: Run the publisher
ros2 run py_publisher_subscriber_01 talker

# Terminal 2: Run the subscriber (in a new terminal)
source ~/ros2_learning_ws/install/setup.bash
ros2 run py_publisher_subscriber_01 listener
```

## Next Steps

After completing the quickstart:

1. Explore the [ROS 2 tutorials](https://docs.ros.org/en/humble/Tutorials.html)
2. Learn about services and actions
3. Practice with robot simulation environments
4. Work with URDF files for robot modeling
5. Build more complex Python agents for robot control

## Troubleshooting

- If you get import errors, ensure ROS 2 environment is sourced: `source /opt/ros/humble/setup.bash`
- If nodes can't communicate, check that ROS_DOMAIN_ID is the same in all terminals
- For permission issues with simulation, ensure Gazebo is properly installed