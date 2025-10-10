from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='image_processor',
            executable='colour_detector_node',
            name='colour_detector',
            output='screen',
            prefix='gnome-terminal -- bash -c',
        )
    ])
