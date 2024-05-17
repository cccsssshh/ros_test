from setuptools import find_packages
from setuptools import setup

setup(
    name='test_package_msg',
    version='0.0.0',
    packages=find_packages(
        include=('test_package_msg', 'test_package_msg.*')),
)
