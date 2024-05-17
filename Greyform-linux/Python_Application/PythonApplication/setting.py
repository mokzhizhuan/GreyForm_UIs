from PyQt5 import QtCore, QtWidgets, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PythonApplication.restoredefault as default
#from pywifi import PyWiFi, const
import PythonApplication.serveraddress as server
import PythonApplication.reset as closewindow
import socket
from PyQt5.QtNetwork import QTcpServer, QHostAddress
import PythonApplication.login as Login
import datetime
import psutil
import os
import pytz
from tzlocal import get_localzone
import subprocess
import re

def get_interface_names():
    try:
        result = subprocess.run(['sudo', 'lshw', '-C', 'network'], capture_output=True, text=True, check=True)
        interface_names = []

        current_interface = None
        is_wireless = False

        for line in result.stdout.split('\n'):
            if line.strip().startswith('*-network'):
                if current_interface and is_wireless:
                    interface_names.append(current_interface)
                current_interface = None
                is_wireless = False
            elif 'logical name:' in line:
                match = re.search(r'logical name: (\S+)', line)
                if match:
                    current_interface = match.group(1)
            elif 'Wireless interface' in line:
                is_wireless = True
        
        if current_interface and is_wireless:
            interface_names.append(current_interface)

        return interface_names
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
        return []

def get_signal_strength(interface):
    try:
        result = subprocess.run(['iwconfig', interface], capture_output=True, text=True, check=True)
        for line in result.stdout.split('\n'):
            if 'Signal level' in line:
                match = re.search(r'Signal level=(-?\d+)', line)
                if match:
                    return match.group(1)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")

    return None

