import menu_close as closewindow
import PythonApplication.menuconfirm as backtomenudialog
import menu_sendmodel as sendmodel
from PyQt5 import QtCore, QtWidgets, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


# main window button interaction
class mainwindowbuttonUI(object):
    def __init__(
        self,
        mainwindow,
        stackedWidget,
        menuStartButton,
        menuCloseButton,
        NextButton_Page_2,
        BacktoMenuButton,
        BackButton_Page_2,
        ChooseButton,
        sendmodelButton,
        CloseButton,
        ros_node,
    ):
        # starting initialize
        super().__init__()
        self.mainwindow = mainwindow
        self.stackedWidget = stackedWidget
        self.menuStartButton = menuStartButton
        self.menuCloseButton = menuCloseButton
        self.NextButton_Page_2 = NextButton_Page_2
        self.BacktoMenuButton = BacktoMenuButton
        self.BackButton_Page_2 = BackButton_Page_2
        self.ChooseButton = ChooseButton
        self.CloseButton = CloseButton
        self.sendmodelButton = sendmodelButton
        self.ros_node = ros_node
        self.button_UI()

    # stacked widget page ui
    def startconfigure(self):
        self.stackedWidget.setCurrentIndex(1)

    def confirmmodel(self):
        self.stackedWidget.setCurrentIndex(2)

    # button interaction ui
    def button_UI(self):
        self.menuStartButton.clicked.connect(self.startconfigure)
        self.menuCloseButton.clicked.connect(
            lambda: closewindow.Ui_Dialog_Close.show_dialog_close(
                self.mainwindow, self.ros_node
            )
        )
        self.NextButton_Page_2.clicked.connect(self.confirmmodel)
        self.BacktoMenuButton.clicked.connect(
            lambda: backtomenudialog.Ui_Dialog_Confirm.show_dialog_confirm(
                self.mainwindow,
                self.stackedWidget,
            )
        )
        self.ChooseButton.clicked.connect(self.startconfigure)
        self.BackButton_Page_2.clicked.connect(self.startconfigure)
        self.CloseButton.clicked.connect(
            lambda: closewindow.Ui_Dialog_Close.show_dialog_close(
                self.mainwindow, self.ros_node
            )
        )
        self.sendmodelButton.clicked.connect(
            lambda: sendmodel.Ui_Dialog_Confirm.show_dialog_confirm(
                self.mainwindow, self.ros_node
            )
        )