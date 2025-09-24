from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='camera_ros',
            executable='camera_node',
            name='camera',
            parameters=[
                {'width': 240},
                {'height': 160},
                {'format': 'YUYV'},
                {'role': 'still'},
                {'jpeg_quality': 25},
                {'FrameDurationLimits': [17000, 17000]}
            ],
            remappings=[
                ('out', '/camera/image_raw')
            ]
        ),
        Node(
            package='image_throttle',
            executable='image_throttle',
            name='image_throttle',
            output='screen'
        ),
        Node(
            package='image_transport',
            executable='republish',
            name='republisher',
            arguments=['raw', 'compressed'],
            remappings=[
                ('in', '/camera/image_throttled'),
                ('out', '/camera/image_compressed')
            ]
        )
    ])
