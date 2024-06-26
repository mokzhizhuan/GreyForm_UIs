import rclpy
from rclpy.node import Node
import sys
from my_robot_wallinterfaces.msg import (
    FileExtractionMessage,
    SelectionWall,
    CombinedMessage,
)
from my_robot_wallinterfaces.srv import SetLed
from std_msgs.msg import String


class TalkerNode(Node):
    def __init__(self):
        super().__init__("talker_node")
        self.file_publisher_ = self.create_publisher(
            FileExtractionMessage, "file_extraction_topic", 10
        )
        self.selection_publisher_ = self.create_publisher(
            SelectionWall, "selection_wall_topic", 10
        )
        self.get_logger().info("TalkerNode has been started.")

    def publish_file_message(self, file_path, excel_filepath):
        try:
            with open(file_path, "rb") as f:
                stl_data = f.read()
            msg = FileExtractionMessage()
            msg.stl_data = list(stl_data)  # Convert bytes to a list of uint8
            msg.excelfile = excel_filepath
            self.file_publisher_.publish(msg)
            self.get_logger().info("STL file published: %s" % stl_data[:100])
            self.get_logger().info("Excel file path: %s" % excel_filepath)
        except FileNotFoundError as e:
            self.get_logger().error(f"File not found: {e}")
        except Exception as e:
            self.get_logger().error(f"Failed to read and publish STL file: {e}")

    def publish_selection_message(self):
        try:
            msg = SelectionWall()
            msg.wallselections = 1
            msg.typeselection = "typeselection"
            msg.sectionselection = 2
            self.selection_publisher_.publish(msg)
            self.get_logger().info(
                "Selection message published: wallselections=%d, typeselection=%s, sectionselection=%d"
                % (wallselections, typeselection, sectionselection)
            )
        except Exception as e:
            self.get_logger().error(f"Failed to publish selection message: {e}")

    def timer_callback(self):
        msg = String()
        msg.data = f"Hello everyone {self.count}"
        self.publisher_.publish(msg)
        self.count += 1
        self.get_logger().info(f"Publishing {msg.data}")


def main(args=None):
    rclpy.init(args=args)

    # create node
    talkerNode = TalkerNode()

    # use node
    rclpy.spin(talkerNode)

    # destroy node
    talkerNode.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
