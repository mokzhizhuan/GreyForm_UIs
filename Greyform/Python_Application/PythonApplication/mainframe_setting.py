from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PythonApplication.mainframe_menubutton as buttons_ros
from pywifi import PyWiFi, const
import PythonApplication.serveraddress as server
import PythonApplication.reset as closewindow
import socket
from PyQt5.QtNetwork import QTcpServer, QHostAddress
import PythonApplication.login as Login


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
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 1)
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

        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setObjectName("verticalLayout_11")

        self.horizontalLayout_3.addLayout(self.verticalLayout_11)
        self.interface_label = QLabel(MainWindow)
        self.interface_label.setGeometry(10, 10, 400, 20)
        self.verticalLayout_11.addWidget(self.interface_label)
        self.treeWidget = QTreeWidget(MainWindow)
        self.treeWidget.setHeaderLabels(["SSID", "Signal Strength"])
        self.wifi = PyWiFi()
        self.interface = self.wifi.interfaces()[0]
        self.refreshWiFiList()
        self.verticalLayout_11.addWidget(self.treeWidget)
        self.ip_label = QLabel(MainWindow)
        self.ip_label.setGeometry(10, 10, 380, 80)
        self.ip_label.setAlignment(Qt.AlignCenter)
        self.ip_label.setStyleSheet("font-size: 20px;")

        self.titlelabel = QLabel()
        self.verticalLayout_11.addWidget(self.titlelabel)
        self.titlelabel.hide()

        self.info_label = QLabel()
        self.verticalLayout_11.addWidget(self.info_label)
        self.info_label.hide()

        self.version_label = QLabel()
        self.verticalLayout_11.addWidget(self.version_label)
        self.version_label.hide()

        self.author_label = QLabel()
        self.author_label.hide()

        self.verticalLayout_11.addWidget(self.author_label)
        self.ip_label.hide()
        self.verticalLayout_11.addWidget(self.ip_label)

        self.host = QLabel()
        self.verticalLayout_11.addWidget(self.host)
        self.host.hide()

        self.port = QLabel()
        self.verticalLayout_11.addWidget(self.port)
        self.port.hide()

        self.accountinfo = [{"Email": "admin@gmail.com", "Pass": "pass"}]
        self.userlabel = QLabel()
        self.userlabel.hide()
        self.verticalLayout_11.addWidget(self.userlabel)
        self.loginwidget = QtWidgets.QStackedWidget()
        loginwindow = Login.Login(self.accountinfo, self.loginwidget, self.userlabel)
        self.loginwidget.addWidget(loginwindow)
        self.loginwidget.setFixedWidth(480)
        self.loginwidget.setFixedHeight(620)
        self.verticalLayout_11.addWidget(self.loginwidget)
        self.loginwidget.hide()

        self.restartwidget = closewindow.RestartCloseWidget()
        self.verticalLayout_11.addWidget(self.restartwidget)
        self.restartwidget.hide()
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
        self.WifiButton.clicked.connect(self.showwifisetting)
        self.serviceIPAddressButton.clicked.connect(self.showipaddress)
        self.AboutButton.clicked.connect(self.showaboutpage)
        self.PowerButton.clicked.connect(self.showrestartui)
        self.ServicesButton.clicked.connect(self.showservicespage)
        self.UserButton.clicked.connect(self.showuserinfo)

    def showwifisetting(self):
        self.treeWidget.show()
        self.interface_label.show()
        self.ip_label.hide()
        self.titlelabel.hide()
        self.info_label.hide()
        self.version_label.hide()
        self.author_label.hide()
        self.host.hide()
        self.port.hide()
        self.loginwidget.hide()
        self.restartwidget.hide()

    def showipaddress(self):
        self.treeWidget.hide()
        self.interface_label.hide()
        self.ip_label.show()
        self.titlelabel.hide()
        self.info_label.hide()
        self.version_label.hide()
        self.author_label.hide()
        self.host.hide()
        self.port.hide()
        self.userlabel.hide()
        self.loginwidget.hide()
        self.restartwidget.hide()

    def showaboutpage(self):
        self.treeWidget.hide()
        self.interface_label.hide()
        self.ip_label.hide()
        self.titlelabel.show()
        self.info_label.show()
        self.version_label.show()
        self.author_label.show()
        self.host.hide()
        self.port.hide()
        self.userlabel.hide()
        self.loginwidget.hide()
        self.restartwidget.hide()

    def showservicespage(self):
        self.treeWidget.hide()
        self.interface_label.hide()
        self.ip_label.hide()
        self.titlelabel.hide()
        self.info_label.hide()
        self.version_label.hide()
        self.author_label.hide()
        self.host.show()
        self.port.show()
        self.userlabel.hide()
        self.loginwidget.hide()
        self.restartwidget.hide()

    def showuserinfo(self):
        self.treeWidget.hide()
        self.interface_label.hide()
        self.ip_label.hide()
        self.titlelabel.hide()
        self.info_label.hide()
        self.version_label.hide()
        self.author_label.hide()
        self.host.hide()
        self.port.hide()
        self.userlabel.show()
        self.loginwidget.show()
        self.restartwidget.hide()

    def showrestartui(self):
        self.treeWidget.hide()
        self.interface_label.hide()
        self.ip_label.hide()
        self.titlelabel.hide()
        self.info_label.hide()
        self.version_label.hide()
        self.author_label.hide()
        self.host.hide()
        self.port.hide()
        self.userlabel.hide()
        self.loginwidget.hide()
        self.restartwidget.show()

    def refreshWiFiList(self):
        networks = self.interface.scan_results()
        self.treeWidget.clear()
        ssid = networks[0].ssid
        signal_strength = networks[0].signal
        item = QTreeWidgetItem([ssid, str(signal_strength)])
        self.treeWidget.addTopLevelItem(item)

        interface_info = f"Interface: {self.interface.name()}"
        self.interface_label.setText(interface_info)

    def get_ip_address(self):
        # Get the IP address of the local machine
        ip_address = socket.gethostbyname(socket.gethostname())
        return ip_address

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
        ip_address = self.get_ip_address()
        self.ip_label.setText(f"IP Address: {ip_address}")
        self.titlelabel.setText("<h1>About My Application</h1>")
        self.info_label.setText("This is a Robot Marking Application program")
        self.version_label.setText("Version: 1.0")
        self.author_label.setText("Created by Mok Zhi Zhuan")
        servers = server.MyServer()
        self.host.setText(f"Host: {servers.serverAddress().toString()}")
        self.port.setText(f"Port: {servers.serverPort()}")
        self.userlabel.setText(f"<h2>User: {self.accountinfo[0]['Email']}</h2>")
