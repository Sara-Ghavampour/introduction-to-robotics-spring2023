import rclpy
import time
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class Lab8(Node):
    def __init__(self):
        super().__init__('lab8')
        
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subsciber = self.create_subscription(LaserScan,'/lidar',self.subscribe_callback,10)
        # self.call_timer = self.create_timer(2.0, self.timer_callback)

        self.first_hit = True
        self.b = False
        self.r = False


    def subscribe_callback(self,msg):
        self.allmore = True
        for i in msg.ranges:
            if i < 0.6:
                self.allmore = False
                break

        velocity = Twist()
        if self.allmore :
            velocity.linear.x=0.8
            velocity.angular.z = 0.0

        else :
            if self.first_hit :
                self.hit_time =  time.time()  
                self.first_hit = False
                self.b = True

            if self.b:
                velocity.linear.x=-0.8
                velocity.angular.z = 0.0
                if abs(time.time() -self.hit_time) > 1.5:
                    self.b = False
                    self.r = True      
                    self.rt = time.time()  

            if self.r:
                velocity.linear.x=0.0
                velocity.angular.z = 0.6

                if abs(self.rt - time.time())>1.5:
                    self.first_hit = True
                    self.r = False

        self.publisher.publish(velocity)        
                



    # def timer_callback(self):
        
    #     msg_v = Twist()
        
    #     if not self.going_down: # up 
    #         msg_v.linear.x = 1.0
    #         msg_v.angular.z = 0.0
            
    #         self.going_down=True
                
    #     else: # down
    #         msg_v.linear.x = -1.0
    #         msg_v.angular.z = 0.0
            
    #         self.going_down=False            
        
    #     self.publisher.publish(msg_v)
    
def main(args=None):    
    rclpy.init(args=args)
    lab8 = Lab8()
    rclpy.spin(lab8)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
