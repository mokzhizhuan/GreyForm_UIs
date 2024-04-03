from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PythonApplication.fileselectionmesh as fileselectionmesh
import PythonApplication.setsequence as SequenceData
import PythonApplication.menuconfirm as backtomenudialog
import PythonApplication.menu_close as closewindow
import PythonApplication.mainframe_page as mainframe_Pagefile
from pyvistaqt import QtInteractor
from vtkmodules.qt import QVTKRenderWindowInteractor
import os


# main frame part 1
class Ui_MainWindow(object):
    def ___init___(self):
        self.MainWindow = None

    # Main Window starting setup
    def setupUi_mainWindow(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        self.MainWindow = MainWindow
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.centralwidget.sizePolicy().hasHeightForWidth()
        )
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.stackedWidget = QtWidgets.QStackedWidget(parent=self.centralwidget)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 0, 1980, 1080))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.stackedWidget.sizePolicy().hasHeightForWidth()
        )
        self.stackedWidget.setSizePolicy(sizePolicy)
        self.stackedWidget.setObjectName("stackedWidget")

        self.setupUi_Menu(MainWindow)

    # Main menu Ui Setup
    def setupUi_Menu(self, MainWindow):
        self.mainmenu = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainmenu.sizePolicy().hasHeightForWidth())
        self.mainmenu.setSizePolicy(sizePolicy)
        self.mainmenu.setObjectName("mainmenu")
        self.QTitle = QtWidgets.QLabel(parent=self.mainmenu)
        self.QTitle.setGeometry(QtCore.QRect(420, 530, 1139, 55))
        self.QTitle.setScaledContents(False)
        self.QTitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.QTitle.setObjectName("QTitle")
        self.menuStartButton = QtWidgets.QPushButton(parent=self.mainmenu)
        self.menuStartButton.setGeometry(QtCore.QRect(730, 980, 240, 25))
        self.menuStartButton.setCheckable(False)
        self.menuStartButton.setObjectName("menuStartButton")
        self.menuCloseButton = QtWidgets.QPushButton(parent=self.mainmenu)
        self.menuCloseButton.setGeometry(QtCore.QRect(1000, 980, 240, 25))
        self.menuCloseButton.setCheckable(False)
        self.menuCloseButton.setObjectName("menuStartButton")
        self.stackedWidget.addWidget(self.mainmenu)
        mainframe_Pagefile.Ui_MainWindow(MainWindow, self.stackedWidget)
        self.button_UI(MainWindow)
        self.finalizeUI(MainWindow)

    # finalizing the ui setup
    def finalizeUI(self, MainWindow):
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # button interaction
    def button_UI(self, MainWindow):
        self.menuStartButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(1)
        )
        self.menuCloseButton.clicked.connect(
            lambda: closewindow.Ui_Dialog_Close.show_dialog_close(MainWindow)
        )

    # translate UI Text
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "mainframe"))
        self.QTitle.setText(
            _translate(
                "MainWindow",
                '<html><head/><body><p><span style=" font-size:36pt;">GREYFORM UI</span></p></body></html>',
            )
        )
        self.menuStartButton.setText(_translate("MainWindow", "Click to Continue"))
        self.menuCloseButton.setText(
            _translate("MainWindow", "Click to Close the Window")
        )
