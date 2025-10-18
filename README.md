---

````markdown
# 🤖 BREAKERS ROBOT — Autonomous ROS 2 System

A fully modular ROS 2 Humble-based robotic system designed for **mapping, navigation, and AI-assisted perception**.  
Runs across a **Raspberry Pi (robot control)** and a **development PC (AI, mapping & navigation)** — communicating over ROS 2 DDS.

---

## 🧠 System Overview

| Component | Platform | Description |
|------------|-----------|-------------|
| **Raspberry Pi 4 / 5 (Robot)** | Ubuntu 22.04 Server + ROS 2 Humble | Handles low-level hardware control, sensors, and camera |
| **PC / Laptop (Base Station)** | Ubuntu 22.04 Desktop + ROS 2 Humble | Handles SLAM, Navigation, AI perception, and Behavior Trees |

---

## 🔩 Hardware Architecture

- **Main MCU:** Arduino Uno (via `diffdrive_arduino`)
- **Microprocessor:** Raspberry Pi 4 / 5  
- **Sensors:** SLLIDAR A1, MPU6050 IMU, Wheel encoders  
- **Actuators:** Two DC motors, Servo (pan/tilt)  
- **Camera:** Raspberry Pi Camera Module V1 (lower FPS, visualization disabled in RViz)

---

## 📚 Inspirations & References

