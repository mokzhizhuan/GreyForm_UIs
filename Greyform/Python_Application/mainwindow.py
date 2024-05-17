from PyQt5 import QtCore, QtWidgets, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import PythonApplication.menu_close as closewindow
import PythonApplication.menuconfirm as backtomenudialog
import PythonApplication.fileselectionmesh as fileselectionmesh
import PythonApplication.setsequence as SequenceData
import PythonApplication.createmesh as Createmesh
from pyvistaqt import QtInteractor
from vtkmodules.qt import QVTKRenderWindowInteractor
import PythonApplication.menu_confirmack as confirmack
import PythonApplication.setting as setting
import PythonApplication.enable_robot as robotenabler
import vtk
import os


# load the mainwindow application
class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.mainwindow = uic.loadUi("UI_Design/mainframe.ui", self)
        self.mainwindow.resize(1920, 1080)
        self.filepaths = os.getcwd()
        self.file = None
        self.file_path = None
        self.mainwindow.stackedWidget.setCurrentIndex(0)
        self.renderer = vtk.vtkRenderer()
        self.append_filter = vtk.vtkAppendPolyData()
        self._translate = QCoreApplication.translate
        self.setupUi()

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
        self.settingpageuipage = setting.Setting(self.stackedWidget, self.mainwindow)#insert setting
        self.mainwindow.verticalLayout_2.setStretch(1,1)
        self.mainwindow.verticalLayout_2.addWidget(self.settingpageuipage)
        self.retranslateUi()
        self.button_UI()

    # button interaction
    def button_UI(self):
        self.mainwindow.menuStartButton.clicked.connect(
            lambda: self.mainwindow.stackedWidget.setCurrentIndex(1)
        )
        self.mainwindow.menuCloseButton.clicked.connect(
            lambda: closewindow.Ui_Dialog_Close.show_dialog_close(self.mainwindow)
        )
        self.mainwindow.Selectivefilelistview.clicked.connect(self.on_selection_changed)
        self.mainwindow.NextButton_Page_2.clicked.connect(
            lambda: self.mainwindow.stackedWidget.setCurrentIndex(2)
        )
        self.mainwindow.BacktoMenuButton.clicked.connect(
            lambda: backtomenudialog.Ui_Dialog_Confirm.show_dialog_confirm(
                self.mainwindow, self.mainwindow.stackedWidget
            )
        )
        self.mainwindow.FilePathButton.clicked.connect(self.browsefilesdirectory)
        self.mainwindow.BacktoMenuButton.clicked.connect(
            lambda: self.mainwindow.stackedWidget.setCurrentIndex(0)
        )
        self.mainwindow.BackButton_Page_2.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(1)
        )
        self.mainwindow.BackButton_2.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(2)
        )
        self.mainwindow.NextButton_Page_3.clicked.connect(
            lambda: self.mainwindow.stackedWidget.setCurrentIndex(3)
        )
        self.mainwindow.seq1Button.clicked.connect(
            lambda: SequenceData.loadseqdata.on_selection_sequence(
                self.mainwindow.seq1Button,
                self.mainwindow.NextButton_Page_3,
                self.mainwindow.Seqlabel,
            )
        )
        self.mainwindow.seq2Button.clicked.connect(
            lambda: SequenceData.loadseqdata.on_selection_sequence(
                self.mainwindow.seq2Button,
                self.mainwindow.NextButton_Page_3,
                self.mainwindow.Seqlabel,
            )
        )
        self.mainwindow.seq3Button.clicked.connect(
            lambda: SequenceData.loadseqdata.on_selection_sequence(
                self.mainwindow.seq3Button,
                self.mainwindow.NextButton_Page_3,
                self.mainwindow.Seqlabel,
            )
        )
        self.mainwindow.NextButton_Page_3.clicked.connect(
            lambda: Createmesh.createMesh.createmesh(
                self,
                self.renderer,
                self.file_path,
                self.renderWindowInteractor,
                self.mainwindow.Ylabel,
                self.mainwindow.Xlabel,
                self.mainwindow.Xlabel_2,
                self.mainwindow.Ylabel_2,
                self.mainwindow.Zlabel,
                self.append_filter,
            )
        )
        self.mainwindow.ConfirmButton.clicked.connect(
            lambda: self.mainwindow.stackedWidget.setCurrentIndex(4)
        )
        self.mainwindow.HomeButton.clicked.connect(
            lambda: self.mainwindow.stackedWidget.setCurrentIndex(0)
        )
        self.mainwindow.CloseButton.clicked.connect(
            lambda: closewindow.Ui_Dialog_Close.show_dialog_close(self.mainwindow)
        )
        self.mainwindow.ConfirmAckButton.clicked.connect(
            lambda: confirmack.Ui_Dialog_ConfirmAck.show_dialog_ConfirmAck(
                self.mainwindow, self.append_filter
            )
        )
        self.mainwindow.MarkingButton.clicked.connect(
            lambda: self.mainwindow.stackedWidget.setCurrentIndex(3)
        )
        self.mainwindow.EnableRobotButton.clicked.connect(
            lambda: robotenabler.EnableRobotInterpreter()
        )
        self.mainwindow.SettingButton.clicked.connect(
            lambda: self.mainwindow.stackedWidget.setCurrentIndex(5)
        )

    def browsefilesdirectory(self):
        dialog = QFileDialog(self.mainwindow)
        dialog.resize(500, 400)
        self.filepaths = dialog.getExistingDirectory(
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
            self.mainwindow.horizontalLayout_2,
            self.mainwindow.horizontalLayout_4,
            self.file_path,
            self.plotterloader,
            self.plotterloader_2,
            self.mainwindow.pyvistaframe,
            self.mainwindow.pyvistaframe_2,
            self.mainwindow.horizontalLayoutWidget,
            self.mainwindow.horizontalLayoutWidget_2,
        )
        self.file = file.replace(".stl", "")
        self.mainwindow.NextButton_Page_2.show()

        self.mainwindow.Itemlabel.setText(
            self._translate("MainWindow", "Product : " + str(self.file))
        )
        self.mainwindow.Itemlabel_2.setText(
            self._translate("MainWindow", "Product: " + str(self.file))
        )
        # clean layout

    def clearLayout(self):
        while self.mainwindow.horizontalLayout_2.count():
            child = self.mainwindow.horizontalLayout_2.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        while self.mainwindow.horizontalLayout_4.count():
            child = self.mainwindow.horizontalLayout_4.takeAt(0)
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
        self.mainwindow.verticalLayoutWidget.close()
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
