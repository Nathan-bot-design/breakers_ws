import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, RegisterEventHandler
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.event_handlers import OnProcessStart
from launch.substitutions import Command
from launch_ros.actions import Node


def generate_launch_description():

    package_name='dojo'  # change if yours is different

    # robot_state_publisher (your existing rsp.launch.py)
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name),'launch','rsp.launch.py'
        )]),
        launch_arguments={'use_sim_time': 'false', 'use_ros2_control': 'true'}.items()
    )

    # twist_mux
    twist_mux_params = os.path.join(get_package_share_directory(package_name),'config','twist_mux.yaml')
    twist_mux = Node(
        package="twist_mux",
        executable="twist_mux",
        parameters=[twist_mux_params],
        remappings=[('/cmd_vel_out','/diff_cont/cmd_vel_unstamped')]
    )

    # robot_description (read from robot_state_publisher params)
    robot_description = Command(['ros2 param get --hide-type /robot_state_publisher robot_description'])

    # controller params file
    controller_params_file = os.path.join(get_package_share_directory(package_name),'config','my_controllers.yaml')

    # controller manager
    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[{'robot_description': robot_description}, controller_params_file],
        output='screen'
    )
    delayed_controller_manager = TimerAction(period=3.0, actions=[controller_manager])

    # spawn diff_cont when controller_manager starts
    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont"],
    )
    delayed_diff_drive_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[diff_drive_spawner],
        )
    )

    # spawn joint_state_broadcaster
    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
    )
    delayed_joint_broad_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[joint_broad_spawner],
        )
    )

    # spawn imu broadcaster (reads your exported state interfaces named "imu")
    imu_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["imu_broad"],
    )
    delayed_imu_broad_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[imu_broad_spawner],
        )
    )

    # ekf_node
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[os.path.join(get_package_share_directory(package_name), 'config', 'ekf.yaml')]
    )

    # Return ordered launch description (keep EKF after the controllers are started)
    return LaunchDescription([
        rsp,
        twist_mux,
        delayed_controller_manager,
        delayed_diff_drive_spawner,
        delayed_joint_broad_spawner,
        delayed_imu_broad_spawner,
        ekf_node,
    ])
