from PyQt5 import QtCore, QtWidgets, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PythonApplication.restoredefault as default
import PythonApplication.serveraddress as server
import PythonApplication.reset as closewindow
import socket
from PyQt5.QtNetwork import QTcpServer, QHostAddress
import PythonApplication.login as Login
import PythonApplication.interfacesignal as interface_signals
import PythonApplication.settinglayout as settinglayoutUi
import PythonApplication.settingbuttoninteraction as settingbuttonUIinteraction
import PythonApplication.settingtext as settingtextlayout
import datetime
import psutil
import os
import pytz
from tzlocal import get_localzone

# setting loader
class Setting(QWidget):
    def __init__(
        self,
        stackedwidgetpage,
        MainWindow,
        windowwidth,
        windowheight,
        settingButton,
        stackedWidget_main,
    ):
        super(Setting, self).__init__()
        self.stackedWidget = stackedwidgetpage
        self.windowwidth = windowwidth
        self.windowheight = windowheight
        self.settingform = uic.loadUi("UI_Design/setting.ui", self)
        self.MainWindow = MainWindow
        self.accountinfo = [{"UserID": "admin", "Pass": "pass"}]
        self.default_settings = {
            "theme": "Gray",
            "font_size": "15",
            "resolution": f"{windowwidth} x {windowheight}",
            "timezone": str(get_localzone()),
            "password": "pass",
        }
        self.saved_setting = {
            "theme": "Gray",
            "font_size": "15",
            "resolution": f"{windowwidth} x {windowheight}",
            "timezone": str(get_localzone()),
            "password": "pass",
        }
        self.settingButton = settingButton
        self.stackedWidget_main = stackedWidget_main
        self.setupUi()

    # setup ui setting from the page
    def setupUi(self):
        # home
        self.settingform.themebox.currentIndexChanged.connect(self.colorchange)
        # wifi
        self.settingform.maintitlelabel.setText("<h3>Home Setting</h3>")
        self.interfaces = interface_signals.get_wireless_interfaces()
        interface_info = f"Interface: None"
        self.settingform.interface_label.setText(interface_info)
        self.settingform.treeWidget.hide()
        for interface in self.interfaces:
            signal_strength = interface_signals.get_signal_strength(interface)
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
        resolution_index = self.settingform.resolutioncomboBox.findText(
            self.default_settings["resolution"], Qt.MatchFixedString
        )
        if resolution_index >= 0:
            self.settingform.resolutioncomboBox.setCurrentIndex(resolution_index)
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
            self.accountinfo,
            self.loginwidget,
            self.userlabel,
            self.file,
            self.settingform.UserPage,
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
        self.setStretch()
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
                self.windowwidth,
                self.windowheight,
            )
        )

    # button interaction page
    def button_UI(self):
        settingbuttonUIinteraction.settingbuttonUI(
            self.settingform.MarkingbackButton,
            self.settingform.stackedWidgetsetting,
            self.stackedWidget,
            self.settingform.HomeButton,
            self.settingform.WifiButton,
            self.settingform.serviceIPAddressButton,
            self.settingform.ServicesButton,
            self.settingform.UserButton,
            self.settingform.AboutButton,
            self.settingform.PowerButton,
            self.settingform.maintitlelabel,
            self.settingform.themebox,
            self.settingform.Text_size,
            self.settingform.resolutioncomboBox,
            self.settingform.country,
            self.settingform.PasslineEdit,
            self.MainWindow,
            self.saved_setting,
            self.settingButton,
            self.stackedWidget_main,
        )

    # add text
    def retranslateUi(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(5000)  # Trigger every 5000 milliseconds (5 seconds)
        settingtextlayout.SettingText(
            self.settingform.labeltitlsetting,
            self.settingform.ip_label,
            self.settingform.titlelabel,
            self.settingform.info_label,
            self.settingform.version_label,
            self.settingform.author_label,
            self.settingform.Portnumipadd,
            self.settingform.host,
            self.settingform.Port,
            self.settingform.SystemDate,
            self.settingform.SystemMemory,
            self.settingform.PasslineEdit,
            self.userlabel,
            self.accountinfo,
        )

    def changepassfunction(self):
        password = self.settingform.PasslineEdit.text()
        self.accountinfo[0]["Pass"] = password

    def update_time(self):
        now = datetime.datetime.now()
        formatted_time = now.strftime("%I:%M %p").lstrip("0")
        if "AM" not in formatted_time and "PM" not in formatted_time:
            am_pm = "AM" if now.hour < 12 else "PM"
            formatted_time = now.strftime("%I:%M ").lstrip("0") + am_pm
        self.settingform.Systemtime.setText(f"Time : {formatted_time}")

    def updateTimeLabel(self, index):
        selected_time_zone = self.settingform.country.currentText()
        tz = pytz.timezone(selected_time_zone)
        now = datetime.datetime.now(tz)
        formatted_time = now.strftime("%I:%M %p").lstrip("0")
        if "AM" not in formatted_time and "PM" not in formatted_time:
            am_pm = "AM" if now.hour < 12 else "PM"
            formatted_time = now.strftime("%I:%M ").lstrip("0") + am_pm
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

    def setStretch(self):
        settinglayoutUi.SettingLayout(
            self.settingform,
            self.settingform.labeltitlsetting,
            self.settingform.settinglayoutWidget,
            self.settingform.layoutWidgethome,
            self.settingform.restoreDefaultsButton,
            self.settingform.settingHomepage,
            self.settingform.interface_label,
            self.settingform.treeWidget,
            self.settingform.wifipage,
            self.settingform.ip_label,
            self.settingform.Portnumipadd,
            self.settingform.serviceipaddresspage,
            self.settingform.layoutWidgetservicestextsize,
            self.settingform.host,
            self.settingform.layoutWidgetservicesresolution,
            self.settingform.layoutWidgetservicescountryGMT,
            self.settingform.layoutWidgetservicessetpass,
            self.settingform.SystemDate,
            self.settingform.Systemtime,
            self.settingform.SystemMemory,
            self.settingform.Port,
            self.settingform.servicespage,
            self.userlabel,
            self.loginwidget,
            self.settingform.UserPage,
            self.settingform.version_label,
            self.settingform.titlelabel,
            self.settingform.author_label,
            self.settingform.info_label,
            self.settingform.AboutPage,
            self.restartwidget,
            self.settingform.RestartPowerOffPage,
        )
