from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PythonApplication.mainframe_menubutton as buttons_ros


# main frame part 5 setting
class Ui_MainWindow(object):
    def __init__(self, stackedwidgetpage, MainWindow):
        self.stackedWidget = stackedwidgetpage
        self.setupUi_Page5(MainWindow)

    def setupUi_Page5(self, MainWindow):
        self.settingpage = QWidget()
        self.settingpage.setObjectName("settingpage")
        self.verticalLayoutWidget_2 = QWidget(self.settingpage)
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(60, 30, 1721, 941))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setSpacing(7)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.labelsetting = QLabel(self.verticalLayoutWidget_2)
        self.labelsetting.setObjectName("label")
        sizePolicy3 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(
            self.labelsetting.sizePolicy().hasHeightForWidth()
        )
        self.labelsetting.setSizePolicy(sizePolicy3)
        font3 = QFont()
        font3.setPointSize(20)
        font3.setBold(True)
        font3.setWeight(75)
        self.labelsetting.setFont(font3)
        self.labelsetting.setTextFormat(Qt.AutoText)
        self.labelsetting.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.labelsetting)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.WifiButton = QPushButton(self.verticalLayoutWidget_2)
        self.WifiButton.setObjectName("WifiButton")
        sizePolicy4 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.WifiButton.sizePolicy().hasHeightForWidth())
        self.WifiButton.setSizePolicy(sizePolicy4)

        self.verticalLayout_4.addWidget(self.WifiButton)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.serviceIPAddressButton = QPushButton(self.verticalLayoutWidget_2)
        self.serviceIPAddressButton.setObjectName("serviceIPAddressButton")

        self.verticalLayout_5.addWidget(self.serviceIPAddressButton)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.ServicesButton = QPushButton(self.verticalLayoutWidget_2)
        self.ServicesButton.setObjectName("ServicesButton")

        self.verticalLayout_6.addWidget(self.ServicesButton)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.UserButton = QPushButton(self.verticalLayoutWidget_2)
        self.UserButton.setObjectName("UserButton")

        self.verticalLayout_3.addWidget(self.UserButton)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.PowerButton = QPushButton(self.verticalLayoutWidget_2)
        self.PowerButton.setObjectName("PowerButton")

        self.verticalLayout_7.addWidget(self.PowerButton)

        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.AboutButton = QPushButton(self.verticalLayoutWidget_2)
        self.AboutButton.setObjectName("AboutButton")

        self.verticalLayout_8.addWidget(self.AboutButton)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.MarkingButton = QPushButton(self.verticalLayoutWidget_2)
        self.MarkingButton.setObjectName("MarkingButton_2")

        self.verticalLayout_9.addWidget(self.MarkingButton)

        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")

        self.verticalLayout_9.addLayout(self.verticalLayout_10)

        self.verticalLayout_8.addLayout(self.verticalLayout_9)

        self.verticalLayout_7.addLayout(self.verticalLayout_8)

        self.verticalLayout_3.addLayout(self.verticalLayout_7)

        self.verticalLayout_6.addLayout(self.verticalLayout_3)

        self.verticalLayout_5.addLayout(self.verticalLayout_6)

        self.verticalLayout_4.addLayout(self.verticalLayout_5)

        self.horizontalLayout_3.addLayout(self.verticalLayout_4)

        self.label_3 = QLabel(self.verticalLayoutWidget_2)
        self.label_3.setObjectName("label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.verticalLayout_2.setStretch(1, 1)
        self.stackedWidget.addWidget(self.settingpage)
        self.button_UI(MainWindow)
        self.finalizeUI(MainWindow)

    def finalizeUI(self, MainWindow):
        self.retranslateUi(MainWindow)

    def button_UI(self, MainWindow):
        self.MarkingButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(4)
        )

    def retranslateUi(self, MainWindow):
        self.labelsetting.setText(
            QCoreApplication.translate("MainWindow", "Settings", None)
        )
        self.WifiButton.setText(QCoreApplication.translate("MainWindow", "Wifi", None))
        self.serviceIPAddressButton.setText(
            QCoreApplication.translate("MainWindow", "Service IP Address", None)
        )
        self.ServicesButton.setText(
            QCoreApplication.translate("MainWindow", "Services", None)
        )
        self.UserButton.setText(QCoreApplication.translate("MainWindow", "User", None))
        self.PowerButton.setText(
            QCoreApplication.translate("MainWindow", "Power/ShutDown/Restart", None)
        )
        self.AboutButton.setText(
            QCoreApplication.translate("MainWindow", "About", None)
        )
        self.MarkingButton.setText(
            QCoreApplication.translate("MainWindow", "Back to Marking Menu", None)
        )
        self.label_3.setText("")
