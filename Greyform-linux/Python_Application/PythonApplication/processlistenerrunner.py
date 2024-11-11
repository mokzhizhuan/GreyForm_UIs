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
        self.close_button = QPushButton("Close", self)
        self.close_button.setStyleSheet(
            """
            QPushButton {
                font-size: 20px;           
                min-height: 100px;   
                icon-size: 100px 100px;        
            }
            """
        )
        self.close_button.clicked.connect(self.close)
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.run_button)
        layout.addWidget(self.close_button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.setWindowTitle("Listener Node Status")
        self.setGeometry(400, 400, 500, 500)

    # interacting running process
    def run_listener_node(self):
        if self.listener_started is not True:
            try:
                threading.Thread(target=self._run_subprocess, daemon=True).start()
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
    def _run_subprocess(self):
        try:
            process = subprocess.Popen(
                ["ros2", "run", "talker_listener", "listenerNode"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            while True:
                output = process.stdout.readline()
                if process.poll() is not None:
                    break
                if output:
                    self.signals.status_signal.emit(
                        f"Output: {output.decode('utf-8').strip()}"
                    )
            stderr = process.stderr.read()
            if stderr:
                self.signals.status_signal.emit(
                    f"Status: Error - {stderr.decode('utf-8')}"
                )
            else:
                self.signals.status_signal.emit(
                    "Status: the marking items are completed, Please include another sequence , Stage and wall number"
                )
        except Exception as e:
            self.signals.status_signal.emit(f"Status: Error - {str(e)}")

    def update_status(self, status):
        self.status_label.setText(status)

