from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'image_processor'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='cypherjac',
    maintainer_email='cypherjac@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'image_processor_node = image_processor.image_processor_node:main',
            'camera_viewer_node = image_processor.camera_viewer_node:main',
            'colour_detector_node = image_processor.colour_detector_node:main',
            'disease_detector_node = image_processor.disease_detector_node:main',
        ],
    },
)
