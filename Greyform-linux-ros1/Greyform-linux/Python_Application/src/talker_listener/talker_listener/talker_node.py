import rospy
import sys
from my_robot_wallinterfaces.msg import (
    FileExtractionMessage,
    SelectionWall,
)
from my_robot_wallinterfaces.srv import SetLed
import PythonApplication.exceldatavtk as exceldata
from std_msgs.msg import String
import subprocess
import pandas as pd
import numpy as np
import sys
from PyQt5.QtCore import pyqtSignal, QObject
import threading
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
sys.path.append("/root/catkin_ws/src/Greyform-linux/Python_Application")
import PythonApplication.dialoglogger as logs

class StatusSignals(QObject):
    status_signal = pyqtSignal(str)


class ListenerNodeRunner(QMainWindow):
    def __init__(
        self, wall_number, sectionnumber, picked_position, Stagelabel, cube_actor
    ):
        super().__init__()
        self.initUI()
        self.wall_number = wall_number
        self.sectionnumber = sectionnumber
        self.picked_position = picked_position
        self.Stagelabel = Stagelabel
        self.cube_actor = cube_actor
        self.signals = StatusSignals()
        self.signals.status_signal.connect(self.update_status)

    def initUI(self):
        self.status_label = QLabel("Status: Not Running", self)
        self.run_button = QPushButton("Run Listener Node", self)
        self.run_button.clicked.connect(self.run_listener_node)
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.run_button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.setWindowTitle("Listener Node Status")
        self.setGeometry(300, 300, 300, 200)

    def run_listener_node(self):
        try:
            threading.Thread(target=self._run_subprocess, daemon=True).start()
            self.signals.status_signal.emit("Status: Running")
        except Exception as e:
            self.signals.status_signal.emit(f"Status: Error - {str(e)}")

    def _run_subprocess(self):
        try:
            command = "rosrun talker_listener listener_node.py"
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable="/bin/bash")
            while True:
                output = process.stdout.readline()
                if process.poll() is not None:
                    break
                if output:
                    self.signals.status_signal.emit(f"Output: {output.decode('utf-8').strip()}")
            stderr = process.stderr.read()
            if stderr:
                self.signals.status_signal.emit(f"Status: Error - {stderr.decode('utf-8')}")
            else:
                self.signals.status_signal.emit("Status: Completed")
            TalkerNode.publish_selection_message(
                self.wall_number,
                self.sectionnumber,
                self.picked_position,
                self.Stagelabel,
                self.cube_actor,
            )
        except Exception as e:
            self.signals.status_signal.emit(f"Status: Error - {str(e)}")

    def update_status(self, status):
        # Update the status label
        self.status_label.setText(status)

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
        self.rate = rospy.Rate(10)
        self.active_dialog = None
        self.listener_started = False

    def publish_file_message(self, file_path, excel_filepath):
        try:
            with open(file_path, "rb") as f:
                stl_data = f.read()
            msg = FileExtractionMessage()
            msg.stl_data = list(stl_data)
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

    def calculate_distance(self, point1, point2):
        return np.linalg.norm(point1 - point2)
    
    def run_ros(
        self, wall_number, sectionnumber, picked_position, Stagelabel, cube_actor
    ):
        self.listenerdialog = ListenerNodeRunner(
            wall_number, sectionnumber, picked_position, Stagelabel, cube_actor
        )
        self.listenerdialog.show()

    def publish_selection_message(
        self, wall_number, sectionnumber, picked_position, seqlabel, cube_actor
    ):
        try:
            msg = SelectionWall()
            msg.wallselection = int(wall_number)
            msg.typeselection = f"{seqlabel.text()}"
            msg.sectionselection = sectionnumber
            picked_position = [
                int(picked_position[0]),
                int(picked_position[1]),
                int(picked_position[2]),
            ]
            msg.picked_position = picked_position
            default_position= [
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
                f"{self.spacing}{list(msg.default_position)}"
            )
            self.show_info_dialog(self.message)
            self.message = ""
            self.run_listernernode()
        except Exception as e:
            message = f"Failed to publish selection message: {e}"
            self.show_error_dialog(message)

    def timer_callback(self, event):
        msg = String()
        msg.data = f"Hello everyone {self.count}"
        self.publisher_.publish(msg)
        self.count += 1
        rospy.loginfo(f"Publishing {msg.data}")

    def run_listernernode(self):
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
