import rclpy 
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
import numpy as np


class colorbased_navigation_eddie(Node):
    def __init__(self):
        super().__init__('colorbased_navigation_eddie')

        self.camera_subscriber = self.create_subscription(Image,'/kinect_rgbd_camera/image',self.camera_subscriber_callback,10)
        self.publisher = self.create_publisher(Twist, '/model/eddiebot/cmd_vel',10)
        self.timer = self.create_timer(0.2,self.timer_callback)

        self.red_tile = False
        self.green_tile = False
        self.yellow_tile = False
        self.move = True
        self.end_episode = False 
        self.rotation_counter = 0
        self.rotation_total = 80
        self.sign_rotation = 0.0

    def timer_callback(self):
        velocity= Twist()
        if self.move:
            velocity.linear.x= 1.0
            velocity.angular.z= self.sign_rotation
            
        if self.red_tile:
            self.move = False

            velocity.linear.x= 0.0
            velocity.angular.z= 0.23
            self.rotation_counter+=1
            if self.rotation_counter >= self.rotation_total:
                self.rotation_counter =0 
                self.red_tile = False 
                self.move = True



        if self.yellow_tile:
            self.move = False

            velocity.linear.x= 0.0
            velocity.angular.z= -0.23
            self.rotation_counter+=1
            if self.rotation_counter >= self.rotation_total:
                self.rotation_counter =0 
                self.yellow_tile = False 
                self.move = True  

        if self.green_tile:
            self.move = False
            velocity.linear.x= 0.0
            velocity.angular.z= -1.0


        self.publisher.publish(velocity)    

    def camera_subscriber_callback(self,msg):
        h_img = msg.height
        w_img = msg.width
        # w * c = step
        step = msg.step
        channels_img = int(step/w_img)

        data = np.array(msg.data)
        data = data.reshape((h_img,w_img,channels_img))
        # self.get_logger().info(str(data[h_img//2,w_img//2]))
        # red tile
        if data[:,:,0].max()>80 and data[:,:,1].max()<20 and data[:,:,2].max()<20:
            self.red_tile = True

        #green
        elif data[:,:,1].max()>80 and data[:,:,0].max()<20 and data[:,:,2].max()<20:
            self.green_tile = True
        #yellow
        elif data[:,:,1].max()>80 and data[:,:,0].max()>80 and data[:,:,2].max()<20:
            self.yellow_tile = True    

        
        color_square = data[:,:,2]<20
        left_side = color_square[:,0:w_img//2]
        right_side = color_square[:,w_img//2:]

        left_color = np.count_nonzero(left_side)
        right_color = np.count_nonzero(right_side)

        if left_color > right_color:
            self.sign_rotation = 0.075
        else:
            self.sign_rotation = -0.075
















        
       
 
 
        
                

        
        
        


        
    
def main(args=None):    
    rclpy.init(args=args)
    nav = colorbased_navigation_eddie()
    rclpy.spin(nav)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
