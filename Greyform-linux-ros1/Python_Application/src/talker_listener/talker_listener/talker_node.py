import rospy

import sys
from my_robot_wallinterfaces.msg import (
    FileExtractionMessage,
    SelectionWall,
)
from my_robot_wallinterfaces.srv import SetLed
import PythonApplication.exceldatavtk as exceldata
from std_msgs.msg import String
import pandas as pd
import numpy as np
import sys
sys.path.append("/root/catkin_ws/src/Greyform-linux/Python_Application")
import PythonApplication.dialoglogger as logs

class TalkerNode:
    def __init__(self):
        self.file_publisher_ = rospy.Publisher(
            "file_extraction_topic", FileExtractionMessage, queue_size=10
        )
        self.selection_publisher_ = rospy.Publisher(
            "selection_wall_topic", SelectionWall, queue_size=10
        )
        self.message = ""
        self.spacing = "\n"
        self.title = "Publisher Node"
        self.rate = rospy.Rate(10)  # 10 Hz

    def publish_file_message(self, file_path, excel_filepath):
        try:
            with open(file_path, "rb") as f:
                stl_data = f.read()
            msg = FileExtractionMessage()
            msg.stl_data = list(stl_data)  # Convert bytes to a list of uint8
            msg.excelfile = excel_filepath
            self.file_publisher_.publish(msg)
            self.message += f"STL file published:{self.spacing} {stl_data[:100]}"
            self.message += f"{self.spacing}Excel file path: {excel_filepath}"
        except FileNotFoundError as e:
            message = f"File not found: {e}"
            self.show_error_dialog(message)
        except Exception as e:
            message = f"Failed to read and publish STL file: {e}"
            self.show_error_dialog(message)


    def calculate_distance(self, point1, point2):
        return np.linalg.norm(point1 - point2)

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
            self.message += f"{self.spacing}Selection message published:{self.spacing}wallselections={msg.wallselection},"
            self.message += f"{self.spacing}typeselection={msg.typeselection},"
            self.message += f"{self.spacing}sectionselection={msg.sectionselection}"
            self.message += f"{self.spacing}{list(msg.picked_position)}"
            self.show_info_dialog(self.message)
            self.message=""
        except Exception as e:
            message = f"Failed to publish selection message: {e}"
            self.show_error_dialog(message)


    def timer_callback(self, event):
        msg = String()
        msg.data = f"Hello everyone {self.count}"
        self.publisher_.publish(msg)
        self.count += 1
        rospy.loginfo(f"Publishing {msg.data}")

    def show_info_dialog(self, message):
        dialog = logs.LogDialog(message, self.title ,log_type="info")
        dialog.exec_()

    def show_error_dialog(self, message):
        dialog = logs.LogDialog(message, self.title, log_type="error")
        dialog.exec_()



def main(args=None):
    rospy.init(args=args)
    rospy.init_node("node_name", anonymous=True)
    talkerNode = TalkerNode()
    rospy.spin(talkerNode)
    talkerNode.destroy_node()
    rospy.shutdown()


if __name__ == "__main__":
    main()
