from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PythonApplication.setsequence as SequenceData
import PythonApplication.createmesh as Createmesh
import PythonApplication.mainframe_menubutton as buttons_ros
from pyvistaqt import QtInteractor
from vtkmodules.qt import QVTKRenderWindowInteractor
import vtk

#main frame part 3
class Ui_MainWindow(object):
    def __init__(
        self,
        file_path,
        stackedwidgetpage,
        NextButton_Page_3,
        MainWindow,
        file,
        seq1Button,
        seq2Button,
        seq3Button,
    ):
        self.file_path = file_path
        self.stackedWidget = stackedwidgetpage
        self.NextButton_Page_3 = NextButton_Page_3
        self.file = file
        self.seq1Button = seq1Button
        self.seq2Button = seq2Button
        self.seq3Button = seq3Button
        self.append_filter = vtk.vtkAppendPolyData()
        self.renderer = vtk.vtkRenderer()
        self.setupUi_Page3(MainWindow)

    # Page 3 of the UI
    def setupUi_Page3(self, MainWindow):
        self.page_3 = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.page_3.sizePolicy().hasHeightForWidth())
        self.page_3.setSizePolicy(sizePolicy)
        self.page_3.setObjectName("page_3")
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=self.page_3)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(160, 20, 1600, 800))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.vtkframe = QFrame(self.verticalLayoutWidget)
        self.vtkframe.setObjectName("pyvistaframe_2")
        self.vtkframe.setFrameShape(QFrame.StyledPanel)
        self.vtkframe.setFrameShadow(QFrame.Raised)
        self.vtkframe.setGeometry(QtCore.QRect(160, 20, 1600, 800))
        # Create a render window, and set interaction styles
        self.renderWindowInteractor = (
            QVTKRenderWindowInteractor.QVTKRenderWindowInteractor(self.vtkframe)
        )
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.addWidget(self.vtkframe)
        self.Ygroupbox = QtWidgets.QGroupBox(parent=self.page_3)
        self.Ygroupbox.setGeometry(QtCore.QRect(1700, 940, 171, 51))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Ygroupbox.sizePolicy().hasHeightForWidth())
        self.Ygroupbox.setSizePolicy(sizePolicy)
        self.Ygroupbox.setTitle("")
        self.Ygroupbox.setObjectName("Ygroupbox")
        self.titleYlabel = QtWidgets.QLabel(parent=self.Ygroupbox)
        self.titleYlabel.setGeometry(QtCore.QRect(10, 20, 61, 17))
        self.titleYlabel.setObjectName("titleYlabel")
        self.Ylabel = QtWidgets.QLabel(parent=self.Ygroupbox)
        self.Ylabel.setGeometry(QtCore.QRect(80, 10, 91, 31))
        self.Ylabel.setObjectName("Ylabel")
        self.Xgroupbox = QtWidgets.QGroupBox(parent=self.page_3)
        self.Xgroupbox.setGeometry(QtCore.QRect(1700, 860, 171, 61))
        self.Xgroupbox.setTitle(""), self.Xgroupbox.setObjectName("Xgroupbox")
        self.titleXlabel = QtWidgets.QLabel(parent=self.Xgroupbox)
        self.titleXlabel.setGeometry(QtCore.QRect(10, 20, 71, 17))
        self.titleXlabel.setObjectName("titleXlabel")
        self.Xlabel = QtWidgets.QLabel(parent=self.Xgroupbox)
        self.Xlabel.setGeometry(
            QtCore.QRect(80, 20, 91, 31)
        ), self.Xlabel.setObjectName("Xlabel")
        self.BackButton_Page_2 = QtWidgets.QPushButton(parent=self.page_3)
        self.BackButton_Page_2.setGeometry(QtCore.QRect(590, 980, 80, 25))
        self.BackButton_Page_2.setObjectName(
            "BackButton_2"
        ), self.BackButton_Page_2.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(2)
        )
        self.ConfirmButton = QtWidgets.QPushButton(parent=self.page_3)
        self.ConfirmButton.setGeometry(QtCore.QRect(430, 980, 80, 25))
        self.ConfirmButton.setObjectName("ConfirmButton")
        self.Itemlabel_Page_3 = QtWidgets.QLabel(parent=self.page_3)
        self.Itemlabel_Page_3.setGeometry(QtCore.QRect(480, 910, 751, 21))
        self.Itemlabel_Page_3.setObjectName("Itemlabel_Page_3")
        self.Seqlabel = QtWidgets.QLabel(parent=self.page_3)
        self.Seqlabel.setGeometry(QtCore.QRect(480, 850, 751, 21))
        self.Seqlabel.setObjectName("Seqlabel")
        self.Xgroupbox_2 = QGroupBox(self.page_3)
        self.Xgroupbox_2.setObjectName("Xgroupbox_2")
        self.Xgroupbox_2.setGeometry(QRect(1480, 860, 171, 61))
        self.titleXlabel_2 = QLabel(self.Xgroupbox_2)
        self.titleXlabel_2.setObjectName("titleXlabel_2")
        self.titleXlabel_2.setGeometry(QRect(10, 20, 71, 17))
        self.Xlabel_2 = QLabel(self.Xgroupbox_2)
        self.Xlabel_2.setObjectName("Xlabel_2")
        self.Xlabel_2.setGeometry(QRect(80, 20, 91, 31))
        self.Ygroupbox_2 = QGroupBox(self.page_3)
        self.Ygroupbox_2.setObjectName("Ygroupbox_2")
        self.Ygroupbox_2.setGeometry(QRect(1360, 950, 171, 51))
        self.titleYlabel_2 = QLabel(self.Ygroupbox_2)
        self.titleYlabel_2.setObjectName("titleYlabel_2")
        self.titleYlabel_2.setGeometry(QRect(10, 20, 61, 17))
        self.Ylabel_2 = QLabel(self.Ygroupbox_2)
        self.Ylabel_2.setObjectName("Ylabel_2")
        self.Ylabel_2.setGeometry(QRect(80, 10, 91, 31))
        self.displaybeforelabel = QLabel(self.page_3)
        self.displaybeforelabel.setObjectName("displaybeforelabel")
        self.displaybeforelabel.setGeometry(QRect(1360, 840, 181, 17))
        self.label_2 = QLabel(self.page_3)
        self.label_2.setObjectName("label_2")
        self.label_2.setGeometry(QRect(1740, 830, 101, 17))
        self.Zgroupbox = QGroupBox(self.page_3)
        self.Zgroupbox.setObjectName("Zgroupbox")
        self.Zgroupbox.setGeometry(QRect(1260, 860, 171, 61))
        self.titleZlabel_3 = QLabel(self.Zgroupbox)
        self.titleZlabel_3.setObjectName("titleZlabel_3")
        self.titleZlabel_3.setGeometry(QRect(10, 20, 71, 17))
        self.Zlabel = QLabel(self.Zgroupbox)
        self.Zlabel.setObjectName("Zlabel")
        self.Zlabel.setGeometry(QRect(80, 20, 91, 31))
        self.stackedWidget.addWidget(self.page_3)
        buttons_ros.Ui_MainWindow(self.stackedWidget, MainWindow, self.append_filter)
        self.button_UI(MainWindow)
        self.finalizeUI(MainWindow)

    def finalizeUI(self, MainWindow):
        self.retranslateUi(MainWindow)

    # button interaction
    def button_UI(self, MainWindow):
        self.NextButton_Page_3.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(3)
        )
        self.seq1Button.clicked.connect(
            lambda: SequenceData.loadseqdata.on_selection_sequence(
                self.seq1Button, self.NextButton_Page_3, self.Seqlabel
            )
        )
        self.seq2Button.clicked.connect(
            lambda: SequenceData.loadseqdata.on_selection_sequence(
                self.seq2Button, self.NextButton_Page_3, self.Seqlabel
            )
        )
        self.seq3Button.clicked.connect(
            lambda: SequenceData.loadseqdata.on_selection_sequence(
                self.seq3Button, self.NextButton_Page_3, self.Seqlabel
            )
        )
        self.NextButton_Page_3.clicked.connect(
            lambda: Createmesh.createMesh.createmesh(
                self,
                self.renderer,
                self.file_path,
                self.renderWindowInteractor,
                self.Ylabel,
                self.Xlabel,
                self.Xlabel_2,
                self.Ylabel_2,
                self.Zlabel,
                self.append_filter
            )
        )
        self.ConfirmButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(4)
        )

    def closeEvent(self, event):
        self.vtkframe.close()
        self.renderWindowInteractor.GetRenderWindow().MakeCurrent()
        self.renderWindowInteractor.Finalize()
        self.renderWindowInteractor.GetRenderWindow().ClearInRenderStatus()
        self.renderWindowInteractor.GetRenderWindow().RemoveAllObservers()
        self.renderWindowInteractor.GetRenderWindow().Finalize()
        self.renderWindowInteractor.GetRenderWindow().GetInteractor().TerminateApp()
        self.verticalLayoutWidget.close()
        event.accept()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.seq1Button.setText(_translate("MainWindow", "Sequence 1"))
        self.seq2Button.setText(_translate("MainWindow", "Sequence 2"))
        self.seq3Button.setText(_translate("MainWindow", "Sequence 3"))
        self.NextButton_Page_3.setText(_translate("MainWindow", "Next"))
        self.titleYlabel.setText(_translate("MainWindow", "Height:"))
        self.Ylabel.setText(_translate("MainWindow", "0"))
        self.titleXlabel.setText(_translate("MainWindow", "Width:"))
        self.Xlabel.setText(_translate("MainWindow", "0"))
        self.BackButton_Page_2.setText(_translate("MainWindow", "Back"))
        self.ConfirmButton.setText(_translate("MainWindow", "Confirm"))
        self.Itemlabel_Page_3.setText(
            _translate("MainWindow", "Product: " + str(self.file))
        )
        self.Seqlabel.setText(_translate("MainWindow", "Sequence:"))
        self.titleXlabel_2.setText(_translate("MainWindow", "Width:"))
        self.Xlabel_2.setText(_translate("MainWindow", "0"))
        self.titleYlabel_2.setText(_translate("MainWindow", "Height:"))
        self.Ylabel_2.setText(_translate("MainWindow", "0"))
        self.displaybeforelabel.setText(
            _translate("MainWindow", "Mesh Camera Dimensions")
        )
        self.label_2.setText(
            QCoreApplication.translate("MainWindow", "Click Position", None)
        )
        self.Zgroupbox.setTitle("")
        self.titleZlabel_3.setText(
            QCoreApplication.translate("MainWindow", "Length:", None)
        )
        self.Zlabel.setText(QCoreApplication.translate("MainWindow", "0", None))
