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
import PythonApplication.exceldatavtk as vtk_data_excel
import tkinter as tk
from tkinter import ttk

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
        Stagetext,
        cube_actor,
        dialog,
        stagestorage, 
        stagecurrentindex,
        Stagelabel,
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
        self.Stagetext = Stagetext
        self.Stagelabel = Stagelabel
        self.cube_actor = cube_actor
        self.dialog = dialog
        self.signals = StatusSignals()
        self.listener_started = False
        self.spacing = "/n"
        self.stagestorage = stagestorage
        self.stagecurrentindex = stagecurrentindex
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
                threading.Thread(target=self._run_process, daemon=True).start()
                self.signals.status_signal.emit("Status: Running")
                self.listener_started = True
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
                    self.wall_number,
                    self.sectionnumber,
                    picked_position,
                    self.Stagetext,
                )
            self.talker_node.showdialog()
        
    
    def checker(self):
        self.wall_identifiers , self.walls , self.excelfiletext = vtk_data_excel.exceldataextractor()
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
        for wall, item, x, y, z, shape , statu in zip(
            walls, items, positionx, positiony, positionz, shapetype , status
        ):
            if wall not in transformed and statu != "done" and wall == self.wall_number:
                transformed[wall] = []
                transformed[wall].append(
                    {
                        "markingidentifier": item,
                        "Wall Number": wall,
                        "Position X (m)": x,
                        "Position Y (m)": y,
                        "Position Z (m)": z,
                        "Shape type": shape,
                    }
                )
            elif wall not in transformed and statu != "done":
                filtered_wall[wall] = []
                filtered_wall[wall].append(
                    {
                        "markingidentifier": item,
                        "Wall Number": wall,
                        "Position X (m)": x,
                        "Position Y (m)": y,
                        "Position Z (m)": z,
                        "Shape type": shape,
                    }
                )
        if transformed:
            self.show_error_message(f"Error, please move the machine.")
        else:
            if filtered_wall:
                self.show_message(f"Marked items in the wall are completed, please click another wall")
            else:
                message = (
                    f"All the items in {self.Stagelabel} are completed.{self.spacing}"
                )
                if self.stagecurrentindex < len(self.stagestorage) - 1:
                    self.stagecurrentindex += 1
                    self.Stagetext = self.stagestorage[self.stagecurrentindex]
                    message += (
                        f"Moving on to {self.Stagetext}"
                    )
                    self.Stagelabel.setText(f"Stage : {self.Stagetext}")
                else:
                    self.show_message(f"All the items that are marked are completed. Please close the program.")
            


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
            "Status: Completed"
        )
        self.listener_started = True
        self.checker()

    def update_status(self, status):
        self.status_label.setText(status)

    def show_message(self, message):
        root = tk.Tk()
        root.title("Message")
        root.geometry("500x300") 
        frame = ttk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget = tk.Text(frame, wrap=tk.WORD, state=tk.DISABLED)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        text_widget.config(state=tk.NORMAL) 
        text_widget.insert(tk.END, message)
        text_widget.config(state=tk.DISABLED)  
        close_button = ttk.Button(root, text="Close", command=root.destroy)
        close_button.pack(pady=10)
        root.mainloop()

    # include error message
    def show_error_message(self, message):
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror("Error", message)
        root.destroy()
