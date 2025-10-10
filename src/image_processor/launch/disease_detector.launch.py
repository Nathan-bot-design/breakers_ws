from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='image_processor',
            executable='disease_detector_node',
            name='disease_detector',
            output='screen',
            prefix='gnome-terminal -- bash -c',
        )
    ])
