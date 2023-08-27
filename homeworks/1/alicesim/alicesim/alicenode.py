import rclpy
from rclpy.node import Node

from std_msgs.msg import Char


class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('alicenode')
        self.subscription = self.create_subscription(
            Char,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        self.count=0
    def listener_callback(self, msg):
        key = "9812762781"
        key_idx = self.count % len(key)
        out = ord(key[key_idx])^ord(chr(msg.data))
        self.get_logger().info('I heard: "%c"' % chr(out))
        if chr(out)=='#': self.count = -1
        self.count +=1


def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()