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

    def run_execution(self, rows, excel_path):
        self.talker_node.publish_file_message(self.file, excel_path)
        for data in rows:
            wn = data.get("Wall Number")
            x = data.get("Position X", 0)
            y = data.get("Position Y", 0)
            z = data.get("Position Z", 0)
            markingtype = data.get("Marking Type")
            def _num(v, default=0):
                try:
                    return float(v)
                except Exception:
                    return default
            picked_position = [int(round(_num(x))),
                               int(round(_num(y))),
                               int(round(_num(z)))]
            self.talker_node.publish_selection_message(wn, picked_position, markingtype)

    def _run_process(self):
        env = os.environ.copy()
        env["ROS_MASTER_URI"] = "http://localhost:11311"
        env["ROS_IP"] = "172.17.0.1"
        env["ROS_HOSTNAME"] = "localhost"
        command = "source /opt/ros/noetic/setup.bash && source /root/catkin_ws/src/newui_Greyform/devel/setup.bash && rosrun talker_listener listener_node.py"
        try:
            process = subprocess.Popen(
                ["bash", "-c", command],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.signals.page_change_signal.emit(4)  
            stdout, stderr = process.communicate()
            if process.returncode == 0:
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
