# Sara Ghavampour
#!/usr/bin/env python3
import math
import time
import random

import rclpy
from rclpy.node import Node
from std_msgs.msg import String,Int32
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from rclpy.action import ActionClient
from turtlesim.action import RotateAbsolute


class Turtlesim_controller(Node):
    
    def __init__(self):
        super().__init__("turtlesim_controller")
        self.declare_parameter('stop', True)

        self.cmd_publisher = self.create_publisher(Twist,'/turtle1/cmd_vel',10)
        self.pose_subscriber = self.create_subscription(Pose, "turtle1/pose", self.pose_subscriber_callback, 10)
        self.fsm_timer = self.create_timer(1, self.fsm)
        self.rotate_action_client = ActionClient(self, RotateAbsolute, '/turtle1/rotate_absolute')

        self.pos_x=0.0
        self.pos_y=0.0
        self.backward = False
        self.rotate = False
        self.stop = True
        self.wall_hit_time = 0


    def fsm(self):
        self.stop = self.get_parameter('stop').get_parameter_value().bool_value
        twist = Twist()
        
        # go farward
        if not self.stop and not self.backward and not self.rotate:
            twist.linear.x=+1.0
            twist.angular.z=0.0
            self.cmd_publisher.publish(twist)

        elif  not self.stop and not self.rotate and self.backward:
            if round(time.time()-self.wall_hit_time)<2:
                
                twist.linear.x=-1.0
                twist.angular.z=0.0
                self.cmd_publisher.publish(twist)
            else: 
                self.rotate=True 

        elif not self.stop and self.rotate :

            rotate_goal = RotateAbsolute.Goal()
            rotate_goal.theta = random.random()*6

            self.rotate_action_client.wait_for_server()
            self._send_rotate_goal_future = self.rotate_action_client.send_goal_async(rotate_goal, feedback_callback=self.feedback_callback)

    
        
    def pose_subscriber_callback(self,pose):
        if pose.x>11.0 or pose.x <0.2 or pose.y>11.0 or pose.y<0.2:
            self.backward = True
            self.wall_hit_time = time.time()
            self.pos_x=pose.x
            self.pos_y=pose.y
            
    def feedback_callback(self,feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info('Received feedback: {0}'.format(feedback.remaining))
        if (abs(feedback_msg.feedback.remaining) <= 0.03):
            self.back_to_1()

    def back_to_1(self):
        self.wall_hit_time=0
        self.stop = False # forward
        self.backward = False
        self.rotate=False
        



    


def main(args=None):
    print('fuckkk')
    rclpy.init(args=args)
    controller = Turtlesim_controller()
    rclpy.spin(controller)
    rclpy.shutdown()

if __name__ == '__main__':
    main()