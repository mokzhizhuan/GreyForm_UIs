from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PythonApplication.progressBar as Progress
import PythonApplication.dxfframeloader as dxfload
import geopandas as gpd

# load pyvista in the frame
class FileSelectionMesh():
    def __init__(self, file_path, mainwindowforfileselection):
        # starting initialize
        super().__init__()
        self.file_path = file_path
        self.mainwindowforfileselection = mainwindowforfileselection
        self.loader = mainwindowforfileselection[0]
        self.loader_2 = mainwindowforfileselection[1]
        self.renderer = mainwindowforfileselection[2]
        self.renderWindowInteractor = mainwindowforfileselection[3]
        self.Ylabel = mainwindowforfileselection[4]
        self.Xlabel = mainwindowforfileselection[5]
        self.Xlabel_before = mainwindowforfileselection[6]
        self.Ylabel_before = mainwindowforfileselection[7]
        self.Zlabel_before = mainwindowforfileselection[8]
        self.seq1Button = mainwindowforfileselection[9]
        self.seq2Button = mainwindowforfileselection[10]
        self.seq3Button = mainwindowforfileselection[11]
        self.NextButton_Page_3 = mainwindowforfileselection[12]
        self.Stagelabel = mainwindowforfileselection[13]
        self.localizebutton = mainwindowforfileselection[14]
        self.rosnode = mainwindowforfileselection[15]
        self.excelfiletext = mainwindowforfileselection[16]
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
        elif ".dxf" in self.file_path:
            gdf = gpd.read_file(self.file_path, engine="fiona")
            dxfload.dxfloader(self.file_path, self.mainwindowforfileselection, gdf)