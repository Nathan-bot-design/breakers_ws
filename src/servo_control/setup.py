from setuptools import find_packages, setup

package_name = 'servo_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='limitbreakers',
    maintainer_email='kingorinathan10@gmail.com',
    description='Servo control node for Raspberry Pi using GPIO',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'servo_node = servo_control.servo_node:main',
        ],
    },
)
