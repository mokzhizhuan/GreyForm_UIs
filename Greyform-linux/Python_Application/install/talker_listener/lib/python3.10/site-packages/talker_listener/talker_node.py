import rclpy
from rclpy.node import Node
import sys
from my_robot_wallinterfaces.msg import (
    FileExtractionMessage,
    SelectionWall,
)
from my_robot_wallinterfaces.srv import SetLed
from std_msgs.msg import String
import pandas as pd
import numpy as np
import sys

sys.path.append("/home/winsys/ros2_ws/src/Greyform-linux/Python_Application")
import PythonApplication.dialoglogger as logs


class TalkerNode(Node):
    def __init__(self):
        super().__init__("talker_node")
        self.file_publisher_ = self.create_publisher(
            FileExtractionMessage, "file_extraction_topic", 10
        )
        self.selection_publisher_ = self.create_publisher(
            SelectionWall, "selection_wall_topic", 10
        )
        self.message = ""
        self.get_logger().info("TalkerNode has been started.")

    def publish_file_message(self, file_path, excel_filepath):
        try:
            with open(file_path, "rb") as f:
                stl_data = f.read()
            msg = FileExtractionMessage()
            msg.stl_data = list(stl_data)  # Convert bytes to a list of uint8
            msg.excelfile = excel_filepath
            self.file_publisher_.publish(msg)
            self.message += f"STL file published: {stl_data[:100]}"
            self.message += f"Excel file path: {excel_filepath}"
        except FileNotFoundError as e:
            message = f"File not found: {e}"
            self.show_error_dialog(message)
        except Exception as e:
            message = f"Failed to read and publish STL file: {e}"
            self.show_error_dialog(message)

    def publish_selection_message(self, wall_number, sectionnumber, picked_position):
        try:
            msg = SelectionWall()
            msg.wallselection = int(wall_number)
            msg.typeselection = f"Wall Number {wall_number}"
            msg.sectionselection = sectionnumber
            picked_position = [
                int(picked_position[0]),
                int(picked_position[1]),
                int(picked_position[2]),
            ]
            msg.picked_position = picked_position
            self.selection_publisher_.publish(msg)
            self.message += f"Selection message published: wallselections={msg.wallselection}, typeselection={msg.typeselection}, sectionselection={msg.sectionselection}"
            self.message += f"\n {str(msg.picked_position.tolist())}"
            self.show_info_dialog(self.message)
        except Exception as e:
            message = f"Failed to publish selection message: {e}"
            self.show_error_dialog(message)

    def timer_callback(self):
        msg = String()
        msg.data = f"Hello everyone {self.count}"
        self.publisher_.publish(msg)
        self.count += 1
        self.get_logger().info(f"Publishing {msg.data}")

    def calculate_distance(self, point1, point2):
        return np.linalg.norm(point1 - point2)

    def show_info_dialog(self, message):
        dialog = logs.LogDialog(message, log_type="info")
        dialog.exec_()

    def show_error_dialog(self, message):
        dialog = logs.LogDialog(message, log_type="error")
        dialog.exec_()


def main(args=None):
    rclpy.init(args=args)
    talkerNode = TalkerNode()
    rclpy.spin(talkerNode)
    talkerNode.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
