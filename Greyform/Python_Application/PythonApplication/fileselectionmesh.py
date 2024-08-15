from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PythonApplication.progressBar as Progress
import ifcopenshell
import ifcopenshell.geom
import PythonApplication.IFCpythondialog as ProgressIFCFile


# load pyvista in the frame
class FileSelectionMesh(QMainWindow):
    def __init__(self, file_path, mainwindowforfileselection):
        self.file_path = file_path
        self.mainwindowforfileselection = mainwindowforfileselection
        self.meshdata()

    # load meshdata from file
    def meshdata(self):
        if ".stl" in self.file_path:
            progressbarprogram = Progress.pythonProgressBar(
                80000, self.file_path, self.mainwindowforfileselection
            )
            progressbarprogram.exec_()
        elif ".ifc" in self.file_path:
            try:
                ifc_file = ifcopenshell.open(self.file_path)
            except Exception as e:
                self.log_error(f"Failed to open IFC file: {e}")
            else:
                progressbarprogram = ProgressIFCFile.ProgressBarDialogIFC(
                    30000, ifc_file, self.mainwindowforfileselection
                )
                progressbarprogram.exec_()

    def log_error(self, message):
        with open("error_log.txt", "a") as log_file:
            log_file.write(message + "\n")
