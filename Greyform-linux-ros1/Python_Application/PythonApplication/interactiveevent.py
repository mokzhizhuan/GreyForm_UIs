from PyQt5.QtCore import *
from vtk import *
import tkinter as tk
from tkinter import messagebox
import time , re
from PyQt5.QtWidgets import QProgressDialog, QApplication, QDialog, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer , Qt

# import rospy
# from sensor_msgs.msg import LaserScan
# this scan import is for scanning the robot , I will implement it tomorrow .
# It is not avaiable to implement for now, Dont uncomment it first
# rospy.init_node('scan_values')
# sub = rospy.Subscriber('/kobuki/laser/scan', LaserScan, callback)
# rospy.spin()

# insert interactive event for the stl mesh , left click is for moving the stl ,
# right click is to insert the actor in the room view , right click for room interact shower and toilet
# l key is to remove the actor in the room view and set the mesh to the original position
class myInteractorStyle(vtkInteractorStyleTrackballCamera):
    def __init__(
        self, setcamerainteraction, wall_identifiers, parent=None
    ):
        # starting initialize
        super().__init__()
        self.render = setcamerainteraction[0]
        self.renderwindowinteractor = setcamerainteraction[1]
        self.meshbound = setcamerainteraction[2]
        self.mesh = setcamerainteraction[6]
        self.polys = setcamerainteraction[7]
        self.reader = setcamerainteraction[8]
        self.walls = setcamerainteraction[13]
        self.wall_actors = setcamerainteraction[14]
        self.wallname = setcamerainteraction[15] 
        self.identifier = setcamerainteraction[16]
        self.stacked_widget = setcamerainteraction[17]
        match = re.search(r'\d+', self.wallname)
        wall_number = int(match.group())
        self.scan = self.identifier[wall_number]
        self.wall_index = list(self.walls.keys()).index(self.wallname) if self.wallname in self.walls else None
        camera = self.render.GetActiveCamera()
        self._translate = QCoreApplication.translate
        self.parent = parent
        self.totalsteps = 100  # Define total steps
        self.scanning = self.AddObserver(
            "RightButtonPressEvent", self.wallscanning
        )
    
    def wallscanning(self, obj, event):
        self.progress_dialog = QProgressDialog("Scanning...", "Cancel", 0, self.totalsteps, self.parent)
        self.progress_dialog.setWindowTitle("Progress")
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.setAutoReset(True)
        self.progress_dialog.show()

        self.current_step = 0
        self.run_scan_step()  # Start the progress loop

    def run_scan_step(self):
        if self.current_step >= self.totalsteps:
            self.progress_dialog.setValue(self.totalsteps)
            QTimer.singleShot(500, self.programexecute)  # Delay execution slightly
            return
        self.current_step += 1
        self.progress_dialog.setValue(self.current_step)

        if self.progress_dialog.wasCanceled():
            return  # Stop execution if canceled

        QTimer.singleShot(50, self.run_scan_step)  # Recursive update every 50ms

    def programexecute(self):
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("Execution Complete")
        dialog.setFixedSize(400, 200)
        layout = QVBoxLayout()
        label = QLabel("The process has finished successfully!")
        label.setStyleSheet("font-size: 18px;")
        ok_button = QPushButton("OK")
        ok_button.setStyleSheet(
            """
            QPushButton {
                font-size: 20px;           
                min-height: 50px;   
                min-width: 150px;  
                icon-size: 50px 50px;        
            }
            """
        )
        ok_button.clicked.connect(dialog.accept)  # Close dialog when clicked
        ok_button.clicked.connect(self.changewall)  # Close dialog when clicked
        layout.addWidget(label)
        layout.addWidget(ok_button)
        layout.setAlignment(ok_button, Qt.AlignCenter)  
        dialog.setLayout(layout)
        dialog.exec_()  # Show the dialog

    def changewall(self):
        self.wall_actors[self.wallname].VisibilityOff() 
        self.wall_index = self.wall_index + 1
        wall_keys = list(self.walls.keys())
        if self.wall_index < len(wall_keys):  # Check if walls remain
            self.wallname = wall_keys[self.wall_index]
            self.wall_actors[self.wallname].VisibilityOn()
            match = re.search(r'\d+', self.wallname)
            wall_number = int(match.group())
            self.scan = self.identifier[wall_number]
            print(self.scan)
        else:
            self.stacked_widget.setCurrentIndex(4)

    def set_progress_bar(self, progress_bar):
        """Attach a QProgressBar from the main UI."""
        self.progress_bar = progress_bar

    def update_progress(self):
        value = self.progress_bar.value()
        if value < 100:
            self.progress_bar.setValue(value + 1)
            # Update progress again after 100 milliseconds
            QTimer.singleShot(100, self.update_progress)
        else:
            self.timer.stop()  # Stop the timer when progress reaches 100%
            self.progress_bar.setValue(0)  # Reset progress to 0
            self.timer.start(100)   

    # show an error message 
    def show_error_message(self, message):
        root = tk.Tk()
        root.withdraw()  
        messagebox.showerror("Error", message)
        root.destroy()
