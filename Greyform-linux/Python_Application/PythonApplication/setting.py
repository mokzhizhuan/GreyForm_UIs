from PyQt5 import QtCore, QtWidgets, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PythonApplication.serveraddress as server
import PythonApplication.reset as closewindow
import socket
from PyQt5.QtNetwork import QTcpServer, QHostAddress
import PythonApplication.login as Login
import netifaces as ni

def get_ethernet_ip():
    """ Get the IP address of the Ethernet interface """
    interfaces = ni.interfaces()
    for interface in interfaces:
        if 'eth' in interface:  # Typical naming for Ethernet interfaces
            addrs = ni.ifaddresses(interface)
            # Check for IPv4 configuration
            if ni.AF_INET in addrs:
                ipv4_info = addrs[ni.AF_INET][0]
                ip_address = ipv4_info.get('addr')
                if ip_address:
                    return ip_address
    return 'No Ethernet IP Found'

class Setting(QWidget):
    def __init__(self, stackedwidgetpage, MainWindow):
        super(Setting, self).__init__()
        self.stackedWidget = stackedwidgetpage
        self.settingform = uic.loadUi("UI_Design/setting.ui", self)
        self.MainWindow = MainWindow
        self.setupUi()

    # setup ui setting from the page
    def setupUi(self):
        self.interface_label = QLabel(self.settingform.wifipage)
        self.interface_label.setGeometry(10, 10, 400, 40)

        self.settingform.maintitlelabel.show()
        self.settingform.maintitlelabel.setText("Home Setting")

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

        self.port.setGeometry(10, 60, 400, 40)
        self.accountinfo = [{"UserID": "admin", "Pass": "pass"}]
        self.userlabel = QLabel(self.settingform.UserPage)
        self.userlabel.setGeometry(10, 10, 400, 40)

        self.file = []
        self.loginwidget = QtWidgets.QStackedWidget(self.settingform.UserPage)
        loginwindow = Login.Login(
            self.accountinfo, self.loginwidget, self.userlabel, self.file
        )
        self.loginwidget.addWidget(loginwindow)
        self.loginwidget.setGeometry(10, 70, 700, 800)

        self.restartwidgetwindow = closewindow.RestartCloseWidget(self.MainWindow)
        self.restartwidgetwindow.show()
        self.restartwidget = QtWidgets.QStackedWidget(
            self.settingform.RestartPowerOffPage
        )
        self.restartwidget.addWidget(self.restartwidgetwindow)
        self.restartwidget.setGeometry(150, 460, 300, 200)
        self.button_UI()
        self.retranslateUi()

    def button_UI(self):
        self.settingform.MarkingbackButton.clicked.connect(
            lambda: self.settingform.stackedWidgetsetting.setCurrentIndex(0)
        )
        self.settingform.MarkingbackButton.clicked.connect(self.homepages)
        self.settingform.MarkingbackButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(4)
        )
        self.settingform.WifiButton.clicked.connect(
            lambda: self.settingform.stackedWidgetsetting.setCurrentIndex(1)
        )

        self.settingform.WifiButton.clicked.connect(self.wifipages)
        self.settingform.serviceIPAddressButton.clicked.connect(
            lambda: self.settingform.stackedWidgetsetting.setCurrentIndex(2)
        )
        self.settingform.serviceIPAddressButton.clicked.connect(
            self.serviceIPAddresspages
        )
        self.settingform.ServicesButton.clicked.connect(
            lambda: self.settingform.stackedWidgetsetting.setCurrentIndex(3)
        )
        self.settingform.ServicesButton.clicked.connect(self.Servicespages)
        self.settingform.UserButton.clicked.connect(
            lambda: self.settingform.stackedWidgetsetting.setCurrentIndex(4)
        )
        self.settingform.UserButton.clicked.connect(self.Userpages)
        self.settingform.AboutButton.clicked.connect(
            lambda: self.settingform.stackedWidgetsetting.setCurrentIndex(5)
        )
        self.settingform.AboutButton.clicked.connect(self.Aboutpages)
        self.settingform.PowerButton.clicked.connect(
            lambda: self.settingform.stackedWidgetsetting.setCurrentIndex(6)
        )
        self.settingform.PowerButton.clicked.connect(self.Powerpages)

    def homepages(self):
        self.settingform.maintitlelabel.show()
        self.settingform.maintitlelabel.setText("Home Setting")

    def wifipages(self):
        self.settingform.maintitlelabel.show()
        self.settingform.maintitlelabel.setText("Wifi Setting")

    def serviceIPAddresspages(self):
        self.settingform.maintitlelabel.show()
        self.settingform.maintitlelabel.setText("Services IP Address Setting")

    def Servicespages(self):
        self.settingform.maintitlelabel.show()
        self.settingform.maintitlelabel.setText("Services Setting")

    def Userpages(self):
        self.settingform.maintitlelabel.show()
        self.settingform.maintitlelabel.setText(
            "User Administration Localization Setting"
        )

    def Aboutpages(self):
        self.settingform.maintitlelabel.show()
        self.settingform.maintitlelabel.setText("About Setting")

    def Powerpages(self):
        self.settingform.maintitlelabel.show()
        self.settingform.maintitlelabel.setText("Power Setting")

    def get_ip_address(self):
        # Get the IP address of the local machine
        ip_address = socket.gethostbyname(socket.gethostname())
        return ip_address

    def retranslateUi(self):
        ip_address = self.get_ip_address()
        ip_address_ethernet = get_ethernet_ip()
        self.interface_label.setStyleSheet("font: 15px")
        self.interface_label.setText(f"Ethernet IP Address: {ip_address}")
        self.ip_label.setText(f"IP Address: {ip_address}")
        self.ip_label.setStyleSheet("font: 15px")
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
        self.userlabel.setText(f"<h2>User: {self.accountinfo[0]['UserID']}</h2>")
