import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import time

class ImageThrottle(Node):
    def __init__(self):
        super().__init__('image_throttle')
        self.sub = self.create_subscription(Image, '/camera/image_raw', self.callback, 10)
        self.pub = self.create_publisher(Image, '/image', 10)
        self.last_pub_time = time.time()

    def callback(self, msg):
        now = time.time()
        if now - self.last_pub_time >= 2.0:
            self.pub.publish(msg)
            self.last_pub_time = now

def main(args=None):
    rclpy.init(args=args)
    node = ImageThrottle()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
