from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PythonApplication.progressBar as Progress
import PythonApplication.IFCpythondialog as ProgressIFCFile


#load pyvista in the frame
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

