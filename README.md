# AgriBot Rover – Hack the Hills 2025 🌽🚜

Autonomous all-terrain robot designed to transport agricultural waste (like corn stalks and husks) from hillside farms to roadside collection points. Developed as a submission for the **AgriSpark Hackathon 2025 – "Hack the Hills"**, this project aims to reduce labor, time, and risk for farmers working in mountainous areas.

---

## 📌 Problem Statement

Farmers in hilly regions face difficulties transporting post-harvest corn waste from the fields down to roads where trucks can access. It's labor-intensive, time-consuming, and dangerous – especially during the rainy season.

---

## 💡 Our Solution: AgriBot Rover

An autonomous wheeled robot designed to:

- Traverse uneven, sloped terrain
- Carry **10–15 kg** of agricultural waste per trip
- Automatically return to base for the next load
- Use GPS, IMU, and obstacle sensors for navigation
- Be monitored and controlled via a simple web dashboard

---

## Overview

| Item | Value |
|------|-------|
| ROS version | ROS 2 Jazzy |
| Simulator | Gazebo Harmonic (gz-sim) |
| Drive type | Skid-steer (4-wheel differential) |
| Sensors | 2D LiDAR, monocular camera |
| Payload capacity | 10–15 kg |
| Terrain | 40 m × 40 m hillside, 8 m elevation change |

---

## Package Structure

```
agribot/
├── rover_description/              # Robot model
│   ├── urdf/
│   │   ├── robot_v2.urdf.xacro    # Top-level xacro (active — AgriBot V2)
│   │   ├── main_v2.xacro          # Chassis, wheels, cargo bed, bumper, plugins
│   │   ├── robot.urdf.xacro       # Legacy V1 model
│   │   ├── main.xacro             # Legacy V1 body
│   │   ├── lidar.xacro            # 2D LiDAR sensor
│   │   ├── depth_camera.xacro     # Forward-facing camera
│   │   └── inertial_macros.xacro
│   ├── meshes/                    # STL / DAE mesh files
│   ├── config/
│   │   └── view_config.rviz       # RViz display config
│   └── launch/
│       └── display.launch.py      # RViz model viewer
│
└── world_simulation/              # Simulation environment
    ├── worlds/
    │   └── grass_world.sdf        # Hillside terrain world
    ├── models/
    │   └── hill_terrain/          # 40 × 40 m heightmap terrain model
    │       └── materials/textures/
    │           ├── heightmap.png  # 257×257 grayscale elevation map
    │           ├── grass.png
    │           └── dirt.png
    ├── config/
    │   └── gz_bridge.yaml         # ROS ↔ Gazebo topic bridges
    ├── scripts/
    │   └── generate_heightmap.py
    └── launch/
        ├── sim.launch.py          # Full hillside simulation
        └── gazebo.launch.py       # Empty world (quick testing)
```

---

## Robot Description (V2)

```
base_link
├── base_footprint
├── chassis                    (dark-grey frame — 0.70 × 0.55 × 0.10 m)
├── front_left_wheel_joint     (continuous, driven)
├── front_right_wheel_joint    (continuous, driven)
├── rear_left_wheel_joint      (continuous, driven)
├── rear_right_wheel_joint     (continuous, driven)
├── cargo_bed                  (brown platform — 0.36 × 0.50 × 0.04 m)
├── cargo_wall_front           (olive-green, blocks cargo sliding on descent)
├── cargo_wall_left            (olive-green side wall)
├── cargo_wall_right           (olive-green side wall, rear open for loading)
├── body                       (safety-yellow electronics box — 0.26 × 0.50 × 0.22 m)
├── front_bumper               (dark-grey protective bar)
├── laser_joint → laser_frame  (2D LiDAR, top of body)
└── camera_joint → camera_link (monocular camera, front of body)
```

**Key dimensions**

