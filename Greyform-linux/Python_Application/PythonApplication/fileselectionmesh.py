import sys
from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import OpenGL.GL as gl
import pyqtgraph.opengl as gl
import ifcopenshell
import ifcopenshell.geom
from ifcopenshell.util.placement import get_local_placement
from pyvistaqt import QtInteractor
import multiprocessing
import PythonApplication.progressBar as Progress
import PythonApplication.IFCpythondialog as ProgressIFCFile


#load pyvista in the frame
class FileSelectionMesh(QMainWindow):
    def __init__(
        self,
        file_path,
        plotterloader,
        plotterloader_2,
        pyvistaframe,
        pyvistaframe_2,
        layoutWidget,
        layoutWidget_page2,
        renderer,
        renderWindowInteractor,
        Ylabel,
        Xlabel,
        Xlabel_before,
        Ylabel_before,
        Zlabel_before,
        append_filter,
        seq1Button,
        seq2Button,
        seq3Button,
        NextButton_Page_3,
        Seqlabel,
    ):
        self.plotterloader = plotterloader
        self.plotterloader_2 = plotterloader_2
        self.pyvistaframe = pyvistaframe
        self.pyvistaframe_2 = pyvistaframe_2
        self.layoutwidget = layoutWidget
        self.layoutwidget_page2 = layoutWidget_page2
        self.file_path = file_path
        self.renderer = renderer
        self.renderWindowInteractor = renderWindowInteractor
        self.Ylabel = Ylabel
        self.Xlabel = Xlabel
        self.Xlabel_before = Xlabel_before
        self.Ylabel_before = Ylabel_before
        self.Zlabel_before = Zlabel_before
        self.append_filter = append_filter
        self.seq1Button = seq1Button
        self.seq2Button = seq2Button
        self.seq3Button = seq3Button
        self.NextButton_Page_3 = NextButton_Page_3
        self.Seqlabel = Seqlabel
        self.meshdata()

    # load meshdata from file
    def meshdata(self):
        if ".stl" in self.file_path:
            progressbarprogram = Progress.pythonProgressBar(
                100000,
                self.plotterloader,
                self.plotterloader_2,
                self.file_path,
                self.renderer,
                self.renderWindowInteractor,
                self.Xlabel,
                self.Ylabel,
                self.Xlabel_before,
                self.Ylabel_before,
                self.Zlabel_before,
                self.append_filter,
                self.seq1Button,
                self.seq2Button,
                self.seq3Button,
                self.NextButton_Page_3,
                self.Seqlabel,
            )
            progressbarprogram.exec_()
        elif ".ifc" in self.file_path:
            try:
                ifc_file = ifcopenshell.open(self.file_path)
            except Exception as e:
                self.log_error(f"Failed to open IFC file: {e}")
            else:
                progressbarprogram = ProgressIFCFile.ProgressBarDialogIFC(
                    80000,
                    ifc_file,
                    self.plotterloader,
                    self.plotterloader_2,
                    self.renderer,
                    self.renderWindowInteractor,
                    self.Xlabel,
                    self.Ylabel,
                    self.Xlabel_before,
                    self.Ylabel_before,
                    self.Zlabel_before,
                    self.append_filter,
                    self.seq1Button,
                    self.seq2Button,
                    self.seq3Button,
                    self.NextButton_Page_3,
                    self.Seqlabel,
                )
                progressbarprogram.exec_()

