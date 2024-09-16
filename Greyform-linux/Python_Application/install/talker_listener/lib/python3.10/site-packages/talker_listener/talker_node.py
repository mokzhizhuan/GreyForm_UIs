import rclpy
from rclpy.node import Node
import sys
from my_robot_wallinterfaces.msg import (
    FileExtractionMessage,
    SelectionWall,
)
from my_robot_wallinterfaces.srv import SetLed
from std_msgs.msg import String
import numpy as np
import sys
import subprocess
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
        self.spacing = "\n"
        self.title = "Publisher Node"
        self.active_dialog = None

    def publish_file_message(self, file_path, excel_filepath):
        try:
            with open(file_path, "rb") as f:
                stl_data = f.read()
            msg = FileExtractionMessage()
            msg.stl_data = list(stl_data)  # Convert bytes to a list of uint8
            msg.excelfile = excel_filepath
            self.file_publisher_.publish(msg)
            self.message += (
                f"STL file published:{self.spacing} {stl_data[:100]}"
                f"{self.spacing}Excel file path: {excel_filepath}"
            )
        except FileNotFoundError as e:
            message = f"File not found: {e}"
            self.show_error_dialog(message)
        except Exception as e:
            message = f"Failed to read and publish STL file: {e}"
            self.show_error_dialog(message)

    def publish_selection_message(
        self, wall_number, sectionnumber, picked_position, Stagelabel, cube_actor
    ):
        try:
            msg = SelectionWall()
            msg.wallselection = int(wall_number)
            msg.typeselection = f"{Stagelabel.text()}"
            msg.sectionselection = sectionnumber
            picked_position = [
                int(picked_position[0]),
                int(picked_position[1]),
                int(picked_position[2]),
            ]
            msg.picked_position = picked_position
            default_position = [
                int(cube_actor.GetPosition()[0]),
                int(cube_actor.GetPosition()[1]),
                int(cube_actor.GetPosition()[2]),
            ]
            msg.default_position = default_position
            self.selection_publisher_.publish(msg)
            self.message += (
                f"{self.spacing}Selection message published:{self.spacing}wallselections={msg.wallselection},"
                f"{self.spacing}typeselection={msg.typeselection},"
                f"{self.spacing}sectionselection={msg.sectionselection}"
                f"{self.spacing}{list(msg.picked_position)}"
            )
            self.show_info_dialog(self.message)
            self.message = ""
        except Exception as e:
            message = f"Failed to publish selection message: {e}"
            self.show_error_dialog(message)

    def run_listernernode(
        self,
        file,
        exceldata,
        wall_number,
        sectionnumber,
        picked_position,
        Stagelabel,
        cube_actor,
    ):
        if not self.listener_started:
            try:
                subprocess.Popen(
                    ["ros2", "run", "talker_listener", "listenerNode"],
                )
                self.listener_started = True
            except Exception as e:
                error_dialog = logs.LogDialog(
                    f"Failed to run ListenerNode: {str(e)}", "Error", log_type="error"
                )
                error_dialog.exec_()
        else:
            self.publish_file_message(file, exceldata)
            self.publish_selection_message(
                wall_number,
                sectionnumber,
                picked_position,
                Stagelabel,
                cube_actor,
            )

    def timer_callback(self):
        msg = String()
        msg.data = f"Hello everyone {self.count}"
        self.publisher_.publish(msg)
        self.count += 1
        self.get_logger().info(f"Publishing {msg.data}")

    def calculate_distance(self, point1, point2):
        return np.linalg.norm(point1 - point2)

    def show_info_dialog(self, message):
        if self.active_dialog:
            self.active_dialog.close()
            self.active_dialog = None
        self.active_dialog = logs.LogDialog(message, self.title, log_type="info")
        self.active_dialog.exec_()
        self.active_dialog.close()
        self.active_dialog = None

    def show_error_dialog(self, message):
        if self.active_dialog:
            self.active_dialog.close()
            self.active_dialog = None
        self.active_dialog = logs.LogDialog(message, self.title, log_type="error")
        self.active_dialog.exec_()
        self.active_dialog.close()
        self.active_dialog = None


def main(args=None):
    rclpy.init(args=args)
    talkerNode = TalkerNode()
    rclpy.spin(talkerNode)
    talkerNode.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
