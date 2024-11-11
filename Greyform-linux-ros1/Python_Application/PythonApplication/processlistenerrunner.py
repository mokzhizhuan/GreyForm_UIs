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
import subprocess
import os


class StatusSignals(QObject):
    status_signal = pyqtSignal(str)


# Run Listener Node dialog
class ListenerNodeRunner(QMainWindow):
    def __init__(
        self,
        talker_node,
        file,
        excel_data,
        wall_number,
        sectionnumber,
        markingitemsbasedonwallnumber,
        Stagelabel,
        cube_actor,
        dataseqtext,
        maxlen,
        counter,
        markingreq,
        dialog,
    ):
        # starting initialize
        super().__init__()
        self.initUI()
        self.talker_node = talker_node
        self.file = file
        self.excel_data = excel_data
        self.wall_number = wall_number
        self.sectionnumber = sectionnumber
        self.markingitemsbasedonwallnumber = markingitemsbasedonwallnumber
        self.Stagelabel = Stagelabel
        self.cube_actor = cube_actor
        self.dataseqtext = dataseqtext
        self.maxlen = maxlen
        self.markingreq = markingreq
        self.counter = counter
        self.dialog = dialog
        self.signals = StatusSignals()
        self.listener_started = False
        self.spacing = "/n"
        self.signals.status_signal.connect(self.update_status)

    # listener runner process ui
    def initUI(self):
        self.status_label = QLabel("Status: Not Running", self)
        self.status_label.setStyleSheet(
            """
            QLabel {
                font-size: 20px;                
            }
            """
        )
        self.run_button = QPushButton("Run Listener Node", self)
        self.run_button.setStyleSheet(
            """
            QPushButton {
                font-size: 20px;           
                min-height: 100px;   
                icon-size: 100px 100px;        
            }
            """
        )
        self.run_button.clicked.connect(self.run_listener_node)
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.run_button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.setWindowTitle("Listener Node Status")
        self.setGeometry(400, 400, 500, 500)

    # interacting running process
    def run_listener_node(self):
        if self.listener_started is not True:
            try:
                threading.Thread(target=self._run_process, daemon=True).start()
                self.signals.status_signal.emit("Status: Running")
                self.listener_started = True
            except Exception as e:
                self.signals.status_signal.emit(f"Status: Error - {str(e)}")
        else:
            for positions, data in self.markingitemsbasedonwallnumber.items():
                for i, (posX, posY, posZ) in enumerate(
                    zip(data["posX"], data["posY"], data["posZ"])
                ):
                    picked_position = [
                        int(data["posX"][i]),
                        int(data["posY"][i]),
                        int(data["posZ"][i]),
                    ]
                    self.talker_node.publish_file_message(self.file, self.excel_data)
                    self.talker_node.publish_selection_message(
                        self.wall_number,
                        self.sectionnumber,
                        picked_position,
                        self.Stagelabel,
                        self.cube_actor,
                    )
            self.talker_node.showdialog()

    # ros running process
    def _run_process(self):
        env = os.environ.copy()
        env["ROS_MASTER_URI"] = "http://localhost:11311"
        env["ROS_IP"] = "172.17.0.3"
        env["ROS_HOSTNAME"] = "localhost"
        command = "source /opt/ros/noetic/setup.bash && source /root/catkin_ws/src/Python_Application/devel/setup.bash && rosrun talker_listener listener_node.py"
        process = subprocess.Popen(
            ["bash", "-c", command],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            self.signals.status_signal.emit("Node started successfully.")
            self.signals.status_signal.emit(stdout.decode("utf-8"))
        else:
            self.signals.status_signal.emit("Failed to start node.")
            self.signals.status_signal.emit(stderr.decode("utf-8"))
        self.process_finished()

    # process completed
    def process_finished(self):
        self.signals.status_signal.emit(
            "Status: Completed , Please include another sequence , Stage and wall number"
        )
        self.listener_started = True

    def update_status(self, status):
        self.status_label.setText(status)
