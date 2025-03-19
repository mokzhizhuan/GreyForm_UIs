from PyQt5.QtCore import pyqtSignal, QObject, QMetaObject , Qt , Q_ARG , QTimer
from PyQt5.QtWidgets import QStackedWidget
import threading
import subprocess
import os

class StatusSignals(QObject):
    status_signal = pyqtSignal(str)
    page_change_signal = pyqtSignal(int)

class ListenerNodeRunner():
    def __init__(
        self,
        talker_node,
        file,
        labelstatus,
        stackedWidget,
    ):
        self.talker_node = talker_node
        self.file = file
        self.labelstatus = labelstatus
        self.signals = StatusSignals()
        self.listener_started = False
        self.spacing = "\n"
        self.stackedWidget = stackedWidget
        self.signals.status_signal.connect(self.update_status)
        self.signals.page_change_signal.connect(self.change_page)

    def run_listener_node(self):
        if not self.listener_started:
            try:
                threading.Thread(target=self._run_process, daemon=True).start()
                self.signals.status_signal.emit("Status: Running")
                self.listener_started = True
            except Exception as e:
                self.signals.status_signal.emit(f"Status: Error - {str(e)}")

    def run_execution(self , markingitemsbasedonwallnumber , wall_number, Stagetext, excel_data):
        if self.listener_started:
            for data in markingitemsbasedonwallnumber:
                picked_position = [
                    int(data["Position X (mm)"]),
                    int(data["Position Y (mm)"]),
                    int(data["Position Z (mm)"]),
                ]
                self.talker_node.publish_file_message(self.file, excel_data)
                self.talker_node.publish_selection_message(
                    wall_number, picked_position, Stagetext
                )
            self.talker_node.showdialog()

    def _run_process(self):
        env = os.environ.copy()
        env["ROS_MASTER_URI"] = "http://localhost:11311"
        env["ROS_IP"] = "172.17.0.3"
        env["ROS_HOSTNAME"] = "localhost"
        command = "source /opt/ros/noetic/setup.bash && source /root/catkin_ws/src/Python_Application/devel/setup.bash && rosrun talker_listener listener_node.py"
        try:
            process = subprocess.Popen(
                ["bash", "-c", command],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.signals.page_change_signal.emit(4)  
            stdout, stderr = process.communicate()
            # Debugging: Print output
            if process.returncode == 0:
                self.signals.status_signal.emit("Node started successfully.")
                self.signals.status_signal.emit(stdout.decode("utf-8"))
            else:
                self.signals.status_signal.emit("Failed to start node.")
                self.signals.status_signal.emit(stderr.decode("utf-8"))
            self.process_finished()
        except Exception as e:
            self.signals.status_signal.emit(f"Process failed: {str(e)}")

    def process_finished(self):
        self.signals.status_signal.emit("Status: Completed")
        self.listener_started = True

    def update_status(self, status):
        self.labelstatus.setText(status)

    def change_page(self, index):
        self.stackedWidget.setCurrentIndex(index)