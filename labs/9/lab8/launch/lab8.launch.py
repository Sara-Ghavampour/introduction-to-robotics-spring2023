from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import (
    IncludeLaunchDescription
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    ld = LaunchDescription()
    


    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
            launch_arguments={'gz_args': '-r /home/softblue/gazebo_ws/src/lab8/sdf/maze.sdf'}.items(),
        )
    )

    ld.add_action(
        Node(
            package='lab8',
            executable='lab8',
        )
    )
    
    ld.add_action(
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=['/lidar@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/blue/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/cmd'],
            remappings=[('/blue/tf','/tf')]


        )
    )

    ld.add_action(
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=[
                "0", "0", "0", "0", "0", "0", "/vehicle_blue/chassis", "vehicle_blue/chassis/gpu_lidar"
            ]
        )
    )
    
    ld.add_action(
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',

            arguments=[
                "0", "0", "0", "0", "0", "0", "/world", "vehicle_blue/chassis/odom"
            ]
        )
    )
    


    return ld
