import rclpy
from rclpy.node import Node
from my_robot_wallinterfaces.msg import (
    SelectionWall,
    FileExtractionMessage,
)
from my_robot_wallinterfaces.srv import SetLed
from std_msgs.msg import String
from stl import mesh
import pandas as pd


class ListenerNode(Node):
    def __init__(self):
        super().__init__("listener_node")
        self.file_subscription_ = self.create_subscription(
            FileExtractionMessage,  # Correct message type
            "file_extraction_topic",  # Correct topic
            self.file_listener_callback,
            10,
        )
        self.selection_subscription_ = self.create_subscription(
            SelectionWall,  # Correct message type
            "selection_wall_topic",  # Correct topic
            self.selection_listener_callback,
            10,
        )
        self.file_callback = None
        self.selection_callback = None
        self.wallselection = None
        self.typeselection = None
        self.sectionselection = None
        self.get_logger().info("ListenerNode has been started.")

    def file_listener_callback(self, msg):
        try:
            stl_data = bytes(msg.stl_data)  # Convert list of uint8 back to bytes
            self.get_logger().info(
                "STL file received and processed: %s" % msg.stl_data[:100]
            )
            with open('/tmp/temp_stl_file.stl', 'wb') as f:
                f.write(stl_data)
            stl_mesh = mesh.Mesh.from_file('/tmp/temp_stl_file.stl')
            self.get_logger().info("Excel file path: %s" % msg.excelfile)
            # Process the Excel file
            self.process_excel_data(msg.excelfile)
            if self.file_callback:
                self.file_callback(stl_mesh)
        except Exception as e:
            self.get_logger().error(f"Failed to process received STL file: {e}")

    def selection_listener_callback(self, msg):
        try:
            self.get_logger().info(
                "Selection message received: wallselections=%d, typeselection=%s, sectionselection=%d"
                % (msg.wallselection, msg.typeselection, msg.sectionselection)
            )
            if self.selection_callback:
                self.selection_callback(msg)
        except Exception as e:
            self.get_logger().error(f"Failed to publish selection message: {e}")

    def process_excel_data(self, excel_filepath):
        try:
            df = pd.read_excel(excel_filepath)
            self.get_logger().info("Excel data processed successfully.")
            # You can add further processing logic here
        except FileNotFoundError as e:
            self.get_logger().error(f"Excel file not found: %e")
        except Exception as e:
            self.get_logger().error(f"Failed to process Excel file: %e")

    def set_file_callback(self, callback):
        self.file_callback = callback

    def set_selection_callback(self, callback):
        self.selection_callback = callback


def main(args=None):
    rclpy.init(args=args)
    listenerNode = ListenerNode()
    rclpy.spin(listenerNode)
    listenerNode.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
