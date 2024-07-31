import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import random

class LiDARPublisher(Node):
    def __init__(self):
        super().__init__('lidar_publisher')
        self.publisher_ = self.create_publisher(LaserScan, 'scan', 10)
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = LaserScan()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'laser_frame'
        msg.angle_min = -1.57
        msg.angle_max = 1.57
        msg.angle_increment = 3.14 / 360
        msg.time_increment = 0.0
        msg.scan_time = 0.1
        msg.range_min = 0.12
        msg.range_max = 3.5
        msg.ranges = [random.uniform(0.12, 3.5) for _ in range(360)]
        msg.intensities = [random.uniform(0, 1) for _ in range(360)]
        
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing LiDAR scan')

def main(args=None):
    rclpy.init(args=args)
    lidar_publisher = LiDARPublisher()
    rclpy.spin(lidar_publisher)
    lidar_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()