| Property | V1 | V2 |
|----------|----|----|
| Chassis size | 0.60 × 0.40 × 0.20 m | 0.70 × 0.55 × 0.10 m |
| Wheel radius | 0.075 m | **0.10 m** |
| Track width | 0.45 m | **0.66 m** |
| Wheelbase | 0.40 m | 0.46 m |
| Cargo area | flat tray, no walls | 3-sided bed, open rear |
| Front protection | none | bumper bar |

**Sensors**

| Sensor | Topic | Rate |
|--------|-------|------|
| 2D LiDAR (360°, 0.3–12 m) | `/scan` | 10 Hz |
| Monocular camera (640×480) | `/camera/image_raw` | 10 Hz |

---

## ROS Topics

| Topic | Type | Direction |
|-------|------|-----------|
| `/cmd_vel` | `geometry_msgs/Twist` | Input — drive command |
| `/odom` | `nav_msgs/Odometry` | Output — wheel odometry |
| `/scan` | `sensor_msgs/LaserScan` | Output — LiDAR |
| `/joint_states` | `sensor_msgs/JointState` | Output — wheel angles |
| `/tf` | `tf2_msgs/TFMessage` | Output — transforms |
| `/clock` | `rosgraph_msgs/Clock` | Output — sim time |

---

## Dependencies

```bash
sudo apt install \
  ros-jazzy-ros-gz \
  ros-jazzy-ros-gz-bridge \
  ros-jazzy-ros-gz-image \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-xacro \
  ros-jazzy-rviz2
```

---

## Build

```bash
cd ~/ros2_ws
colcon build --packages-select rover_description world_simulation
source install/setup.bash
```

---

## Launch

### Hillside simulation (main scenario)

```bash
ros2 launch world_simulation sim.launch.py
```

The robot spawns at the **hilltop** (Y = +16 m, Z ≈ 8.5 m) facing downhill toward the valley drop-off point at Y = −20 m.

### Empty world (fast testing)

```bash
ros2 launch world_simulation gazebo.launch.py
```

### RViz model viewer (no Gazebo)

```bash
ros2 launch rover_description display.launch.py
```

---

## Teleoperation

```bash
# In a second terminal after the simulation is running
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Install if missing: `sudo apt install ros-jazzy-teleop-twist-keyboard`

---

## Terrain

The hillside world uses a procedurally generated heightmap that replicates a typical mountainous farm slope.

| Property | Value |
|----------|-------|
| Footprint | 40 m × 40 m |
| Elevation range | 0.1 m → 7.8 m |
| Average grade | ~15 % (≈ 8.5°) |
| Terrain friction | μ = 0.85 |
| Wheel friction | μ = 0.90 |

Hilltop is at **Y = +20 m** (farm field / robot start), valley at **Y = −20 m** (roadside drop-off).

To regenerate the heightmap with a different shape, edit `scripts/generate_heightmap.py` then:

```bash
python3 src/agribot/world_simulation/scripts/generate_heightmap.py
colcon build --packages-select world_simulation
```

---

## Roadmap

| Feature | Status |
|---------|--------|
| Robot URDF V2 (wider stance, cargo bed, bumper) | ✅ Done |
| Hillside Gazebo world (40 × 40 m heightmap) | ✅ Done |
| ROS–Gazebo bridge (cmd_vel, odom, LiDAR, camera) | ✅ Done |
| Teleoperation | ✅ Ready |
| IMU sensor + tilt estimation | 🔲 Planned |
| EKF odometry fusion (wheel + IMU) | 🔲 Planned |
| GPS localisation | 🔲 Planned |
| Nav2 autonomous path planning | 🔲 Planned |
| SLAM hillside mapping | 🔲 Planned |
| Cargo contact sensor (detect load/unload) | 🔲 Planned |
| Web monitoring dashboard | 🔲 Planned |
| ros2_control hardware interface | 🔲 Planned |

---


AgriSpark Hackathon 2025 – "Hack the Hills"
