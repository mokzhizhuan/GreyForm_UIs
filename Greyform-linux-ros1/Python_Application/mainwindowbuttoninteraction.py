import menu_sendmodel as sendmodel
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import subprocess


# main window button interaction
class mainwindowbuttonUI(object):
    def __init__(
        self,
        mainwindow,
        stackedWidget,
        menuStartButton,
        NextButton_Page_2,
        sendmodelButton,
        choosemodelButton,
        DataButton,
        ros_node,
    ):
        # starting initialize
        super().__init__()
        self.mainwindow = mainwindow
        self.stackedWidget = stackedWidget
        self.menuStartButton = menuStartButton
        self.NextButton_Page_2 = NextButton_Page_2
        self.sendmodelButton = sendmodelButton
        self.choosemodelButton = choosemodelButton
        self.DataButton = DataButton
        self.ros_node = ros_node
        self.button_UI()

    # stacked widget page ui
    def startconfigure(self):
        self.stackedWidget.setCurrentIndex(1)

    def confirmmodel(self):
        self.stackedWidget.setCurrentIndex(2)

    def open_excel_file(self):
        excel_path = "exporteddatassss(with TMP)(draft)(tetra).xlsx"
        subprocess.Popen(["libreoffice", excel_path])

    # button interaction ui
    def button_UI(self):
        self.menuStartButton.clicked.connect(self.startconfigure)
        self.NextButton_Page_2.clicked.connect(self.confirmmodel)
        self.sendmodelButton.clicked.connect(
            lambda: sendmodel.Ui_Dialog_Confirm.show_dialog_confirm(
                self.mainwindow, self.ros_node
            )
        )
        self.choosemodelButton.clicked.connect(lambda: self.startconfigure())
        self.DataButton.clicked.connect(lambda: self.open_excel_file())