from setuptools import find_packages, setup
import os
from glob import glob


package_name = 'test_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name), glob('launch/*.py')),
        (os.path.join('share', package_name), glob('params/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='addinedu',
    maintainer_email='shcho9666@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "tcp_node = test_package.TcpNode:main",
            "control_tower = test_package.control_tower:main",
            "test_service_node = test_package.TestNode:main",
            "action_server = test_package.action_server:main",
            "action_client = test_package.action_client:main",
            "test = test_package.test:main",
            "robot_control = test_package.robot_control:main",
            "drobot_motor_test = test_package.drobot_motor_test:main",
            "nav_test = test_package.nav_test:main",
            "order_tracking_service_client = test_package.order_tracking_service_client:main",
            "order_info_service_server = test_package.order_info_service_server:main",
            "drobot_motor = test_package.drobot_motor:main",
            "amcl_sub = test_package.amcl_sub:main",
            "drobot_motor_1 = test_package.drobot_motor_1:main",
            "drobot_motor_2 = test_package.drobot_motor_2:main",
            "drobot_motor_3 = test_package.drobot_motor_3:main",
            "drobot_motor_tmp = test_package.drobot_motor_tmp:main",
            "drobot_motor_tmp2 = test_package.drobot_motor_tmp2:main",
        ],
    },
)
