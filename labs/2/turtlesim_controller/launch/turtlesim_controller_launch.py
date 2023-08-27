from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim_controller',
            executable='turtlesim_controller',
            name='custom_turtlesim_controller',
            output='screen',
            emulate_tty=True,
            parameters=[
                {'stop': True}
            ]
        )
    ])