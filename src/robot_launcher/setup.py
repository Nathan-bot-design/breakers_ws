from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'robot_launcher'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='frost',
    maintainer_email='frost@todo.todo',
    description='Launch package for robot stack',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Add 
        ],
    },
)