class Setting(QWidget):
    # setting loader
    def __init__(self, stackedwidgetpage, MainWindow):
        super(Setting, self).__init__()
        self.stackedWidget = stackedwidgetpage
        self.settingform = uic.loadUi("UI_Design/setting.ui", self)
        self.MainWindow = MainWindow
        self.accountinfo = [{"UserID": "admin", "Pass": "pass"}]
        self.default_settings = {
            "theme": "Gray",
            "font_size": "15",
            "resolution": "1920 x 1080",
            "timezone": str(get_localzone()),
            "password": "pass",
        }
        self.setupUi()

    # setup ui setting from the page
    def setupUi(self):
        # home
        self.settingform.themebox.currentIndexChanged.connect(self.colorchange)
        result = subprocess.run(['sudo', 'lshw', '-C', 'network'], capture_output=True, text=True, check=True)
        # wifi
        self.settingform.maintitlelabel.setText("<h3>Home Setting</h3>")
        self.interfaces = get_interface_names()
        interface_info = f"Interface: None"
        self.settingform.interface_label.setText(interface_info)
        self.settingform.treeWidget.hide()
        for interface in self.interfaces:
            signal_strength = get_signal_strength(interface)
            if signal_strength:
                ssid = self.interfaces
                item = QTreeWidgetItem([ssid, str(signal_strength)])
                self.settingform.treeWidget.show()
                self.settingform.treeWidget.addTopLevelItem(item)
                interface_info = f"Interface: {self.interfaces[0]}"
                self.settingform.interface_label.setText(interface_info)
        
        # setting host services and resolution
        self.font_size = self.settingform.Text_size.currentText()
        self.font = QFont()
        self.font.setPointSize(int(self.font_size))
        self.settingform.setFont(self.font)
        self.settingform.Text_size.currentIndexChanged[int].connect(self.update_font)
        self.settingform.resolutioncomboBox.currentIndexChanged.connect(
            self.change_resolution
        )
        all_timezones = pytz.all_timezones
        for timezone in all_timezones:
            self.settingform.country.addItem(timezone)
        local_timezone = get_localzone()
        index = self.settingform.country.findText(
            str(local_timezone), Qt.MatchFixedString
        )
        if index >= 0:
            self.settingform.country.setCurrentIndex(index)
        self.settingform.country.currentIndexChanged.connect(self.updateTimeLabel)

        self.userlabel = QLabel(self.settingform.UserPage)
        self.userlabel.setGeometry(10, 10, 400, 40)

        # User info login
        self.file = []
        self.loginwidget = QStackedWidget(self.settingform.UserPage)
        loginwindow = Login.Login(
            self.accountinfo, self.loginwidget, self.userlabel, self.file
        )
        self.loginwidget.addWidget(loginwindow)
        self.loginwidget.setGeometry(10, 70, 700, 800)

        # power and restart
        self.restartwidgetwindow = closewindow.RestartCloseWidget(self.MainWindow)
        self.restartwidgetwindow.show()
        self.restartwidget = QStackedWidget(self.settingform.RestartPowerOffPage)
        self.restartwidget.addWidget(self.restartwidgetwindow)
        self.restartwidget.setGeometry(150, 460, 300, 200)
        self.button_UI()
        self.retranslateUi()

        self.settingform.restoreDefaultsButton.clicked.connect(
            lambda: default.restoredefaultsetting(
                self.accountinfo,
                self.settingform.themebox,
                self.settingform.Text_size,
                self.settingform.resolutioncomboBox,
                self.settingform.country,
                self.default_settings,
                self.settingform.PasslineEdit,
                self.stackedWidget,
                self.MainWindow,
            )
        )

    # button interaction page
    def button_UI(self):
        self.settingform.MarkingbackButton.clicked.connect(
            lambda: self.settingform.stackedWidgetsetting.setCurrentIndex(0)
        )
        self.settingform.MarkingbackButton.clicked.connect(self.homepages)
        self.settingform.MarkingbackButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(4)
        )
        self.settingform.HomeButton.clicked.connect(self.homepages)
        self.settingform.HomeButton.clicked.connect(
            lambda: self.settingform.stackedWidgetsetting.setCurrentIndex(0)
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

    # ui button setting
    def homepages(self):
        self.settingform.maintitlelabel.setText("<h3>Home Setting</h3>")

    def wifipages(self):
        self.settingform.maintitlelabel.setText("<h3>Wifi Setting</h3>")

    def serviceIPAddresspages(self):
        self.settingform.maintitlelabel.setText("<h3>Host Services</h3>")

    def Servicespages(self):
        self.settingform.maintitlelabel.setText(
            "<h3>Services and Resolution Setting</h3>"
        )

    def Userpages(self):
        self.settingform.maintitlelabel.setText(
            "<h3>User Administration Localization Setting</h3>"
        )

    def Aboutpages(self):
        self.settingform.maintitlelabel.setText("<h3>About Setting</h3>")

    def Powerpages(self):
        self.settingform.maintitlelabel.setText("<h3>Power Setting</h3>")

    # detect ip address
    def get_ip_address(self):
        # Get the IP address of the local machine
        ip_address = socket.gethostbyname(socket.gethostname())
        return ip_address

    # add text
    def retranslateUi(self):
        ip_address = self.get_ip_address()
        self.settingform.labeltitlsetting.setText("<h3>Setting</h3>")
        self.settingform.ip_label.setText(f"IP Address: {ip_address}")
        self.settingform.titlelabel.setText("<h3>About My Application</h3>")
        self.settingform.info_label.setText(
            "This is a Robot Marking Application program"
        )
        self.settingform.version_label.setText("Version: 1.0")
        self.settingform.author_label.setText("Created by Mok Zhi Zhuan")
        servers = server.MyServer()
        self.settingform.Portnumipadd.setText(f"Port: {servers.serverPort()}")
        self.settingform.host.setText(f"Host: {servers.serverAddress().toString()}")
        self.settingform.Port.setText(f"Port: {servers.serverPort()}")
        datenow = datetime.datetime.now()
        datetoday = datetime.date.today()
        datetodayformatted = datetoday.strftime("%d/%m/%Y")
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / (1024 * 1024)  # in MB
        self.settingform.Systemtime.setText(
            "Time : " + str(datenow.strftime("%I:%M %p"))
        )
        self.update_time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(5000)  # Trigger every 5000 milliseconds (5 seconds)
        self.settingform.SystemDate.setText(f"Date : {datetodayformatted}")
        self.settingform.SystemMemory.setText(
            f"System Memory Usage : {memory_usage:.2f} MB"
        )
        self.userlabel.setText(f"<h2>User: {self.accountinfo[0]['UserID']}</h2>")
        self.settingform.PasslineEdit.setText(f"{self.accountinfo[0]['Pass']}")
        self.settingform.PasslineEdit.returnPressed.connect(self.changepassfunction)

    def changepassfunction(self):
        password = self.settingform.PasslineEdit.text()
        self.accountinfo[0]["Pass"] = password

    def update_time(self):
        now = datetime.datetime.now()
        formatted_time = now.strftime("%I:%M %p").lstrip("0")
        self.settingform.Systemtime.setText(f"Time : {formatted_time}")

    def updateTimeLabel(self, index):
        selected_time_zone = self.settingform.country.currentText()
        tz = pytz.timezone(selected_time_zone)
        now = datetime.datetime.now(tz)
        formatted_time = now.strftime("%I:%M %p").lstrip("0")
        self.settingform.Systemtime.setText(f"Time : {formatted_time}")

    def update_font(self, index):
        self.font_size = int(self.settingform.Text_size.currentText())
        self.font.setPointSize(self.font_size)
        self.settingform.setFont(self.font)
        self.MainWindow.setFont(self.font)
        self.apply_font_to_widgets(self.settingform, self.font)
        self.apply_font_to_widgets(self.MainWindow, self.font)

    def apply_font_to_widgets(self, parent, font):
        if hasattr(parent, "setFont"):
            parent.setFont(font)
        if hasattr(parent, "children"):
            for child in parent.children():
                self.apply_font_to_widgets(child, font)

    def change_resolution(self, index):
        resolution = self.settingform.resolutioncomboBox.currentText()
        width, height = map(int, resolution.split("x"))
        if width == 1920 and height == 1080:
            self.MainWindow.showMaximized()
        else:
            self.MainWindow.showNormal()
            self.MainWindow.resize(width, height)

    def colorchange(self, index):
        self.color = self.settingform.themebox.currentText()
        if self.color == "White":
            self.MainWindow.setStyleSheet(f"background-color : {self.color}")
        elif self.color == "Gray":
            self.MainWindow.setStyleSheet(self.styleSheet())
        elif self.color == "Black":
            self.MainWindow.setStyleSheet(
                f"color: white; background-color : {self.color}"
            )
        else:
            color = QColorDialog.getColor()
            self.MainWindow.setStyleSheet(f"background-color : {color.name()}")
