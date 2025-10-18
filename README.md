

#  BREAKERS Robot — Robotics Dojo Challenge 2025

The **BREAKERS Robot** was developed for the **Robotics Dojo 2025 Robotics Challenge** under the mentorship of **Robotics Dojo** and **Dr. Shohei Aoki**.

The challenge focused on creating robots that assist in **agriculture**, addressing tasks such as:

* Navigation in unstructured environments
* Crop monitoring
* Autonomous field operations

Our solution — **BREAKERS** — is a **fully modular ROS 2 Humble–based robotic system** built for **mapping, navigation, and AI-assisted perception**.
It operates as a distributed system across:

*  **Raspberry Pi (robot control + sensors)**
*  **Development PC (AI, mapping, navigation)**

Communication between them uses **ROS 2 DDS**.

---

##  Repository Branch Overview

| Branch                  | Purpose                                                                         | Link                                                                                                       |
| :---------------------- | :------------------------------------------------------------------------------ | :--------------------------------------------------------------------------------------------------------- |
| **pi (Default)**        | Robot-side code for Raspberry Pi 4/5 running Ubuntu 22.04 Server + ROS 2 Humble | [🔗 pi branch](https://github.com/Nathan-bot-design/breakers_ws)                                           |
| **breakerpc**           | Development machine branch for AI, mapping, and navigation                      | [🔗 breakerpc branch](https://github.com/Nathan-bot-design/breakers_ws/tree/breakerpc)                     |
| **ros_bridge_with_imu** | Arduino firmware + ROS bridge (for Arduino UNO)                                 | [🔗 ros_bridge_with_imu branch](https://github.com/Nathan-bot-design/breakers_ws/tree/ros_bridge_with_imu) |

---

##  System Overview

| Component                      | Platform                            | Description                                                 |
| :----------------------------- | :---------------------------------- | :---------------------------------------------------------- |
| **Raspberry Pi 4/5 (Robot)**   | Ubuntu 22.04 Server + ROS 2 Humble  | Handles low-level hardware control, sensors, and camera     |
| **PC / Laptop (Base Station)** | Ubuntu 22.04 Desktop + ROS 2 Humble | Handles SLAM, navigation, AI perception, and behavior trees |

---

##  Hardware Architecture

* **Main MCU:** Arduino UNO (via `diffdrive_arduino`)
* **Microprocessor:** Raspberry Pi 4 / 5
* **Sensors:** SLLIDAR A1 • MPU6050 IMU • Wheel Encoders
* **Actuators:** Dual DC motors with encoders • Servo (pan/tilt)
* **Camera:** Raspberry Pi Camera Module V1 (Low FPS; RViz disabled)

---

##  Inspirations & References

This project builds upon the work of:

* [**articubot_one** by Josh Newans](https://github.com/joshnewans/articubot_one)
* [**diffdrive_arduino (Humble branch)**](https://github.com/joshnewans/diffdrive_arduino/tree/humble)
* [**ROOK_ros_ws** by Collins Omariba](https://github.com/Collins-Omariba/ROOK_ros_ws)

 **Final working DiffDrive:** [Pi branch → diffdrive_arduino](https://github.com/Nathan-bot-design/breakers_ws/tree/pi/src/diffdrive_arduino)
 **ROS–Arduino Bridge with IMU:** [ros_bridge_with_imu branch](https://github.com/Nathan-bot-design/breakers_ws/tree/ros_bridge_with_imu)

>  *Note:* Some IMU axes return negative readings — stable but under refinement.

---

##  Node Launch Summary

###  On Raspberry Pi — *Robot Side*

Handles **hardware**, **movement**, **sensors**, and **camera streaming**.

|  #  | Node              | Command                                   | Purpose                        |
| :-: | :---------------- | :---------------------------------------- | :----------------------------- |
| 1️⃣ | **Robot Core**    | `ros2 launch dojo launch_robot.launch.py` | Motor control + odometry       |
| 2️⃣ | **LiDAR**         | `ros2 run sllidar_ros2 sllidar_node`      | Publishes `/scan`              |
| 3️⃣ | **EKF Fusion**    | `ros2 launch dojo ekf_launch.py`          | Fuses IMU + encoders → `/odom` |
| 4️⃣ | **Camera Stack**  | `ros2 launch dojo robot_stack_launch.py`  | Publishes camera stream        |
| 5️⃣ | **Servo Control** | `ros2 run dojo_servo servo_node`          | Controls pan/tilt              |

---

###  On PC — *Base Station / AI & Autonomy*

Handles **mapping**, **localization**, **navigation**, and **AI perception**.

|  #  | Node                       | Command                                                                                                                                   | Description             |
| :-: | :------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------- | :---------------------- |
| 1️⃣ | **Mapping (SLAM Toolbox)** | `ros2 launch slam_toolbox online_async_launch.py slam_params_file:=./src/dojo/config/mapper_params_online_async.yaml use_sim_time:=false` | Builds live map         |
| 2️⃣ | **Teleop Keyboard**        | `ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/cmd_vel_key`                                               | Manual control          |
| 3️⃣ | **RViz Visualization**     | `rviz2 -d ./src/dojo/rviz/default.rviz`                                                                                                   | 3D visualization        |
| 4️⃣ | **Map Saver**              | `ros2 run nav2_map_server map_saver_cli -f ~/my_map123`                                                                                   | Saves `.pgm + .yaml`    |
| 5️⃣ | **Localization**           | `ros2 launch dojo localization_launch.py map:=/home/nathan/my_map123.yaml`                                                                | AMCL localization       |
| 6️⃣ | **Navigation Stack**       | `ros2 launch dojo navigation_launch.py use_sim_time:=false`                                                                               | Nav2 autonomy           |
| 7️⃣ | **Color Detection**        | `ros2 launch image_processor colour_detector.launch.py`                                                                                   | Detects color markers   |
| 8️⃣ | **Disease Detector (ML)**  | `ros2 launch image_processor disease_detector.launch.py`                                                                                  | Classifies plant health |
| 9️⃣ | **Behavior Tree (PyTree)** | `python3 app.py`                                                                                                                          | Controls mission flow   |

---

##  Sensor Fusion & EKF Configuration

IMU (MPU6050) integrated via Arduino bridge + `robot_localization` EKF for drift-free odometry.
Key matrices tuned to eliminate wheel skid.

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
```

---

##  ROS 2 Control & Arduino Interface

Modified **DiffDriveArduino** plugin for auto-detected `/dev/arduino` port.
Encoders moved from A4/A5 → A0/A1 to free I²C pins for MPU6050.

📄 [`ros2_control.xacro`](https://github.com/Nathan-bot-design/breakers_ws/blob/pi/src/dojo/description/ros2_control.xacro)

```xml
<plugin>diffdrive_arduino/DiffDriveArduino</plugin>
<param name="device">/dev/arduino</param>
<param name="baud_rate">57600</param>
<param name="enc_counts_per_rev">1135</param>
```

---

##  Automatic USB Port Detection

LiDAR and Arduino devices auto-identified to avoid manual port edits.
📄 [`sllidar_a1_launch.py`](https://github.com/Nathan-bot-design/breakers_ws/blob/pi/src/sllidar_ros2/launch/sllidar_a1_launch.py):

```python
serial_port = LaunchConfiguration('serial_port', default='/dev/lidar')
```

---

##  Robot Parameters

| Parameter             | Value    | Notes             |
| :-------------------- | :------- | :---------------- |
| **Robot radius**      | 0.15 m   | Tuned for Nav2    |
| **Wheel diameter**    | 0.0425 m | Measured          |
| **Encoder ticks/rev** | 1135     | Accurate odometry |

---

## 📁 Repository Structure

```bash
breakers_ws/
├── src/
│   ├── dojo/                     # Core control & navigation
│   ├── image_processor/          # Color & ML perception
│   ├── dojo_servo/               # Servo control nodes
│   ├── gazebo_ignition_fortress/ # Behavior tree tests
│   ├── diffdrive_arduino/        # Motor + encoder driver
│   └── sllidar_ros2/             # LiDAR driver
├── config/                       # EKF, Nav2, SLAM YAMLs
├── launch/                       # Launch files
├── rviz/                         # RViz setups
└── README.md
```

---

##  Setup Instructions

###  Development PC (Ubuntu 22.04 + ROS 2 Humble)

```bash
sudo apt update && sudo apt install -y python3-colcon-common-extensions git
mkdir -p ~/breakers_ws/src && cd ~/breakers_ws/src
git clone -b breakerpc https://github.com/Nathan-bot-design/breakers_ws
cd ~/breakers_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
```

###  Raspberry Pi (Ubuntu 22.04 Server + ROS 2 Humble)

```bash
git clone https://github.com/Nathan-bot-design/breakers_ws
cd breakers_ws && colcon build && source install/setup.bash
ros2 launch dojo launch_robot.launch.py
ros2 run sllidar_ros2 sllidar_node
ros2 launch dojo ekf_launch.py
ros2 launch dojo robot_stack_launch.py
ros2 run dojo_servo servo_node
```

---

##  Network Configuration (ROS 2 DDS)

Add to `~/.bashrc` on both devices:

```bash
export ROS_DOMAIN_ID=7
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
```

---

##  AI Models

Stored in:
`src/image_processor/image_processor/models/`
Used by:

* `colour_detector.launch.py`
* `disease_detector.launch.py`

---

##  Mapping → Localization → Navigation

```bash
ros2 launch slam_toolbox online_async_launch.py \
  slam_params_file:=./src/dojo/config/mapper_params_online_async.yaml use_sim_time:=false
ros2 run nav2_map_server map_saver_cli -f ~/my_map123
ros2 launch dojo localization_launch.py map:=/home/nathan/my_map123.yaml
ros2 launch dojo navigation_launch.py use_sim_time:=false
```

---

##  Navigation Stack Tuning

The navigation stack in the **BREAKERS Robot** was **heavily optimized beyond default Nav2 parameters** to achieve **smooth, reliable, and real-time motion** on a **Raspberry Pi + PC** setup.

This section summarizes the key improvements and tuning decisions made during development.

---

### 1️⃣ Localization (AMCL)

**Goal:** Improve pose accuracy and reduce drift.  

**Changes:**

| Parameter | New | Old |
|:--|:--:|:--:|
| α1–α5 | 0.05 | 0.2 |
| update_rate | 5.0 | 1.0 |

**Effect:**  
AMCL now **trusts wheel odometry more**, producing a tighter and more stable particle cloud with minimal jitter — essential for **precise mapping and navigation**.

---

### 2️⃣ Controller Server (Path Following)

**Goal:** Achieve smoother, more natural motion and stronger obstacle avoidance.  

**Changes:**

| Parameter | New | Old |
|:--|:--:|:--:|
| xy_goal_tolerance | 0.20 | 0.25 |
| yaw_goal_tolerance | 0.20 | 0.25 |
| PathAlign.scale | 15.0 | 32.0 |
| BaseObstacle.scale | 0.5 | 0.02 |

**Effect:**  
Reduced oscillations and zig-zagging. The robot now executes **fluid turns** and maintains **stable paths** across gravel, ramps, and uneven terrain.

---

### 3️⃣ Local Costmap

**Goal:** Optimize for real-time performance on limited hardware.  

**Changes:**

| Parameter | New | Old |
|:--|:--:|:--:|
| resolution | 0.05 m | 0.02 m |
| robot_radius | 0.18 m | 0.15 m |
| inflation_radius | 0.08 m | 0.10 m |
| cost_scaling_factor | 2.0 | 20.0 |

**Effect:**  
CPU load reduced significantly while maintaining **safe obstacle margins** and **smooth local pathing**.

---

### 4️⃣ Global Costmap

**Goal:** Accelerate global planning and reduce computational overhead.  

**Changes:**

| Parameter | New | Old |
|:--|:--:|:--:|
| resolution | 0.05 m | 0.02 m |
| cost_scaling_factor | 2.5 | 20.0 |
| robot_radius | 0.18 m | 0.15 m |

**Effect:**  
Global planner now computes paths **faster and more efficiently**, ideal for **open or semi-structured fields**.

---

### 5️⃣ Planner & Smoother Servers

**Goal:** Combine **stable global paths** with **smooth local execution**.  

**Changes:**

| Parameter | New | Old |
|:--|:--:|:--:|
| planner | Dijkstra | A* |
| goal_tolerance | 0.75 | 0.5 |
| smoother.refinement_enabled | true | — |
| smoother.max_iterations | 1000 | — |

**Effect:**  
The **Dijkstra planner** performs better in partially mapped areas, while the **smoother** ensures **continuous, curve-optimized motion** without pausing between waypoints.

---

###  Summary of Improvements

| Subsystem | Change | Result |
|:--|:--|:--|
| **Localization** | Higher odometry trust | Low drift, stable positioning |
| **Controller** | Balanced DWB critics | Smooth obstacle-aware motion |
| **Local Map** | Coarser resolution | Lower CPU load, faster updates |
| **Global Map** | Soft inflation zones | Faster global planning |
| **Planner** | Dijkstra + smoother | Robust real-world navigation |

---

###  Overall Result

These tuned parameters enabled the **BREAKERS Robot** to achieve:
- **Collision-free**, **power-efficient** navigation  
- **Human-like motion profiles**  
- Reliable performance across **grass**, **gravel**, **ramps**, and **sawdust**  

##  Autonomy — Behavior Tree–Driven Mission Control

> “With guidance from Dr. Shohei Aoki, we learned that true autonomy isn’t just about navigation — it’s about *decision-making*.”

The **BREAKERS Robot** achieves full autonomy through a **Behavior Tree (BT)** framework [app.py](https://github.com/Nathan-bot-design/breakers_ws/blob/breakerpc/src/gazebo_ignition_fortress/test_folder/app.py)
, integrating all subsystems — navigation, camera, LiDAR, servo control, and AI detection — into a single decision engine.

###  Mission Flow Overview

| Stage | Task              | ROS Integration                                 | Status        |
| :---: | :---------------- | :---------------------------------------------- | :------------ |
|  1️⃣  | Weeding           | Navigate + Disease Detection                    | ✅ Success     |
|  2️⃣  | Terrain Traversal | Ramp → Grass → Gravel → Sawdust                 | ⏳ In Progress |
|  3️⃣  | Loading Area      | Color Detection                                 | ✅/⚠️          |
|  4️⃣  | Delivery Route    | Follows route based on color (“white” / “blue”) | ✅ Final Stage |

![WhatsApp Image 2025-10-11 at 07 41 28_433962e3](https://github.com/user-attachments/assets/f3d19e6e-7cd2-4e41-a2e2-f048bd633927)

**Core Autonomy Features:**

* Dynamic Task Sequencing
* ROS 2 Action Integration (Nav2 `navigate_to_pose`)
* Context Awareness via Blackboard
* Servo Control Hooks for camera tilt
* Failure Recovery for incomplete goals

###  Launching the Autonomy Node

```bash
cd ~/breakers_ws/src/gazebo_ignition_fortress/test_folder
python3 app.py
```

This initializes the full mission logic — subscribing to detection topics, publishing visualization markers, and autonomously executing the full workflow.

---

##  Key Dependencies

* `ros-humble-slam-toolbox`
* `ros-humble-nav2-bringup`
* `ros-humble-rviz2`
* `ros-humble-robot-localization`
* `ros-humble-ros2-control`
* `sllidar_ros2`
* `OpenCV`, `PyTorch`

---

##  Credits

| Role                     | Contributors                                                                                        |
| :----------------------- | :-------------------------------------------------------------------------------------------------- |
| **Developers**           | Limit Breakers Team                                                                                 |
| **Mentors & References** | [Josh Newans](https://github.com/joshnewans), [Collins Omariba](https://github.com/Collins-Omariba) |
| **Inspired by**          | [2025 KNIGHTS Robot](https://github.com/roboticsdojo/2025-KNIGHTS-Robot)                            |
| **Special Thanks**       | Robotics Dojo, Dr. Shohei Aoki, Lenny Ng’ang’a                                                      |

---

##  CAD & Robot Previews

**CAD Preview**
![CAD](https://github.com/user-attachments/assets/3dc8365f-aca1-4d4e-9a0a-158cf7830ffe)

**Physical Robot** <img width="322" height="235" alt="Physical Robot" src="https://github.com/user-attachments/assets/5bba7aea-4be7-44ac-9c19-dc1476c55bec" />

---

##  Competition & Publications

| Resource                           | Link                                                                                                   |
| :--------------------------------- | :----------------------------------------------------------------------------------------------------- |
| **Robotics Dojo Competition 2025** | [roboticsdojo.github.io/competition2025.html](https://roboticsdojo.github.io/competition2025.html)     |
| **Technical Paper (PDF)**          | [2_limit_breakers.pdf](https://roboticsdojo.github.io/files/technical_paper/2025/2_limit_breakers.pdf) |
| **Poster (PDF)**                   | [2_limit_breakers_poster.pdf](https://roboticsdojo.github.io/files/poster/2025/2_limit_breakers.pdf)   |

---


