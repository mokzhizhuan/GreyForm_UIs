import sys
from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pyvistaqt import QtInteractor
import PythonApplication.progressBar as Progress


# load pyvista in the frame
class FileSelectionMesh(QMainWindow):
    def __init__(
        self,
        horizontalLayout,
        horizontalLayout_page2,
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
    ):
        self.horizontalLayout = horizontalLayout
        self.horizontalLayout_page2 = horizontalLayout_page2
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
        self.meshdata()

    # load meshdata from file
    def meshdata(self):
        # clear mesh
        self.horizontalLayout.addWidget(self.plotterloader.interactor)
        self.horizontalLayout_page2.addWidget(self.plotterloader_2.interactor)
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
        )
        progressbarprogram.exec_()
