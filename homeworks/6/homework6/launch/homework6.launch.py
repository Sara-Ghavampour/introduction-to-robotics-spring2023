from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import (
    IncludeLaunchDescription
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, GroupAction,
                            IncludeLaunchDescription, TimerAction)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node, PushRosNamespace


ARGUMENTS = [
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'),
        DeclareLaunchArgument(
            'description',
            default_value='true',
            description='Launch eddiebot description'
            ),
        DeclareLaunchArgument('model', default_value='eddie_kinect_v1',
                              choices=['eddie_kinect_v1'],
                              description='Eddiebot Model'),
        DeclareLaunchArgument(
            'namespace',
            default_value='',
            description='Robot namespace'
            ),
        ]

def generate_launch_description():

    pkg_ros_gz_sim = get_package_share_directory('eddiebot_gazebo')

    ld = LaunchDescription(ARGUMENTS)

    pkg_eddiebot_description = get_package_share_directory('eddiebot_description')


    description_launch = PathJoinSubstitution(
        [pkg_eddiebot_description, 'launch', 'robot_description.launch.py']
    )

    namespace = LaunchConfiguration('namespace')





    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_ros_gz_sim, 'launch', 'eddiebot_gz_sim.launch.py')),
            launch_arguments={'world': 'maze'}.items(),
        )
    )

    ld.add_action(
        Node(
            package='homework6',
            executable='homework6',
        )
    )

    ld.add_action(
        Node(
            package='depthimage_to_laserscan',
            executable='depthimage_to_laserscan_node',
        )
    )

   
    
    ld.add_action(
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=['/lidar@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/model/eddiebot/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/kinect_rgbd_camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
            '/kinect_rgbd_camera/depth_image@sensor_msgs/msg/Image@gz.msgs.Image',
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist'],
            remappings=[('/model/eddiebot/tf','tf'),
            ('/kinect_rgbd_camera/camera_info','depth_camera_info'),
            ('/kinect_rgbd_camera/depth_image','depth')]


        )
    )

    ld.add_action(
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=[
                "0", "0", "0", "0", "0", "0", "eddiebot/base_footprint", "base_footprint",
            ]
        )
    )
    
    ld.add_action(
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',

            arguments=[
                "0", "0", "0", "0", "0", "0", "/world", "eddiebot/odom"
            ]
        )
    )

    ld.add_action(
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',

            arguments=[
                "0", "0", "0", "0", "0", "0", "/camera_link", "camera_depth_frame"
            ]
        )
    )


    ld.add_action(GroupAction([
        PushRosNamespace(namespace),

        Node(package='rviz2',
             executable='rviz2',
             parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
             remappings=[
                ('/tf', 'tf'),
                ('/tf_static', 'tf_static')
             ],
             output='screen'),

        # Delay launch of robot description to allow Rviz2 to load first.
        # Prevents visual bugs in the model.
        TimerAction(
            period=1.0,
            actions=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource([description_launch]),
                    launch_arguments=[('model', LaunchConfiguration('model')),
                                      ('use_sim_time', LaunchConfiguration('use_sim_time'))],
                    condition=IfCondition(LaunchConfiguration('description'))
                )])
    ]))
    
    
    return ld