This project was heavily inspired by and builds upon:
- [**articubot_one** by Josh Newans](https://github.com/joshnewans/articubot_one)
- [**diffdrive_arduino (Humble branch)**](https://github.com/joshnewans/diffdrive_arduino/tree/humble)
- [**ROOK_ros_ws**](https://github.com/Collins-Omariba/ROOK_ros_ws) (used as an early template before full migration)
- **Final working diffdrive_arduino version:**  
  👉 [Breakers DiffDrive (Pi branch)](https://github.com/Nathan-bot-design/breakers_ws/tree/pi/src/diffdrive_arduino)
- **ROS-Arduino Bridge (with IMU)**  
  👉 [Bridge with IMU integration](https://github.com/Nathan-bot-design/breakers_ws/tree/ros_bridge_with_imu)

🟢 *Note:* Some IMU axes return slightly negative values — performance is stable and under refinement.

---

## 🧩 Node Launch Summary

### 🟠 ON RASPBERRY PI — *Robot Side*
Handles **hardware**, **movement**, **sensors**, and **camera streaming**.

| # | Node | Command | Purpose |
|---|------|----------|----------|
| 1️⃣ | **Robot core** | `ros2 launch dojo launch_robot.launch.py` | Motor control + odometry publishing |
| 2️⃣ | **LiDAR** | `ros2 run sllidar_ros2 sllidar_node` | Publishes `/scan` topic |
| 3️⃣ | **EKF Fusion** | `ros2 launch dojo ekf_launch.py` | Fuses IMU + encoder data → `/odom` |
| 4️⃣ | **Camera Stack** | `ros2 launch dojo robot_stack_launch.py` | Publishes camera stream |
| 5️⃣ | **Servo Control** | `ros2 run dojo_servo servo_node` | Controls pan/tilt |

---

### 💻 ON PC — *Base Station / AI & Autonomy*
Handles **mapping**, **localization**, **navigation**, and **AI perception**.

| # | Node | Command | Description |
|---|------|----------|-------------|
| 1️⃣ | **Mapping (SLAM Toolbox)** | `ros2 launch slam_toolbox online_async_launch.py slam_params_file:=./src/dojo/config/mapper_params_online_async.yaml use_sim_time:=false` | Builds live map |
| 2️⃣ | **Teleop Keyboard** | `ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/cmd_vel_key` | Manual control |
| 3️⃣ | **RViz Visualization** | `rviz2 -d ./src/dojo/rviz/default.rviz` | 3D visualization |
| 4️⃣ | **Map Saver** | `ros2 run nav2_map_server map_saver_cli -f ~/my_map123` | Save generated map |
| 5️⃣ | **Localization** | `ros2 launch dojo localization_launch.py map:=/home/nathan/my_map123.yaml` | AMCL-based localization |
| 6️⃣ | **Navigation Stack** | `ros2 launch dojo navigation_launch.py use_sim_time:=false` | Autonomous navigation |
| 7️⃣ | **Color Detection** | `ros2 launch image_processor colour_detector.launch.py` | Detects color markers or object regions |
| 8️⃣ | **Disease Detector (ML)** | `ros2 launch image_processor disease_detector.launch.py` | Classifies crops/leaves using trained model |
| 9️⃣ | **Behavior Tree (PyTree)** | `python3 app.py` | Controls mission flow |

---

## 🧠 Sensor Fusion & EKF Configuration

The **IMU (MPU6050)** was integrated via the Arduino bridge, and the **robot_localization** package fuses its data with wheel encoder odometry.  
Fine-tuning the covariance matrices solved drift and skid issues.

Sample EKF config snippet:  
📄 [`ekf.yaml`](https://github.com/Nathan-bot-design/breakers_ws/blob/pi/src/dojo/config/ekf.yaml)

```yaml
odom0_config: [false, false, false,
               false, false, false,
               true, true, false,
               false, false, true,
               false, false, false]

imu0: /imu_broad/imu
imu0_config: [false, false, false,
              false, false, true,
              false, false, false,
              false, false, true,
              false, false, false]
````

🟢 After adjusting the matrices and calibration, the translation skids were eliminated.

---

## ⚙️ ROS 2 Control & Arduino Interface

The robot uses a modified **DiffDriveArduino** plugin to communicate with `/dev/arduino` (auto-detected by ID).
Encoders initially on **A4/A5** were shifted to **A0/A1** to free I2C pins for the MPU6050.

Excerpt from [`ros2_control.xacro`](https://github.com/Nathan-bot-design/breakers_ws/blob/pi/src/dojo/description/ros2_control.xacro):

```xml
<plugin>diffdrive_arduino/DiffDriveArduino</plugin>
<param name="left_wheel_name">left_wheel_joint</param>
<param name="right_wheel_name">right_wheel_joint</param>
<param name="loop_rate">30</param>
<param name="device">/dev/arduino</param>
<param name="baud_rate">57600</param>
<param name="timeout">1000</param>
<param name="enc_counts_per_rev">1135</param>
```

---

## 🧲 Automatic USB Port Detection

Both LiDAR and Arduino are dynamically assigned device IDs to eliminate port dependency.

Excerpt from [`sllidar_a1_launch.py`](https://github.com/Nathan-bot-design/breakers_ws/blob/pi/src/sllidar_ros2/launch/sllidar_a1_launch.py):

```python
serial_port = LaunchConfiguration('serial_port', default='/dev/lidar')
```

This allows plug-and-play without manually editing port numbers.

---

## 🧮 Robot Parameters

Borrowed and tuned similarly to **KNIGHTS** robot parameters for consistent odometry scaling:

* **Robot Radius:** ~0.105 m
* **Encoder Ticks/Rev:** 1135 (measured)
* **Wheel Diameter:** 0.065 m
* **Max Speed:** ~0.4 m/s

---

## 🧱 Repository Structure

```bash
breakers_ws/
├── src/
│   ├── dojo/                     # Core robot control (motors, EKF, navigation)
│   ├── image_processor/          # Color & ML-based image processing
│   ├── dojo_servo/               # Servo & actuator control nodes
│   ├── gazebo_ignition_fortress/ # Behavior Tree & autonomy testing
│   ├── diffdrive_arduino/        # Custom motor + encoder driver
│   └── sllidar_ros2/             # LiDAR integration
├── config/                       # YAMLs for EKF, Nav2, SLAM
├── launch/                       # Launch files
├── rviz/                         # Visualization configs
└── README.md
```

---

## 🧩 Setup Instructions

### 🖥️ 1. Dev PC (Ubuntu 22.04 + ROS 2 Humble)

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

### 🤖 2. Raspberry Pi (Ubuntu 22.04 Server + ROS 2 Humble)

```bash
ros2 launch dojo launch_robot.launch.py
ros2 run sllidar_ros2 sllidar_node
ros2 launch dojo ekf_launch.py
ros2 launch dojo robot_stack_launch.py
ros2 run dojo_servo servo_node
```

---

## 🌍 Network Configuration (ROS 2 DDS)

```bash
export ROS_DOMAIN_ID=7
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
```

Add the above lines to both devices’ `~/.bashrc`.

---

## 🧠 AI Models

Stored under:

```
src/image_processor/image_processor/models/
```

Used by:

* `colour_detector.launch.py`
* `disease_detector.launch.py`

---

## 🗺️ Mapping → Localization → Navigation Flow

```bash
ros2 launch slam_toolbox online_async_launch.py \
slam_params_file:=./src/dojo/config/mapper_params_online_async.yaml use_sim_time:=false
ros2 run nav2_map_server map_saver_cli -f ~/my_map123
ros2 launch dojo localization_launch.py map:=/home/nathan/my_map123.yaml
ros2 launch dojo navigation_launch.py use_sim_time:=false
```

---

## 🧭 Mission Control (Autonomy)

```bash
cd src/gazebo_ignition_fortress/test_folder
python3 app.py
```

---

## 🧰 Key Dependencies

* `ros-humble-slam-toolbox`
* `ros-humble-nav2-bringup`
* `ros-humble-rviz2`
* `ros-humble-robot-localization`
* `ros-humble-ros2-control`
* `sllidar_ros2`
* `OpenCV`, `PyTorch`

---

## 🧑‍💻 Credits

* **Developers:** Limit Breakers Team
* **Mentors & References:** [Josh Newans](https://github.com/joshnewans), [Collins Omariba](https://github.com/Collins-Omariba)
* **Documentation style inspired by:** [2025-KNIGHTS-Robot](https://github.com/roboticsdojo/2025-KNIGHTS-Robot)
* **Contributors:** Robotics Dojo, Shohei Aoki Labs

---

## 🦾 CAD & Robot Previews

**CAD Preview**
![CAD](https://github.com/user-attachments/assets/3dc8365f-aca1-4d4e-9a0a-158cf7830ffe)

**Physical Robot** <img width="322" height="235" alt="image" src="https://github.com/user-attachments/assets/5bba7aea-4be7-44ac-9c19-dc1476c55bec" />

---

## 📜 License

MIT License © 2025 Limit Breakers Robotics

```

---

