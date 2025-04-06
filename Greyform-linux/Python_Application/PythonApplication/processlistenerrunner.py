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

    def run_execution(self , markingitemsbasedonwallnumber , wall_number, Stagetext, excel_data, next_wall_number):
        print(excel_data)
        print(markingitemsbasedonwallnumber)
        print(wall_number)
        print(Stagetext)
        if self.listener_started:
            for data in markingitemsbasedonwallnumber:
                picked_position = [
                    int(data["Position X (mm)"]),
                    int(data["Position Y (mm)"]),
                    int(data["Position Z (mm)"]),
                ]
                self.talker_node.publish_file_message(self.file, excel_data)
                self.talker_node.publish_selection_message(
                    wall_number, picked_position, Stagetext , next_wall_number
                )
            self.talker_node.showdialog()

    def _run_process(self):
        env = os.environ.copy()
        env["ROS_MASTER_URI"] = "http://localhost:11311"
        env["ROS_IP"] = "172.17.0.3"
        env["ROS_HOSTNAME"] = "localhost"
        command = "source /opt/ros/humble/setup.bash && source /home/ubuntu/ros2_ws/src/Greyform-linux/Python_Application/install/setup.bash && ros2 run talker_listener listener_node"
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
                print("Node started successfully.")
                self.signals.status_signal.emit("Node started successfully.")
                self.signals.status_signal.emit(stdout.decode("utf-8"))
            else:
                print("Failed to start node.")
                self.signals.status_signal.emit("Failed to start node.")
                self.signals.status_signal.emit(stderr.decode("utf-8"))
            self.process_finished()
        except Exception as e:
            print(f"Process failed: {str(e)}")
            self.signals.status_signal.emit(f"Process failed: {str(e)}")

    def process_finished(self):
        print("Process finished.")
        self.signals.status_signal.emit("Status: Completed")
        self.listener_started = True

    def update_status(self, status):
        self.labelstatus.setText(status)

    def change_page(self, index):
        self.stackedWidget.setCurrentIndex(index)