from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import (
    SetEnvironmentVariable, IncludeLaunchDescription,
    DeclareLaunchArgument, TimerAction
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os
import xacro

def generate_launch_description():
    # === Paths ===
    ros_gz_sim_pkg_path = get_package_share_directory('ros_gz_sim')
    robot_description_pkg_path = get_package_share_directory('rover_description')

    gz_launch_path = os.path.join(ros_gz_sim_pkg_path, 'launch', 'gz_sim.launch.py')
    xacro_file = os.path.join(robot_description_pkg_path, 'urdf', 'robot_v2.urdf.xacro')

    # === Process Xacro ===
    doc = xacro.process_file(xacro_file)
    robot_description = {'robot_description': doc.toxml()}

    # === Launch arguments ===
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock'
    )

    # === Robot state publisher ===
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': use_sim_time}]
    )

    # === Spawn robot at origin, wheels just above ground ===
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.15',
        ],
        output='screen',
    )

    # === Gazebo bridge ===
    bridge_params = os.path.join(
        get_package_share_directory('world_simulation'),
        'config',
        'gz_bridge.yaml'
    )

    start_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['--ros-args', '-p', f'config_file:={bridge_params}'],
        output='screen',
    )

    # === Launch description ===
    return LaunchDescription([
        use_sim_time_arg,
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_launch_path),
            launch_arguments={
                'gz_args': '-r empty.sdf',
                'on_exit_shutdown': 'true',
            }.items(),
        ),
        robot_state_publisher,
        start_gz_bridge,
        TimerAction(period=3.0, actions=[spawn_entity]),
    ])
