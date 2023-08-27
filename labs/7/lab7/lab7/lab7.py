import rclpy
from rclpy.node import Node
import time
import random 
from rclpy.action import ActionClient
from geometry_msgs.msg import Twist


class Lab7(Node):
    def __init__(self):
        super().__init__('lab7')
        
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.call_timer = self.create_timer(2.0, self.timer_callback)

        self.going_down = False



    def timer_callback(self):
        
        msg_v = Twist()
        
        if not self.going_down: # up 
            msg_v.linear.x = 1.0
            msg_v.angular.z = 0.0
            
            self.going_down=True
                
        else: # down
            msg_v.linear.x = -1.0
            msg_v.angular.z = 0.0
            
            self.going_down=False            
        
        self.publisher.publish(msg_v)
    
def main(args=None):    
    rclpy.init(args=args)
    lab7 = Lab7()
    rclpy.spin(lab7)
    rclpy.shutdown()


if __name__ == '__main__':
    main()