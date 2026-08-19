from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim'
    )

    controller_node = Node(
        package='midnight_tuner',
        executable='controller',
        name='midnight_tuner'
    )

    return LaunchDescription([
        turtlesim_node,
        controller_node
    ])
