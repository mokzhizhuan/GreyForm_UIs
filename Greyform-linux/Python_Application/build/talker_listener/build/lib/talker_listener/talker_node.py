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
import PythonApplication.dialoglogger as logs
from pathlib import Path

# talker node
class TalkerNode(Node):
    def __init__(self):
        # starting initialize
        super().__init__("talker_node")
        self.file_publisher_ = self.create_publisher(
            FileExtractionMessage, "file_extraction_topic", 10
        )
        self.selection_publisher_ = self.create_publisher(
            SelectionWall, "selection_wall_topic", 10
        )
        self.message = ""
        self.errormessage = ""
        self.spacing = "\n"
        self.title = "Publisher Node"
        self.active_dialog = None

    # show dialog
    def showdialog(self):
        if self.message != "":
            self.show_info_dialog(self.message)
            self.message = ""
        else:
            self.show_error_dialog(self.errormessage)
            self.errormessage = ""

    #talker file message implementation
    def publish_file_message(self, file_path, excel_filepath):
        try:
            if isinstance(file_path, Path):
                file_path = str(file_path)
            with open(file_path, "rb") as f:
                stl_data = f.read()
            msg = FileExtractionMessage()
            msg.stl_data = list(stl_data)  
            if isinstance(excel_filepath, Path):
                excel_filepath = str(excel_filepath)
            msg.excelfile = excel_filepath
            self.file_publisher_.publish(msg)
        except Exception as e:
            print(f"Error: {e}")
            self.errormessage += (
                f"{self.spacing}Failed to publish file message: {e}"
            )

    #talker selection message implementation
    def publish_selection_message(
        self, wall_number, picked_position, Stagelabel, next_wall_number
    ):  
        try:
            msg = SelectionWall()
            msg.wallselection = str(wall_number)
            msg.typeselection = f"{str(Stagelabel)}"
            msg.picked_position = list(picked_position) 
            self.selection_publisher_.publish(msg)
            if next_wall_number is not None:
                self.message = f"The process has finished successfully! Please move in to Wall: {next_wall_number}"
            else:
                self.message = ""
        except Exception as e:
            self.errormessage += (
                f"{self.spacing}Failed to publish selection message: {e}"
            )
            

    #test callback
    def timer_callback(self, event):
        msg = String()
        msg.data = f"Hello everyone {self.count}"
        self.publisher_.publish(msg)
        self.count += 1
        rclpy.loginfo(f"Publishing {msg.data}")

    def show_info_dialog(self, message):
        if self.active_dialog:
            self.active_dialog.close()
            self.active_dialog = None
        self.active_dialog = logs.LogDialog(message, self.title, log_type="info")
        self.active_dialog.exec_()
        self.active_dialog.close()
        self.active_dialog = None

    # error dialog implementation
    def show_error_dialog(self, message):
        if self.active_dialog:
            self.active_dialog.close()
            self.active_dialog = None
        self.active_dialog = logs.LogDialog(message, self.title, log_type="error")
        self.active_dialog.exec_()
        self.active_dialog.close()
        self.active_dialog = None


    # run normally with no dialog
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



# main runner for listener node
def main(args=None):
    rclpy.init(args=args)
    talkerNode = TalkerNode()
    rclpy.spin(talkerNode)
    talkerNode.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
