from PyQt5 import QtCore, QtWidgets, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pywifi import PyWiFi, const
import PythonApplication.serveraddress as server
import PythonApplication.reset as closewindow
import socket
from PyQt5.QtNetwork import QTcpServer, QHostAddress
import PythonApplication.login as Login


class Setting(QWidget):
    def __init__(self, stackedwidgetpage, MainWindow):
        super(Setting, self).__init__()
        self.stackedWidget = stackedwidgetpage
        self.settingform = uic.loadUi("UI_Design/setting.ui", self)
        self.MainWindow = MainWindow
        self.setupUi()

    def setupUi(self):
        self.interface_label = QLabel(self.settingform.wifipage)
        self.interface_label.setGeometry(10, 10, 400, 40)

        self.treeWidget = QTreeWidget(self.settingform.wifipage)

        self.treeWidget.setGeometry(10, 80, 400, 80)
        self.treeWidget.setHeaderLabels(["SSID", "Signal Strength"])
        self.wifi = PyWiFi()
        self.interface = self.wifi.interfaces()[0]
        self.refreshWiFiList()

        self.ip_label = QLabel(self.settingform.serviceipaddresspage)
        self.ip_label.setGeometry(10, 10, 380, 80)
        self.ip_label.setAlignment(Qt.AlignCenter)
        self.ip_label.setStyleSheet("font-size: 20px;")

        self.titlelabel = QLabel(self.settingform.AboutPage)
        self.titlelabel.setGeometry(10, 10, 400, 40)

        self.info_label = QLabel(self.settingform.AboutPage)
        self.info_label.setGeometry(10, 60, 400, 40)

        self.version_label = QLabel(self.settingform.AboutPage)
        self.version_label.setGeometry(10, 130, 400, 40)

        self.author_label = QLabel(self.settingform.AboutPage)
        self.author_label.setGeometry(10, 190, 400, 40)

        self.host = QLabel(self.settingform.servicespage)
        self.host.setGeometry(10, 10, 400, 40)

        self.port = QLabel(self.settingform.servicespage)

        self.port.setGeometry(10, 60, 400, 20)
        self.accountinfo = [{"Email": "admin@gmail.com", "Pass": "pass"}]
        self.userlabel = QLabel(self.settingform.UserPage)
        self.userlabel.setGeometry(10, 10, 400, 40)

        self.loginwidget = QtWidgets.QStackedWidget(self.settingform.UserPage)
        loginwindow = Login.Login(self.accountinfo, self.loginwidget, self.userlabel)
        self.loginwidget.addWidget(loginwindow)
        self.loginwidget.setGeometry(10, 70, 480, 620)

        self.restartwidgetwindow = closewindow.RestartCloseWidget(self.MainWindow)
        self.restartwidget = QtWidgets.QStackedWidget(
            self.settingform.RestartPowerOffPage
        )
        self.restartwidget.addWidget(self.restartwidgetwindow)
        self.button_UI()
        self.retranslateUi()

    def button_UI(self):
        self.settingform.MarkingbackButton.clicked.connect(
            lambda: self.settingform.stackedWidgetsetting.setCurrentIndex(0)
        )
        self.settingform.MarkingbackButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(4)
        )
        self.settingform.WifiButton.clicked.connect(
            lambda: self.settingform.stackedWidgetsetting.setCurrentIndex(1)
        )
        self.settingform.serviceIPAddressButton.clicked.connect(
            lambda: self.settingform.stackedWidgetsetting.setCurrentIndex(2)
        )
        self.settingform.ServicesButton.clicked.connect(
            lambda: self.settingform.stackedWidgetsetting.setCurrentIndex(3)
        )
        self.settingform.UserButton.clicked.connect(
            lambda: self.settingform.stackedWidgetsetting.setCurrentIndex(4)
        )
        self.settingform.AboutButton.clicked.connect(
            lambda: self.settingform.stackedWidgetsetting.setCurrentIndex(5)
        )
        self.settingform.PowerButton.clicked.connect(
            lambda: self.settingform.stackedWidgetsetting.setCurrentIndex(6)
        )

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

    def retranslateUi(self):
        ip_address = self.get_ip_address()
        self.interface_label.setStyleSheet("font: 15px")
        self.ip_label.setText(f"IP Address: {ip_address}")
        self.titlelabel.setText("<h1>About My Application</h1>")
        self.info_label.setText("This is a Robot Marking Application program")
        self.info_label.setStyleSheet("font: 15px")
        self.version_label.setText("Version: 1.0")
        self.version_label.setStyleSheet("font: 15px")
        self.author_label.setText("Created by Mok Zhi Zhuan")
        self.author_label.setStyleSheet("font: 15px")
        servers = server.MyServer()
        self.host.setText(f"Host: {servers.serverAddress().toString()}")
        self.host.setStyleSheet("font: 15px")
        self.port.setText(f"Port: {servers.serverPort()}")
        self.port.setStyleSheet("font: 15px")
        self.userlabel.setText(f"<h2>User: {self.accountinfo[0]['Email']}</h2>")
