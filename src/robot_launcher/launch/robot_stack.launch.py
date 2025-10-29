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
                # {'FrameDurationLimits': [17000, 17000]}
                {'FrameDurationLimits': [5000, 5000]}
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




# from launch import LaunchDescription
# from launch_ros.actions import Node

# def generate_launch_description():
#     return LaunchDescription([

#         # Camera node (IMX219 on Pi v2)
#         Node(
#             package='camera_ros',
#             executable='camera_node',
#             name='camera',
#             parameters=[
#                 {'width': 640},              # safer resolution for Pi 4
#                 {'height': 480},
#                 {'format': 'YUYV'},          # YUYV or NV12 works, NV12 lighter
#                 {'role': 'video'},           # use "video" not "still"
#                 {'framerate': 10.0},         # limit FPS
#                 {'jpeg_quality': 50},        # balance quality vs size
#             ],
#             remappings=[
#                 ('out', '/camera/image_raw')
#             ]
#         ),

#         # Throttle node (extra protection if camera outputs too much)
#         Node(
#             package='image_throttle',
#             executable='image_throttle',
#             name='image_throttle',
#             output='screen',
#             parameters=[
#                 {'target_fps': 5}            # only forward 5 fps
#             ],
#             remappings=[
#                 ('in', '/camera/image_raw'),
#                 ('out', '/camera/image_throttled')
#             ]
#         ),

#         # Republish compressed stream
#         Node(
#             package='image_transport',
#             executable='republish',
#             name='republisher',
#             arguments=['raw', 'compressed'],
#             remappings=[
#                 ('in', '/camera/image_throttled'),
#                 ('out', '/camera/image_raw/compressed')
#             ]
#         )
#     ])


# from launch import LaunchDescription
# from launch_ros.actions import Node

# def generate_launch_description():
#     return LaunchDescription([

#         # Camera node for OV5647 (Pi Camera v1)
#         Node(
#             package='camera_ros',
#             executable='camera_node',
#             name='camera',
#             parameters=[
#                 {'width': 320},
#                 {'height': 240},
#                 {'format': 'YUYV'},        # ✅ supported by OV5647
#                 {'role': 'video'},
#                 {'framerate': 5.0},
#                 {'jpeg_quality': 40},
#             ],
#             remappings=[
#                 ('out', '/camera/image_raw/compressed')
#             ]
#         ),

#         # Optional throttle node
#         Node(
#             package='image_throttle',
#             executable='image_throttle',
#             name='image_throttle',
#             output='screen',
#             parameters=[
#                 {'target_fps': 2}
#             ],
#             remappings=[
#                 ('in', '/camera/image_raw/compressed'),
#                 ('out', '/camera/image_throttled/compressed')
#             ]
#         ),
#     ])
