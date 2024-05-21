from setuptools import find_packages, setup

package_name = 'test_package'

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
            "middle_server = test_package.middle_server:main",
            "amcl_server = test_package.amcl_server:main",
        ],
    },
)
