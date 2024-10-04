#!/usr/bin/env python3
import rospy
import sys
from my_robot_wallinterfaces.msg import FileExtractionMessage, SelectionWall
from my_robot_wallinterfaces.srv import SetLed
from std_msgs.msg import String
import subprocess
import sys
import PythonApplication.dialoglogger as logs

class TalkerNode:
    def __init__(self):
        self.file_publisher_ = rospy.Publisher(
            "file_extraction_topic",
            FileExtractionMessage,
            queue_size=10,
        )
        self.selection_publisher_ = rospy.Publisher(
            "selection_wall_topic",
            SelectionWall,
            queue_size=10,
        )
        self.message = ""
        self.spacing = "\n"
        self.title = "Publisher Node"
        self.rate = rospy.Rate(10)
        self.active_dialog = None
        self.listener_started = False

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
                    ["rosrun", "talker_listener", "listener_node.py"],
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
            self.errormessage += f"File is not found: {e}"
        except Exception as e:
            self.errormessage += f"Failed to read and publish STL file: {e}"

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
        except Exception as e:
            self.errormessage += f"{self.spacing}Failed to publish selection message: {e}"
            

    def showdialog(self):
        if self.message != "":
            self.show_info_dialog(self.message)
            self.message = ""
        else:
            self.show_error_dialog(self.errormessage)
            self.errormessage= ""

    def timer_callback(self, event):
        msg = String()
        msg.data = f"Hello everyone {self.count}"
        self.publisher_.publish(msg)
        self.count += 1
        rospy.loginfo(f"Publishing {msg.data}")

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
    rospy.init(args=args)
    rospy.init_node("node_name", anonymous=True)
    talkerNode = TalkerNode()
    rospy.spin(talkerNode)
    talkerNode.destroy_node()
    rospy.shutdown()


if __name__ == "__main__":
    main()
