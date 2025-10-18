
# 🤖 BREAKERS ROBOT — Autonomous ROS 2 System

A fully modular ROS 2 Humble-based robotic system designed for mapping, navigation, and AI-assisted perception.  
Runs across a **Raspberry Pi (robot control)** and a **development PC (AI, mapping & navigation)** — communicating over ROS 2 DDS.

---

## 🧠 System Overview

| Component | Platform | Description |
|------------|-----------|-------------|
| **Raspberry Pi 4 / 5 (Robot)** | Ubuntu 22.04 Server + ROS 2 Humble | Handles low-level hardware control, sensors, and camera |
| **PC / Laptop (Base Station)** | Ubuntu 22.04 Desktop + ROS 2 Humble | Handles SLAM, Navigation, AI perception, and Behavior Trees |

---

## 🧩 Node Launch Summary

### 🟠 ON RASPBERRY PI — *Robot Side*
Handles **hardware**, **movement**, **sensors**, and **camera streaming**.

| # | Node | Command | Purpose |
|---|------|----------|----------|
| 1️⃣ | **Robot core** | `ros2 launch dojo launch_robot.launch.py` | Motor control + odometry publishing |
| 2️⃣ | **LiDAR** | `ros2 run sllidar_ros2 sllidar_node` | Publishes `/scan` topic |
| 3️⃣ | **EKF** | `ros2 launch dojo ekf_launch.py` | Fuses IMU + encoder data → `/odom` |
| 4️⃣ | **Camera stack** | `ros2 launch dojo robot_stack_launch.py` | Publishes camera stream to `/image_raw` |
| 5️⃣ | **Servo control** | `ros2 run dojo_servo servo_node` | Controls pan/tilt or other actuators |

---

### 💻 ON PC — *Base Station / AI & Autonomy*
Handles **mapping**, **localization**, **navigation**, and **AI perception**.

| # | Node | Command | Description |
|---|------|----------|-------------|
| 1️⃣ | **Mapping (SLAM Toolbox)** | `ros2 launch slam_toolbox online_async_launch.py slam_params_file:=./src/dojo/config/mapper_params_online_async.yaml use_sim_time:=false` | Builds live map |
| 2️⃣ | **Teleop Keyboard** | `ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/cmd_vel_key` | Manual control |
| 3️⃣ | **RViz Visualization** | `rviz2 -d ./src/dojo/rviz/default.rviz` | 3D visualization |
| 4️⃣ | **Map Saver** | `ros2 run nav2_map_server map_saver_cli -f ~/my_map123` | Saves `.pgm` + `.yaml` map |
| 5️⃣ | **Localization** | `ros2 launch dojo localization_launch.py map:=/home/nathan/my_map123.yaml` | Loads map for AMCL localization |
| 6️⃣ | **Navigation Stack** | `ros2 launch dojo navigation_launch.py use_sim_time:=false` | Autonomous navigation (Nav2) |
| 7️⃣ | **Color Detection** | `ros2 launch image_processor colour_detector.launch.py` | Detects color markers/objects |
| 8️⃣ | **Disease Detector (ML)** | `ros2 launch image_processor disease_detector.launch.py` | Uses trained model to classify plant health |
| 9️⃣ | **Behavior Tree** | `python3 app.py` | Controls mission flow — integrates Nav2 & detectors |

---

## 🧱 Repository Structure

```bash
breakers_ws/
├── src/
│   ├── dojo/                     # Core robot control (motors, EKF, navigation)
│   ├── image_processor/          # Color & ML-based image processing
│   ├── gazebo_ignition_fortress/ # Testing folder for behavior trees & simulations
│   ├── dojo_servo/               # Servo and actuator control nodes
│   └── ...
├── launch/                       # Launch files for each system module
├── config/                       # YAML configs (EKF, Nav2, SLAM, etc.)
├── rviz/                         # Visualization layouts
└── README.md                     # (this file)
````

---

## 🧩 Setup Instructions

### 🖥️ 1. Dev PC Setup (Ubuntu 22.04 + ROS 2 Humble)

```bash
sudo apt update && sudo apt install -y python3-colcon-common-extensions git
mkdir -p ~/breakers_ws/src
cd ~/breakers_ws/src
git clone https://github.com/Nathan-bot-design/breakers_ws
cd ~/breakers_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
```

### 🤖 2. Raspberry Pi Setup (Ubuntu 22.04 Server + ROS 2 Humble)

Same steps as above, then launch robot nodes:

```bash
ros2 launch dojo launch_robot.launch.py
ros2 run sllidar_ros2 sllidar_node
ros2 launch dojo ekf_launch.py
ros2 launch dojo robot_stack_launch.py
ros2 run dojo_servo servo_node
```

---

## 🌍 Network Configuration (ROS 2 DDS)

Both devices must be on the same Wi-Fi / LAN.
Set the PC as the main discovery server (optional) or simply export the ROS domain:

```bash
# On both devices
export ROS_DOMAIN_ID=7
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
```

You can add those lines to `~/.bashrc` for persistence.

---

## 🧠 AI Models

The trained image models are stored here:

```
src/image_processor/image_processor/models/
```

Used by:

* `colour_detector.launch.py`
* `disease_detector.launch.py`

Ensure model `.pth` files are available before running detection nodes.

---

## 🗺️ Mapping → Localization → Navigation Flow

1️⃣ **Mapping phase**

```bash
ros2 launch slam_toolbox online_async_launch.py \
slam_params_file:=./src/dojo/config/mapper_params_online_async.yaml use_sim_time:=false
```

2️⃣ **Save map**

```bash
ros2 run nav2_map_server map_saver_cli -f ~/my_map123
```

3️⃣ **Localization**

```bash
ros2 launch dojo localization_launch.py map:=/home/nathan/my_map123.yaml
```

4️⃣ **Navigation**

```bash
ros2 launch dojo navigation_launch.py use_sim_time:=false
```

---

## 🧭 Mission Control (Autonomy)

Run PyTree-based mission logic:

```bash
cd src/gazebo_ignition_fortress/test_folder
python3 app.py
```

---

## 🧰 Dependencies & Key Packages

* **ros-humble-slam-toolbox**
* **ros-humble-nav2-bringup**
* **ros-humble-rviz2**
* **ros-humble-robot-localization**
* **ros-humble-ros2-control**
* **sllidar_ros2**
* **OpenCV + PyTorch (for ML detection)**

---

## 🧑‍💻 Credits

* **Developer:** Nathan Kingori
* **Based on:** [ROOK_ros_ws](https://github.com/Collins-Omariba/ROOK_ros_ws)
* **Documentation style inspired by:** [2025-KNIGHTS-Robot](https://github.com/roboticsdojo/2025-KNIGHTS-Robot)
* **Contributors:** Robotics Dojo & Shohei Aoki Labs

---

## 📸 Preview

(Insert image or GIF of robot + RViz screenshot)

---
 

That would make your repo look *super polished and professional*, just like top-tier robotics research repos.
```
