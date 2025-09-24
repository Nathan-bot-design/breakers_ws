#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import RPi.GPIO as GPIO
import time

SERVO_PIN = 18  # GPIO18 (physical pin 12)

def angle_to_duty_cycle(angle: float) -> float:
    # Map 0–180 degrees to duty cycle (2–12%)
    return 2 + (angle / 18)

class ServoNode(Node):
    def __init__(self):
        super().__init__('servo_node')

        self.subscription = self.create_subscription(
            Float32,
            'servo_angle',
            self.listener_callback,
            10
        )

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SERVO_PIN, GPIO.OUT)
        self.pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz
        self.pwm.start(0)

        self.get_logger().info("Servo node started. Listening on /servo_angle topic...")

    def listener_callback(self, msg):
        angle = max(0, min(180, msg.data))  # clamp between 0 and 180
        duty = angle_to_duty_cycle(angle)
        self.pwm.ChangeDutyCycle(duty)
        self.get_logger().info(f"Servo set to {angle}° (duty {duty:.2f}%)")
        time.sleep(0.3)
        self.pwm.ChangeDutyCycle(0)  # stop to prevent jitter

def main(args=None):
    rclpy.init(args=args)
    node = ServoNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.pwm.stop()
        GPIO.cleanup()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
