import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node

from std_msgs.msg import String
import time

from yinyang_interfaces.action import Goodbye
from yinyang_interfaces.srv import Datasrv


class YinNode(Node):
    
    def __init__(self):
        super().__init__('yinnode')
        self.end=False
        self.conv = [
            "I am Yin, some mistake me for an actual material entity but I am more of a concept",
            "Interesting Yang, so one could say, in a philosophical sense, we are two polar elements",
            "We, Yang, are therefore the balancing powers in the universe.",
            "Difficult and easy complete each other.",
            "Long and short show each other.",
            "Noise and sound harmonize each other.",
            "You shine your light."
        ]    

        self.counter = 0


        self.declare_parameter('shout', True)
        self.declare_parameter('opacity', 100)
        self.yin_client = self.create_client(Datasrv, 'yang_service')

        self.yin_service = self.create_service(Datasrv, 'yin_service', self.yin_service_callback)
        
        self.ytimer = self.create_timer(1, self.yin_timer)
        self.endtimer = self.create_timer(1, self.end_timer)

        self.publisher_ = self.create_publisher(String, 'conversation', 10)
        
        self.action_server = ActionServer(self, Goodbye,'goodbye',self.execute)
        
    
        
        while not self.yin_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('waiting for server')

        self.req = Datasrv.Request()
        self.yin_cli_send_flag = True




    def yin_service_callback(self, req, res):
        self.get_logger().info(req.a)
        pub_sent = 'Yang client masage: '+ req.a + ', ' + str(req.len)
        sum = 0
        for word in req.a:
            for ch in word:
                sum += ord(ch)

        pub_sent +=  ', ' + str(sum)
        msg = String()        
        msg.data = pub_sent
        self.publisher_.publish(msg)
        res.checksum = sum
        self.yin_cli_send_flag = True
        
        return res    
        
    

    def yin_timer(self):
        
        if(self.yin_cli_send_flag and self.counter !=7):
            isshout = self.get_parameter('shout').get_parameter_value().bool_value
            
            req_str = self.conv[self.counter]
            length = len(req_str)
            if isshout:
                req_str = '**' + req_str + '**'
                length += 4
            
            self.req.a = req_str
            self.req.len = length
            self.counter +=1
            _future = self.yin_client.call_async(self.req)
            self.get_logger().info('request from yin_client to yin_server sent')
            self.yin_cli_send_flag = False

    def execute(self, goal_handle):
        
        if 'bye' in goal_handle.request.a:
            self.get_logger().info('Goodbye accepted')
            self.get_logger().info(goal_handle.request.a)
            feedback_msg = Goodbye.Feedback()
            cur_opacity = self.get_parameter('opacity').get_parameter_value().integer_value
            
        
            while    cur_opacity >-1 :
                feedback_msg.opacity = cur_opacity
                goal_handle.publish_feedback(feedback_msg)
                cur_opacity -=1
                time.sleep(0.01)

            
            goal_handle.succeed()
            result = Goodbye.Result()
            result.b = 'farewell'
            self.done=True
            return result            


    def end_timer(self) :
        if(self.end): 
            self.destroy_node()
            rclpy.shutdown()  


def main(args=None):
    rclpy.init(args=args)
    yinnode = YinNode()
    rclpy.spin(yinnode)
    yinnode.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()






