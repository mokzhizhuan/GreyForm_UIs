import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class LiDARSubscriber(Node):
    def __init__(self):
        super().__init__("lidar_subscriber")
        self.subscription = self.create_subscription(
            LaserScan, "scan", self.listener_callback, 10
        )
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f"Received LiDAR scan: {msg.ranges[:10]}...")


def main(args=None):
    rclpy.init(args=args)
    lidar_subscriber = LiDARSubscriber()
    rclpy.spin(lidar_subscriber)
    lidar_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
