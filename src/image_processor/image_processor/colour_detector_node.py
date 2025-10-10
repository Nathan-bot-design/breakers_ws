import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2
import numpy as np

class ColorDetector(Node):
    def __init__(self):
        super().__init__('colour_detector')
        self.bridge = CvBridge()

        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        self.color_pub = self.create_publisher(String, '/detected_colour', 10)

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            lower_red1 = np.array([0, 120, 70])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 120, 70])
            upper_red2 = np.array([180, 255, 255])

            lower_blue = np.array([100, 150, 0])
            upper_blue = np.array([140, 255, 255])

            mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask_red = mask_red1 | mask_red2
            mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

            red_pixels = cv2.countNonZero(mask_red)
            blue_pixels = cv2.countNonZero(mask_blue)

            if red_pixels > 500:
                detected_color = "White"
            elif blue_pixels > 500:
                detected_color = "Blue"
            else:
                detected_color = "Unregistered"

            msg_out = String()
            msg_out.data = detected_color
            self.color_pub.publish(msg_out)

            cv2.putText(frame, f"{detected_color}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.imshow("Colour Detection", frame)
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f"Failed to process image: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = ColorDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()