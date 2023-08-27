from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='lab7',
            executable='lab7',
            name='lab7'
        ), 
        
        Node(
            package='ros_gz_bridge', 
            executable='parameter_bridge', 
            arguments=['/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist']
        )
        
    ])