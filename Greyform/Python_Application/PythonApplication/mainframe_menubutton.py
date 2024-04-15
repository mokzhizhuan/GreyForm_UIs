from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PythonApplication.menu_close as closewindow
import PythonApplication.menu_confirmack as confirmack
from pyvistaqt import QtInteractor
import PythonApplication.enable_robot as robotenabler
import PythonApplication.setting as setting


# main frame part 4
class Ui_MainWindow(object):
    def __init__(self, stackedwidgetpage, MainWindow, append_filter):
        self.stackedWidget = stackedwidgetpage
        self.append_filter = append_filter
        self.setupUi_Page4(MainWindow)


    # Page 4 UI setup
    def setupUi_Page4(self, MainWindow):
        self.page_4 = QWidget()
        self.page_4.setObjectName("page_4")
        font2 = QFont()
        font2.setPointSize(40)
        self.HomeButton = QPushButton(self.page_4)
        self.HomeButton.setFont(font2)
        self.HomeButton.setObjectName("HomeButton")
        self.HomeButton.setGeometry(QRect(150, 470, 500, 270))
        self.CloseButton = QPushButton(self.page_4)
        self.CloseButton.setFont(font2)
        self.CloseButton.setObjectName("CloseButton")
        self.CloseButton.setGeometry(QRect(150, 770, 500, 270))
        self.EnableRobotButton = QPushButton(
            self.page_4
        )  # this one not confirmed must clarify
        self.EnableRobotButton.setFont(font2)
        self.EnableRobotButton.setObjectName("RobotButton")
        self.EnableRobotButton.setGeometry(QRect(1200, 470, 500, 270))
        self.ConfirmackButton = QPushButton(self.page_4)
        self.ConfirmackButton.setFont(font2)
        # using the confirm dialog button to confirm the marking. Basically finalize the marking.
        self.ConfirmackButton.setObjectName("ConfirmButton")
        self.ConfirmackButton.setGeometry(QRect(1200, 780, 500, 270))
        self.MarkingButton = QPushButton(self.page_4)
        self.MarkingButton.setObjectName("MarkingButton")
        self.MarkingButton.setGeometry(QRect(650, 70, 500, 270))
        self.MarkingButton.setFont(font2)
        self.SettingButton = QPushButton(self.page_4)
        self.SettingButton.setObjectName("SettingButton")
        self.SettingButton.setGeometry(QRect(1810, 20, 89, 25))
        self.stackedWidget.addWidget(self.page_4)
        self.setupUi_Page5(MainWindow)

    # Page 5 UI setup
    def setupUi_Page5(self, MainWindow):
        self.settingpage = QWidget()
        self.settingpage.setObjectName("settingpage")
        self.verticalLayoutWidget_2 = QWidget(self.settingpage)
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(60, 30, 1721, 941))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setSpacing(7)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 1)
        self.verticalLayoutWidget_2.setStyleSheet(
            "QWidget#verticalLayoutWidget_2 { border: 2px solid black; }"
        )
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.verticalLayoutWidget_2.sizePolicy().hasHeightForWidth()
        )
        self.settingpageuipage = setting.Setting(self.stackedWidget, MainWindow)#insert setting
        self.verticalLayout_2.addWidget(self.settingpageuipage)
        self.stackedWidget.addWidget(self.settingpage)
        self.button_UI(MainWindow)
        self.finalizeUI(MainWindow)

    def finalizeUI(self, MainWindow):
        self.retranslateUi(MainWindow)

    # button interaction
    def button_UI(self, MainWindow):
        self.HomeButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.CloseButton.clicked.connect(
            lambda: closewindow.Ui_Dialog_Close.show_dialog_close(MainWindow)
        )
        self.ConfirmackButton.clicked.connect(
            lambda: confirmack.Ui_Dialog_ConfirmAck.show_dialog_ConfirmAck(MainWindow, self.append_filter)
        )
        self.MarkingButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(3)
        )
        self.EnableRobotButton.clicked.connect(
            lambda: robotenabler.EnableRobotInterpreter()
        )
        self.SettingButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(5)
        )

    def retranslateUi(self, MainWindow):
        self.HomeButton.setText(QCoreApplication.translate("MainWindow", "Home", None))
        self.EnableRobotButton.setText(
            QCoreApplication.translate("MainWindow", "Enable Robot", None)
        )
        self.ConfirmackButton.setText(
            QCoreApplication.translate("MainWindow", "Acknowledge", None)
        )
        self.CloseButton.setText(
            QCoreApplication.translate("MainWindow", "Abort/Close", None)
        )
        self.MarkingButton.setText(
            QCoreApplication.translate("MainWindow", "Back to Marking", None)
        )
        self.SettingButton.setText(
            QCoreApplication.translate("MainWindow", "Setting", None)
        )
