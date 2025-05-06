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
        NextButton_Page_2,
        ChooseButton,
        sendmodelButton,
    ):
        # starting initialize
        super().__init__()
        self.mainwindow = mainwindow
        self.stackedWidget = stackedWidget
        self.menuStartButton = menuStartButton
        self.NextButton_Page_2 = NextButton_Page_2
        self.ChooseButton = ChooseButton
        self.sendmodelButton = sendmodelButton
        self.button_UI()

    # stacked widget page ui
    def startconfigure(self):
        self.stackedWidget.setCurrentIndex(1)

    def confirmmodel(self):
        self.stackedWidget.setCurrentIndex(2)

    # button interaction ui
    def button_UI(self):
        self.menuStartButton.clicked.connect(self.startconfigure)
        self.NextButton_Page_2.clicked.connect(self.confirmmodel)
        self.ChooseButton.clicked.connect(self.startconfigure)
        self.sendmodelButton.clicked.connect(
            lambda: sendmodel.Ui_Dialog_Confirm.show_dialog_confirm(
                self.mainwindow
            )
        )