from PyQt5.QtCore import pyqtSignal, QObject
import threading
import subprocess
import os
import PythonApplication.exceldatavtk as vtk_data_excel
from PyQt5.QtWidgets import QLabel

class StatusSignals(QObject):
    status_signal = pyqtSignal(str)
    page_change_signal = pyqtSignal(int)

class ListenerNodeRunner():
    def __init__(
        self,
        talker_node,
        file,
        excel_data,
        wall_number,
        markingitemsbasedonwallnumber,
        Stagetext,
        stagestorage,
        stagecurrentindex,
        Stagelabel,
        labelstatus,
        stackedWidget,
    ):
        self.talker_node = talker_node
        self.file = file
        self.excel_data = excel_data
        self.wall_number = wall_number
        self.markingitemsbasedonwallnumber = markingitemsbasedonwallnumber
        self.Stagetext = Stagetext
        self.Stagelabel = Stagelabel
        self.signals = StatusSignals()
        self.listener_started = False
        self.spacing = "\n"
        self.stagestorage = stagestorage
        self.stackedWidget = stackedWidget
        self.stagecurrentindex = stagecurrentindex
        self.labelstatus = labelstatus
        self.signals.status_signal.connect(self.update_status)
        self.signals.page_change_signal.connect(self.change_page)
        
    def change_page(self, page_index):
        self.stackedWidget.setCurrentIndex(page_index)

    def checkerpager(self):
        if self.stackedWidget.currentIndex() == 3 and self.listener_started:
            self.signals.page_change_signal.emit(4)

    def run_listener_node(self):
        if not self.listener_started:
            try:
                threading.Thread(target=self._run_process, daemon=True).start()
                self.signals.status_signal.emit("Status: Running")
                self.listener_started = True
                self.checkerpager()
            except Exception as e:
                self.signals.status_signal.emit(f"Status: Error - {str(e)}")
        else:
            for data in self.markingitemsbasedonwallnumber:
                picked_position = [
                    int(data["Position X (m)"]),
                    int(data["Position Y (m)"]),
                    int(data["Position Z (m)"]),
                ]
                self.talker_node.publish_file_message(self.file, self.excel_data)
                self.talker_node.publish_selection_message(
                    self.wall_number, picked_position, self.Stagetext
                )
            self.talker_node.showdialog()

    def checker(self):
        self.wall_identifiers, self.walls, self.excelfiletext = vtk_data_excel.exceldataextractor()
        stage_data = self.wall_identifiers[self.Stagetext]
        items = stage_data.get("markingidentifiers", [])
        walls = stage_data.get("wall_numbers", [])
        positionx = stage_data.get("Position X (m)", [])
        positiony = stage_data.get("Position Y (m)", [])
        positionz = stage_data.get("Position Z (m)", [])
        shapetype = stage_data.get("Shape type", [])
        status = stage_data.get("Status", [])
        transformed = {}
        filtered_wall = {}
        
        for wall, item, x, y, z, shape, statu in zip(
            walls, items, positionx, positiony, positionz, shapetype, status
        ):
            if wall not in transformed and statu != "done" and wall == self.wall_number:
                transformed[wall] = [{
                    "markingidentifier": item,
                    "Wall Number": wall,
                    "Position X (m)": x,
                    "Position Y (m)": y,
                    "Position Z (m)": z,
                    "Shape type": shape,
                }]
            elif wall not in transformed and statu != "done":
                filtered_wall[wall] = [{
                    "markingidentifier": item,
                    "Wall Number": wall,
                    "Position X (m)": x,
                    "Position Y (m)": y,
                    "Position Z (m)": z,
                    "Shape type": shape,
                }]
        
        if transformed:
            self.signals.status_signal.emit("Error, please move the machine.")
        else:
            if filtered_wall:
                self.signals.status_signal.emit("Marked items in the wall are completed, please click another wall.")
            else:
                message = f"All the items in {self.Stagelabel} are completed.{self.spacing}"
                if self.stagecurrentindex < len(self.stagestorage) - 1:
                    self.stagecurrentindex += 1
                    self.Stagetext = self.stagestorage[self.stagecurrentindex]
                    message += f"Moving on to {self.Stagetext}"
                    self.Stagelabel.setText(f"Stage: {self.Stagetext}")
                else:
                    self.signals.status_signal.emit("All the items that are marked are completed. Please close the program.")

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

    def process_finished(self):
        self.signals.status_signal.emit("Status: Completed")
        self.listener_started = True

    def update_status(self, status):
        self.labelstatus.setText(status)
