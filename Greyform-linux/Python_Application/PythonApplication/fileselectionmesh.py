from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PythonApplication.progressBar as Progress
import PythonApplication.dxfframeloader as dxfload
import PythonApplication.IFCpythondialog as ProgressIFCFile
import ifcopenshell
import geopandas as gpd

# load pyvista in the frame
class FileSelectionMesh():
    def __init__(self, file_path, mainwindowforfileselection , mainwindow, stackedWidget):
        # starting initialize
        super().__init__()
        self.file_path = file_path
        self.mainwindowforfileselection = mainwindowforfileselection
        self.mainwindow = mainwindow
        self.stackedWidget = stackedWidget
        self.meshdata()

    # load meshdata from file
    def meshdata(self):
        if ".stl" in self.file_path:
            progressbarprogram = Progress.pythonProgressBar(
                80000, self.file_path, self.mainwindowforfileselection , self.mainwindow
            )
            progressbarprogram.exec_()
        elif ".dxf" in self.file_path:
            gdf = gpd.read_file(self.file_path, engine="fiona")
            dxfload.dxfloader(self.file_path, self.mainwindowforfileselection, gdf , self.mainwindow, self.stackedWidget)
        elif ".ifc" in self.file_path:
            try:
                ifc_file = ifcopenshell.open(self.file_path)
            except Exception as e:
                self.log_error(f"Failed to open IFC file: {e}")
            else:
                progressbarprogram = ProgressIFCFile.ProgressBarDialogIFC(
                    30000, ifc_file, self.mainwindowforfileselection , self.mainwindow ,self.stackedWidget
                )
                progressbarprogram.exec_()

    
    #error message implement for converting to text file
    def log_error(self, message):
        with open("error_log.txt", "a") as log_file:
            log_file.write(message + "\n")