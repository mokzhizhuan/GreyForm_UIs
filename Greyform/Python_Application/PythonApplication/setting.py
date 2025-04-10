from PyQt5 import QtCore, QtWidgets, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PythonApplication.restoredefault as default
import PythonApplication.wifiset as wifisetup
from pywifi import PyWiFi, const
import PythonApplication.reset as closewindow
from PyQt5.QtNetwork import QTcpServer, QHostAddress
import PythonApplication.login as Login
import PythonApplication.settinglayout as settinglayoutUi
import PythonApplication.settingbuttoninteraction as settingbuttonUIinteraction
import PythonApplication.settingtext as settingtextlayout
import pytz
import psutil
import os


# setting page
class Setting(QWidget):
    # setting loader
    def __init__(
        self,
        stackedwidgetpage,
        MainWindow,
        windowwidth,
        windowheight,
        default_settings,
        stackedWidget_main,
    ):
        # starting initialize
        super(Setting, self).__init__()
        self.stackedWidget = stackedwidgetpage
        self.windowwidth = windowwidth
        self.windowheight = windowheight
        self.settingform = uic.loadUi("UI_Design/setting.ui", self)
        self.MainWindow = MainWindow
        self.accountinfo = [{"UserID": "admin", "Pass": "pass"}]
        font = default_settings["font_size"]
        self.theme = default_settings["theme"]
        self.password = default_settings["password"]
        self.font_size = int(font)
        self.selected_time_zone = default_settings["timezone"]
        self.default_settings = default_settings
        self.saved_setting = self.default_settings
        self.stackedWidget_main = stackedWidget_main
        self.setupUi()

    # setup ui setting from the page
    def setupUi(self):
        self.button_UI()
        # home
        self.settingform.themebox.currentIndexChanged.connect(self.colorchange)
        self.settingform.maintitlelabel.setText("<h3>Home Setting</h3>")
        # wifi
        self.settingform.treeWidget.setColumnWidth(0, 500)
        self.refreshWiFiList()
        # setting host services and resolution
        Text_index = self.settingform.Text_size.findText(
            str(self.default_settings["font_size"]), Qt.MatchFixedString
        )
        if Text_index >= 0:
            self.settingform.Text_size.setCurrentIndex(Text_index)
        self.font = QFont()
        self.font.setPointSize(int(self.font_size))
        self.apply_font_to_widgets(self.settingform, self.font)
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
        timezone_index = self.settingform.country.findText(
            self.selected_time_zone, Qt.MatchFixedString
        )
        if timezone_index >= 0:
            self.settingform.country.setCurrentIndex(timezone_index)
        self.settingform.country.currentIndexChanged.connect(self.updateTimeLabel)
        self.userlabel = QLabel(self.settingform.UserPage)
        self.userlabel.setFont(self.font)
        # User info login
        self.file = []
        self.loginwidget = QStackedWidget(self.settingform.UserPage)
        self.loginwindow = Login.Login(
            self.accountinfo,
            self.loginwidget,
            self.userlabel,
            self.file,
            self.settingform.UserPage,
        )
        self.loginwidget.addWidget(self.loginwindow)
        # power and restart
        self.restartwidgetwindow = closewindow.RestartCloseWidget(
            self.MainWindow,
            self.saved_setting,
            self.settingform.themebox,
            self.settingform.Text_size,
            self.settingform.resolutioncomboBox,
            self.settingform.country,
            self.font_size,
            self.password,
        )
        self.restartwidgetwindow.show()
        self.restartwidget = QStackedWidget(self.settingform.RestartPowerOffPage)
        self.restartwidget.addWidget(self.restartwidgetwindow)
        self.restartwidget.setGeometry(50, 260, 300, 200)
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
                self.stackedWidget_main,
            )
        )

    # button interaction page
    def button_UI(self):
        self.settingbutton = settingbuttonUIinteraction.settingbuttonUI(
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
            self.stackedWidget_main,
        )

    # detect WIFI
    def refreshWiFiList(self):
        """wifisetup.setup_wifi(
            self.settingform.treeWidget, self.settingform.interface_label
        )"""

    # add text
    def retranslateUi(self):
        self.update_time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_memory()
        self.memorytimer = QTimer(self)
        self.memorytimer.timeout.connect(self.update_memory)
        self.memorytimer.start(1000)
        settingtextlayout.SettingText(
            self.settingform.labeltitlsetting,
            self.settingform.ip_label,
            self.settingform.titlelabel,
            self.settingform.info_label,
            self.settingform.version_label,
            self.settingform.author_label,
            self.settingform.Portnumipadd,
            self.settingform.host,
            self.settingform.SystemDate,
            self.settingform.PasslineEdit,
            self.userlabel,
            self.accountinfo,
        )

    #memeory implementation
    def update_memory(self):
        # Update the system memory text
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / (1024 * 1024)  # in MB
        self.settingform.SystemMemory.setText(
            f"System Memory Usage : {memory_usage:.2f} MB"
        )

    # set time in am/pm format
    def update_time(self):
        self.settingbutton.updatingtime(
            self.selected_time_zone, self.settingform.Systemtime
        )

    def updateTimeLabel(self, index):
        self.selected_time_zone = self.settingform.country.currentText()
        self.settingbutton.updatingtime(
            self.selected_time_zone, self.settingform.Systemtime
        )

    #font implementation
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

    #resolution set
    def change_resolution(self, index):
        resolution = self.settingform.resolutioncomboBox.currentText()
        width, height = map(int, resolution.split("x"))
        if width == 1920 and height == 1080:
            self.MainWindow.showMaximized()
        else:
            self.MainWindow.showNormal()
            self.MainWindow.resize(width, height)

    #color background change implementation
    def colorchange(self, index):
        self.color = self.settingform.themebox.currentText()
        if self.color == "Light":
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

    #setting layout
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
