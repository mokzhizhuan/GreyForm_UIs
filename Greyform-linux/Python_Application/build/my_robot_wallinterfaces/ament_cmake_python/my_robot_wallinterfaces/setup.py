from setuptools import find_packages
from setuptools import setup

setup(
    name='my_robot_wallinterfaces',
    version='0.0.0',
    packages=find_packages(
        include=('my_robot_wallinterfaces', 'my_robot_wallinterfaces.*')),
)
