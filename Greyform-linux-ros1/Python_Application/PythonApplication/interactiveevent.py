from PyQt5.QtCore import *
from vtk import *
import tkinter as tk
from tkinter import messagebox
import time , re
from PyQt5.QtWidgets import QProgressDialog, QApplication, QDialog, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer , Qt
import PythonApplication.actors as createactorvtk

class myInteractorStyle(vtkInteractorStyleTrackballCamera):
    def __init__(
        self, setcamerainteraction, wall_identifiers, parent=None
    ):
        # starting initialize
        super().__init__()
        self.render = setcamerainteraction[0]
        self.renderwindowinteractor = setcamerainteraction[1]
        self.meshbound = setcamerainteraction[2]
        self.excelfiletext = setcamerainteraction[4]
        self.stagetext = setcamerainteraction[6]
        self.wall_identifiers = setcamerainteraction[9]
        self.stagestorage = setcamerainteraction[10]
        self.currentindexstage = setcamerainteraction[11]
        self.Stagelabel = setcamerainteraction[12]
        self.walls = setcamerainteraction[13]
        self.wall_actors = setcamerainteraction[14]
        self.wallname = setcamerainteraction[15] 
        self.identifier = setcamerainteraction[16]
        self.stacked_widget = setcamerainteraction[17]
        self.walllabel = setcamerainteraction[18]
        self.listenerdialog = setcamerainteraction[19]
        match = re.search(r'\d+', self.wallname)
        wall_number = int(match.group())
        self.scan = self.identifier[wall_number]
        self.wall_index = list(self.walls.keys()).index(self.wallname) if self.wallname in self.walls else None
        camera = self.render.GetActiveCamera()
        self._translate = QCoreApplication.translate
        self.parent = parent
        self.totalsteps = 100  # Define total steps
        self.stage_completed = False 
        self.remaining_walls_to_scan = set()
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
    
    def initialize_wall_tracking(self):
        """Initialize tracking of walls to ensure all are scanned before moving to the next stage."""
        self.stagetext = self.stagestorage[self.currentindexstage]  # Get current stage
        self.remaining_walls_to_scan = set(self.identifier.keys())  # Get all wall numbers in current stage
        self.stage_completed = False  # Ensure we track when a stage is finished
        self.show_message(f"Initializing tracking for {self.stagetext}. Walls to scan: {self.remaining_walls_to_scan}")

    def find_next_valid_wall(self, wall_keys):
        """Find the next valid unscanned wall or fallback to 'Floor'."""
        while self.wall_index < len(wall_keys) - 1:
            self.wall_index += 1
            self.wallname = wall_keys[self.wall_index]
            match = re.search(r'\d+', str(self.wallname))
            wall_number = int(match.group()) if match else None

            if wall_number in self.identifier and wall_number in self.remaining_walls_to_scan:
                return wall_number
        if "F" in self.remaining_walls_to_scan:
            self.wallname = "Floor"
            return "F"

        return None  # No valid wall or fallback found

    def changewall(self):
        self.wall_actors[self.wallname].VisibilityOff()
        if self.stage_completed and self.stagetext == "Stage 2":
            self.show_message("✅ User pressed again. Moving to Stage 3...")
            self.goto_next_stage_or_page()
            return
        if not self.remaining_walls_to_scan and self.stagetext == "Stage 3" and not self.stage_completed:
            self.show_message("✅ All walls and Floor in Stage 3 scanned. Moving to the next page...")
            self.stacked_widget.setCurrentIndex(5)
            return
        # Initialize tracking if not already set
        if not hasattr(self, "remaining_walls_to_scan") or not self.remaining_walls_to_scan:
            self.initialize_wall_tracking()

        wall_keys = sorted(self.walls.keys())
        wall_number = self.find_next_valid_wall(wall_keys)
        

        if wall_number:
            self.wallname = "Floor" if wall_number == "F" else self.wallname
            self.wall_actors[self.wallname].VisibilityOn()

            # Remove scanned wall
            if wall_number in self.identifier:
                self.scan = self.identifier[wall_number]
                self.listenerdialog.run_execution(self.scan, wall_number, self.stagetext, self.excelfiletext)
                self.remaining_walls_to_scan.discard(wall_number)

            self.walllabel.setText(f"Wall : {self.wallname}")
            self.refresh()

        # ✅ Move to Stage 3 automatically after scanning all walls in Stage 2
        if not self.remaining_walls_to_scan and self.stagetext == "Stage 2" and not self.stage_completed:
            self.stage_completed = True
            self.show_message("✅ Stage 2 complete (including Floor). Press again to move to Stage 3.")
            return  # Wait for user input


    def goto_next_stage_or_page(self):
        # ✅ Otherwise, move to the next stage (Stage 2 → Stage 3)
        self.currentindexstage += 1
        self.wall_index = 0
        self.stagetext = self.stagestorage[self.currentindexstage]
        self.Stagelabel.setText(f"Stage : {self.stagetext}")

        # Reset tracking for new stage
        self.wall_actors, self.identifier, self.wallname = createactorvtk.setupactors(
            self.walls, self.stagetext, self.wall_identifiers, self.render, self.walllabel
        )
        self.initialize_wall_tracking()

        # Start scanning first wall in the new stage
        self.changewall()

    def refresh(self):
        self.render.ResetCameraClippingRange()
        self.renderwindowinteractor.GetRenderWindow().Render()

    def show_message(self, message):
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showinfo("Message", message)
        root.destroy()

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
