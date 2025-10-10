from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='image_processor',
            executable='camera_viewer_node',
            name='camera_viewer',
            output='screen',
            prefix='gnome-terminal -- bash -c',
        )
    ])
