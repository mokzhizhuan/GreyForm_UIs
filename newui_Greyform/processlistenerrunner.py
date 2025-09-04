from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtCore import Qt ,  QObject ,pyqtSignal
import threading
import subprocess
import os
import json


class StatusSignals(QObject):
    status_signal = pyqtSignal(str)
    page_change_signal = pyqtSignal(int)


class ListenerNodeRunner:
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
        self.status_icon = QLabel(labelstatus.parent())
        self.status_icon.setFixedSize(20, 20)
        self.status_icon.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self._movie = None 
        lay = self.labelstatus.parent().layout()
        if lay is not None:
            idx = lay.indexOf(self.labelstatus)
            if idx >= 0:
                lay.insertWidget(idx, self.status_icon)
            else:
                lay.addWidget(self.status_icon)
        self.signals.status_signal.connect(self.update_status)
        try:
            self.signals.status_signal.disconnect()   # disconnect ALL existing slots
        except TypeError:
            pass                                      # no existing connections
        self.signals.status_signal.connect(self.on_status)
        self.signals.page_change_signal.connect(self.change_page)

    def run_listener_node(self):
        if not self.listener_started:
            try:
                threading.Thread(target=self._run_process, daemon=True).start()
                self.signals.status_signal.emit("Status: Running")
                self.listener_started = True
                self.process = None
            except Exception as e:
                self.signals.status_signal.emit(f"Status: Error - {str(e)}")
        else:
            self.stop_listener_node()
            try:
                threading.Thread(target=self._run_process, daemon=True).start()
                self.signals.status_signal.emit("Status: Running")
                self.listener_started = True
                self.process = None
            except Exception as e:
                self.signals.status_signal.emit(f"Status: Error - {str(e)}")

    def stop_listener_node(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                self.signals.status_signal.emit(
                    "Please wait, robot is calculating its position"
                )
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.signals.status_signal.emit(
                    "Please wait, robot is calculating its position"
                )
        self.process = None

    def run_execution(self, rows, excel_data):
        if not self.listener_started:
            return
        self.talker_node.publish_file_message(self.file, excel_data)
        for data in rows:
            wn = data.get("Wall Number")
            x = data.get("LX", data.get("Position X"))
            y = data.get("LY", data.get("Position Y"))
            z = data.get("LZ", data.get("Position Z"))
            markingtype = data.get("Marking Type", data.get("Shape Type"))
            picked_position = [int(x), int(y), int(z)]
            self.talker_node.publish_selection_message(wn, picked_position, markingtype)
        self.talker_node.showdialog()

    def _run_process(self):
        env = os.environ.copy()
        command = (
            "source /opt/ros/humble/setup.bash && "
            "source /home/ubuntu/ros2_ws/src/Greyform-linux/Python_Application/install/setup.bash && "
            "ros2 run talker_listener listener_node"
        )
        try:
            self.process = subprocess.Popen(
                ["bash", "-c", command],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.signals.page_change_signal.emit(4)
            stdout, stderr = self.process.communicate()
            if self.process.returncode == 0:
                self.signals.status_signal.emit("Node started successfully.")
                self.signals.status_signal.emit(stdout.decode("utf-8"))
            else:
                self.signals.status_signal.emit("Failed to start node.")
                self.signals.status_signal.emit(stderr.decode("utf-8"))
            self.process_finished()
        except Exception as e:
            self.signals.status_signal.emit(f"Process failed: {str(e)}")

    def on_status(self, msg: str):
        # Parse JSON if provided; else treat as plain text
        try:
            data = json.loads(msg)
            text = data.get("text", msg)
            icon = data.get("icon")
            gif  = data.get("gif")
        except Exception:
            text, icon, gif = msg, None, None

        self.labelstatus.setText(text)

        # update small icon label next to text (create once in __init__)
        if getattr(self, "_movie", None):
            self._movie.stop(); self._movie = None
        self.status_icon.clear()

        if gif:
            self._movie = QMovie(gif)
            self._movie.setScaledSize(self.status_icon.size())
            self.status_icon.setMovie(self._movie)
            self._movie.start()
        elif icon:
            pm = QPixmap(icon)
            if not pm.isNull():
                pm = pm.scaled(self.status_icon.width(), self.status_icon.height(),
                            Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.status_icon.setPixmap(pm)

    def send_status(self, text, icon=None, gif=None):
        # This method should NEVER be connected to status_signal
        if icon or gif:
            payload = {"text": text}
            if icon: payload["icon"] = icon
            if gif:  payload["gif"]  = gif
            self.signals.status_signal.emit(json.dumps(payload))
        else:
            self.signals.status_signal.emit(text)

    def process_finished(self):
        self.send_status("Marking is completed. Please move the robot to the next position.", icon="check.png")
        self.listener_started = True

    def update_status(self, text: str):
        self.send_status(text)
                         
    def change_page(self, index):
        self.stackedWidget.setCurrentIndex(index)
