import sys
from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pyvistaqt import QtInteractor
import PythonApplication.progressBar as Progress


#load pyvista in the frame
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
        self.meshdata()

    # load meshdata from file
    def meshdata(self):
        # clear mesh
        self.clearLayout()
        self.horizontalLayout.addWidget(self.plotterloader.interactor)
        self.horizontalLayout_page2.addWidget(self.plotterloader_2.interactor)
        progressbarprogram = Progress.pythonProgressBar(
            60000, self.plotterloader, self.plotterloader_2, self.file_path
        )
        progressbarprogram.exec_()

    # clear layout
    def clearLayout(self):
        while self.horizontalLayout.count():
            child = self.horizontalLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        while self.horizontalLayout_page2.count():
            child = self.horizontalLayout_page2.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    
    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.horizontalLayout.close()
        self.horizontalLayout_page2.close()
        self.pyvistaframe.close()
        self.plotterloader.close()
        self.plotterloader_2.close()
        self.pyvistaframe_2.close()
        self.plotterloader.GetRenderWindow().Finalize()
        self.plotterloader_2.GetRenderWindow().Finalize()
