from PyQt5 import QtCore, QtWidgets, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import mainwindowlayout as mainwindowuilayout
import PythonApplication.fileselectionmesh as fileselectionmesh
import PythonApplication.setsequence as SequenceData
from pyvistaqt import QtInteractor
from vtkmodules.qt import QVTKRenderWindowInteractor
import mainwindowbuttoninteraction as mainwindowbuttonUIinteraction
import PythonApplication.setting as setting
import vtk
import os


# load the mainwindow application
class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.mainwindow = uic.loadUi("UI_Design/mainframe.ui", self)
        self.width = 800
        self.height = 600
        self.mainwindow.resize(self.width, self.height)
        self.filepaths = os.getcwd()
        self.file = None
        self.file_path = None
        self.renderer = vtk.vtkRenderer()
        self.append_filter = vtk.vtkAppendPolyData()
        self._translate = QCoreApplication.translate
        self.setupUi()

    # setup UI
    def setupUi(self):
        self.mainwindow.NextButton_Page_2.hide()
        self.plotterloader = QtInteractor(
            self.mainwindow.pyvistaframe,
            line_smoothing=True,
            point_smoothing=True,
            polygon_smoothing=True,
            multi_samples=8,
        )
        self.plotterloader.enable()
        self.plotterloader_2 = QtInteractor(
            self.mainwindow.pyvistaframe_2,
            line_smoothing=True,
            point_smoothing=True,
            polygon_smoothing=True,
            multi_samples=8,
        )
        self.plotterloader_2.enable()
        self.renderWindowInteractor = (
            QVTKRenderWindowInteractor.QVTKRenderWindowInteractor(
                self.mainwindow.vtkframe
            )
        )
        self.mainwindow.horizontalLayout_2.addWidget(self.plotterloader.interactor)
        self.mainwindow.horizontalLayout_4.addWidget(self.plotterloader_2.interactor)
        self.mainwindow.verticalLayout.addWidget(self.renderWindowInteractor)
        self.settingpageuipage = setting.Setting(
            self.mainwindow.stackedWidget,
            self.mainwindow,
            self.width,
            self.height,
        )  # insert setting
        self.setStretch()
        self.retranslateUi()
        self.button_UI()

    # button interaction
    def button_UI(self):
        self.mainwindow.Selectivefilelistview.clicked.connect(self.on_selection_changed)
        self.mainwindow.FilePathButton.clicked.connect(self.browsefilesdirectory)
        for i in range(1, 4):
            button = getattr(self.mainwindow, f"seq{i}Button")
            self.addbuttonseq(
                button, self.mainwindow.NextButton_Page_3, self.mainwindow.Seqlabel
            )
        mainwindowbuttonUIinteraction.mainwindowbuttonUI(
            self.mainwindow,
            self.mainwindow.stackedWidget,
            self.mainwindow.menuStartButton,
            self.mainwindow.menuCloseButton,
            self.mainwindow.NextButton_Page_2,
            self.mainwindow.BacktoMenuButton,
            self.mainwindow.BackButton_Page_2,
            self.mainwindow.BackButton_2,
            self.mainwindow.NextButton_Page_3,
            self.mainwindow.ConfirmButton,
            self.mainwindow.HomeButton,
            self.mainwindow.CloseButton,
            self.mainwindow.ConfirmAckButton,
            self.mainwindow.MarkingButton,
            self.mainwindow.EnableRobotButton,
            self.mainwindow.SettingButton,
            self.append_filter,
        )

    def addbuttonseq(self, button, nextbutton, seqlabel):
        button.clicked.connect(
            lambda: SequenceData.loadseqdata.on_selection_sequence(
                button, nextbutton, seqlabel
            )
        )

    def browsefilesdirectory(self):
        self.filepaths = QFileDialog.getExistingDirectory(
            None, "Choose Directory", self.filepaths
        )
        model = QFileSystemModel()
        model.setRootPath(self.filepaths)
        model.setFilter(QDir.NoDotAndDotDot | QDir.Files)
        self.mainwindow.Selectivefilelistview.setModel(model)
        self.mainwindow.Selectivefilelistview.setRootIndex(model.index(self.filepaths))
        self.mainwindow.Selectivefilelistview.setAlternatingRowColors(True)

    # file selection when clicked
    def on_selection_changed(self, index):
        model = self.mainwindow.Selectivefilelistview.model()
        self.file_path = model.filePath(index)
        file = self.mainwindow.Selectivefilelistview.model().itemData(index)[0]
        fileselectionmesh.FileSelectionMesh(
            self.file_path,
            self.plotterloader,
            self.plotterloader_2,
            self.mainwindow.pyvistaframe,
            self.mainwindow.pyvistaframe_2,
            self.mainwindow.layoutWidgetframe,
            self.mainwindow.layoutWidgetpage3,
            self.renderer,
            self.renderWindowInteractor,
            self.mainwindow.Ylabel,
            self.mainwindow.Xlabel,
            self.mainwindow.Xlabel_2,
            self.mainwindow.Ylabel_2,
            self.mainwindow.Zlabel,
            self.append_filter,
        )
        if ".stl" in file:
            self.file = file.replace(".stl", "")
        elif ".ifc" in file:
            self.file = file.replace(".ifc", "")
        self.mainwindow.NextButton_Page_2.show()
        self.mainwindow.Itemlabel.setText(
            self._translate("MainWindow", "Product : " + str(self.file))
        )
        self.mainwindow.Itemlabel_2.setText(
            self._translate("MainWindow", "Product: " + str(self.file))
        )

    def setStretch(self):
        mainwindowuilayout.Ui_MainWindow_layout(
            self.mainwindow.stackedWidget,
            self.mainwindow.centralwidget,
            self.mainwindow.QTitle,
            self.mainwindow.layoutWidget,
            self.mainwindow.horizontalLayout,
            self.mainwindow.mainmenu,
            self.mainwindow.layoutWidgetpage2,
            self.mainwindow.layoutWidgetframe,
            self.mainwindow.page,
            self.mainwindow.Itemlabel,
            self.mainwindow.layoutWidgetpage3,
            self.mainwindow.page_2,
            self.mainwindow.layoutWidgetpage4,
            self.mainwindow.horizontalLayoutWidgetpage4,
            self.mainwindow.page_3,
            self.mainwindow.SettingButton,
            self.mainwindow.layoutWidgetpage5,
            self.mainwindow.page_4,
            self.settingpageuipage,
            self.mainwindow.settingpage,
        )

    # clean layout
    def clearLayout(self):
        while self.mainwindow.layoutWidgetframe.count():
            child = self.mainwindow.layoutWidgetframe.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        while self.mainwindow.layoutWidgetpage3.count():
            child = self.mainwindow.layoutWidgetpage3.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def closeEvent(self, event):
        self.mainwindow.vtkframe.close()
        self.renderWindowInteractor.GetRenderWindow().MakeCurrent()
        self.renderWindowInteractor.Finalize()
        self.renderWindowInteractor.GetRenderWindow().ClearInRenderStatus()
        self.renderWindowInteractor.GetRenderWindow().RemoveAllObservers()
        self.renderWindowInteractor.GetRenderWindow().Finalize()
        self.renderWindowInteractor.GetRenderWindow().GetInteractor().TerminateApp()
        event.accept()

    def retranslateUi(self):
        self.mainwindow.displaybeforelabel.setText(
            self._translate("MainWindow", "Mesh Camera Dimensions")
        )
        self.mainwindow.label_2.setText(
            self._translate("MainWindow", "Click Position", None)
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())