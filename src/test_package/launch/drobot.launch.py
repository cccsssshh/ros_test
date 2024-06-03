from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    package_share_directory = get_package_share_directory('test_package')
    params_file = os.path.join(package_share_directory, 'coordinate.yaml')
    
    return LaunchDescription(
        [
            Node(
                namespace= '',
                package= 'test_package',
                executable= 'drobot_motor',
                output= 'screen',
                parameters=[params_file]
            )
        ]
    )