import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import numpy as np
from rclpy.qos import QoSProfile, QoSReliabilityPolicy

class LaserScanFilter(Node):
    def __init__(self):
        super().__init__('laserscan_filter')
        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            depth=10
        )
        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, qos_profile)
        self.publisher = self.create_publisher(LaserScan, '/scan_gazebo', qos_profile)


    def scan_callback(self, msg):
        new_scan = msg
       
        self.publisher.publish(new_scan)

rclpy.init()
node = LaserScanFilter()
rclpy.spin(node)
rclpy.shutdown()
