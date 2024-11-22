from PyQt5 import uic 
from PyQt5.QtWidgets import QWidget, QLabel, QStackedWidget, QColorDialog, QPushButton 
from PyQt5.QtCore import QTimer, Qt 
from PyQt5.QtGui import QFont , QColor
import PythonApplication.restoredefault as default
import PythonApplication.reset as closewindow
import PythonApplication.login as Login
import PythonApplication.interfacesignal as interface_signals
import PythonApplication.settinglayout as settinglayoutUi
import PythonApplication.settingbuttoninteraction as settingbuttonUIinteraction
import PythonApplication.settingtext as settingtextlayout
import pytz
import psutil
import os
import re


class Setting(QWidget):
    def __init__(
        self,
        stackedwidgetpage,
        MainWindow,
        centralwidget,
        windowwidth,
        windowheight,
        default_settings,
        stackedWidget_main,
    ):
        super(Setting, self).__init__()
        self.init_variables(
            stackedwidgetpage,
            MainWindow,
            centralwidget,
            windowwidth,
            windowheight,
            default_settings,
            stackedWidget_main,
        )
        self.settingform = uic.loadUi("UI_Design/setting.ui", self)
        self.setupUi()
        self.retranslateUi()

    def init_variables(
        self,
        stackedwidgetpage,
        MainWindow,
        centralwidget,
        windowwidth,
        windowheight,
        default_settings,
        stackedWidget_main,
    ):
        self.stackedWidget, self.MainWindow, self.centralwidget = (
            stackedwidgetpage,
            MainWindow,
            centralwidget,
        )
        self.windowwidth, self.windowheight, self.stackedWidget_main = (
            windowwidth,
            windowheight,
            stackedWidget_main,
        )
        self.default_settings = self.saved_setting = default_settings
        self.font_size = int(default_settings["font_size"])
        self.selected_time_zone = default_settings["timezone"]
        self.accountinfo = [{"UserID": "admin", "Pass": "pass"}]
        self.font = QFont()
        self.font.setPointSize(self.font_size)
        self.colors = {
            "theme": default_settings["themeothercolor"],
            "text": default_settings["text_labelothercolor"],
            "button": default_settings["buttonthemeothercolor"],
            "button_text": default_settings["buttontextothercolor"],
        }

    def setupUi(self):
        self.button_UI()
        self.load_UIsettings()
        self.init_interface_settings()
        self.setup_font_and_resolution()
        self.setup_timezone_selection()
        self.setup_user_login()
        self.setup_restart_widget()
        self.init_timers()
        self.setup_text_and_layout()
        self.connect_events()

    def load_UIsettings(self):
        settings_map = {
            "theme": (self.themebox, "themeothercolor", "theme"),
            "text_label": (self.themetextbox, "text_labelothercolor", "text"),
            "buttontheme": (self.buttonthemebox, "buttonthemeothercolor", "button"),
            "buttontext": (self.buttonthemetextbox, "buttontextothercolor", "button_text"),
        }
        for key, (combobox, other_key, color_key) in settings_map.items():
            predefined_value = self.default_settings.get(key, "Gray" if "theme" in key else "Black")
            other_color = self.default_settings.get(other_key, "")

            if predefined_value == "Other Color " and other_color:
                self.colors[color_key] = other_color
                self.apply_color_to_widgets(color_key)
                
            else:
                combobox.setCurrentText(predefined_value)
        self.apply_color_to_widgets("theme")
        self.apply_color_to_widgets("text")
        self.apply_color_to_widgets("button")
        self.apply_color_to_widgets("button_text")

    def init_interface_settings(self):
        interface_name, ip_address, host, ports_text = (
            interface_signals.get_active_wifi_interface()
        )
        self.set_interface_labels(interface_name, ip_address, host, ports_text)
        interfaces = interface_signals.get_wireless_interfaces()
        interface_signals.show_interface(interfaces, self.settingform.treeWidget)
        self.settingform.treeWidget.itemClicked.connect(self.ethernet_item_clicked)


    def setup_font_and_resolution(self):
        self.settingform.Text_size.setCurrentText(str(self.font_size))
        self.apply_font_to_widgets(self.settingform, self.font)
        self.settingform.resolutioncomboBox.setCurrentText(
            self.default_settings["resolution"]
        )

    def setup_timezone_selection(self):
        self.settingform.country.addItems(pytz.all_timezones)
        self.settingform.country.setCurrentText(self.selected_time_zone)

    def setup_user_login(self):
        self.userlabel = QLabel(self.settingform.UserPage)
        self.loginwidget = QStackedWidget(self.settingform.UserPage)
        login_window = Login.Login(
            self.accountinfo,
            self.loginwidget,
            self.userlabel,
            self.settingform.UserPage,
        )
        self.loginwidget.addWidget(login_window)
        self.loginwidget.setGeometry(10, 70, 700, 800)

    def setup_restart_widget(self):
        self.restartwidget = QStackedWidget(self.settingform.RestartPowerOffPage)
        self.restartwidget.addWidget(
            closewindow.RestartCloseWidget(
                self.MainWindow,
                self.saved_setting,
                self.settingform.themebox,
                self.settingform.themetextbox,
                self.settingform.buttonthemebox,
                self.settingform.buttonthemetextbox,
                self.settingform.Text_size,
                self.settingform.resolutioncomboBox,
                self.settingform.country,
                self.font_size,
                self.default_settings["password"],
            )
        )
        self.restartwidget.setGeometry(150, 460, 300, 300)

    def retranslateUi(self):
        self.update_time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Trigger every 5000 milliseconds (5 seconds)
        self.update_memory()
        self.memorytimer = QTimer(self)
        self.memorytimer.timeout.connect(self.update_memory)
        self.memorytimer.start(1000)
        settingtextlayout.SettingText(
            self.settingform.labeltitlsetting,
            self.settingform.titlelabel,
            self.settingform.info_label,
            self.settingform.version_label,
            self.settingform.author_label,
            self.settingform.SystemDate,
            self.settingform.SystemMemory,
            self.settingform.PasslineEdit,
            self.userlabel,
            self.accountinfo,
        )

    def update_time(self):
        self.settingbutton.updatingtime(
            self.selected_time_zone, self.settingform.Systemtime
        )

    def updateTimeLabel(self, index):
        self.selected_time_zone = self.settingform.country.currentText()
        self.settingbutton.updatingtime(
            self.selected_time_zone, self.settingform.Systemtime
        )

    # update memory
    def update_memory(self):
        # Update the system memory text
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / (1024 * 1024)  # in MB
        self.settingform.SystemMemory.setText(
            f"System Memory Usage : {memory_usage:.2f} MB"
        )

    def init_timers(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.memorytimer = QTimer(self)
        self.memorytimer.timeout.connect(self.update_memory)
        self.memorytimer.start(1000)

    def setup_text_and_layout(self):
        settinglayoutUi.SettingLayout(
            self.settingform,
            self.settingform.labeltitlsetting,
            self.settingform.settinglayoutWidget,
            self.settingform.layoutWidgethome,
            self.settingform.layoutWidgethome_2,
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
            self.settingform.horizontalLayoutWidgetspeed,
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

    def connect_events(self):
        self.settingform.themebox.currentIndexChanged.connect(
            lambda: self.update_color("theme")
        )
        self.settingform.themetextbox.currentIndexChanged.connect(
            lambda: self.update_color("text")
        )
        self.settingform.buttonthemebox.currentIndexChanged.connect(
            lambda: self.update_color("button")
        )
        self.settingform.buttonthemetextbox.currentIndexChanged.connect(
            lambda: self.update_color("button_text")
        )
        self.settingform.restoreDefaultsButton.clicked.connect(
            lambda: default.restoredefaultsetting(
                self.accountinfo,
                self.settingform.themebox,
                self.settingform.themetextbox,
                self.settingform.buttonthemebox,
                self.settingform.buttonthemetextbox,
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
            self.settingform.themetextbox,
            self.settingform.buttonthemebox,
            self.settingform.buttonthemetextbox,
            self.settingform.Text_size,
            self.settingform.resolutioncomboBox,
            self.settingform.country,
            self.settingform.PasslineEdit,
            self.MainWindow,
            self.saved_setting,
            self.stackedWidget_main,
            self.colors,
        )

    def ethernet_item_clicked(self, item, column):
        interface_name = item.text(column)
        interface_info, ip_address, host, ports_text = interface_signals.get_interface(
            self.interfaces, interface_name
        )
        self.set_interface_labels(interface_info, ip_address, host, ports_text)

    def set_interface_labels(self, interface_info, ip_address, host, ports_text):
        self.settingform.interface_label.setText(interface_info)
        self.settingform.ip_label.setText(f"IP Address: {ip_address}")
        self.settingform.host.setText(f"Host: {host}")
        self.settingform.Portnumipadd.setText(f"Port: {ports_text}")

    def update_color(self, element):
        element_to_box = {
            "theme": self.settingform.themebox,
            "text": self.settingform.themetextbox,
            "button": self.settingform.buttonthemebox,
            "button_text": self.settingform.buttonthemetextbox,
        }
        box = element_to_box.get(element)
        if not box:
            raise ValueError(f"Unknown element: {element}")
        if "Other Color" in box.currentText():
            selected_color = QColorDialog.getColor()
            if selected_color.isValid():
                self.colors[element] = selected_color.name()
        else:
            self.colors[element] = box.currentText()
        self.apply_color_to_widgets(element)

    def apply_color_to_widgets(self, element):
        if element == "theme":
            self.MainWindow.setStyleSheet(f"background-color: {self.colors[element]}")
            self.settingform.setStyleSheet(f"background-color: {self.colors[element]}")
        elif element == "text":
            for child in self.centralwidget.findChildren(QLabel):
                child.setStyleSheet(f"color: {self.colors[element]}")
            for child in self.settingform.centralwidget.findChildren(QLabel):
                child.setStyleSheet(f"color: {self.colors[element]}")
        elif element == "button":
            for child in self.centralwidget.findChildren(QPushButton):
                current_style = child.styleSheet()
                text_color = self.extract_style_property(current_style, "color")
                child.setStyleSheet(
                    f"background-color: {self.colors[element]}; color: {text_color or 'black'};"
                )
            for child in self.settingform.centralwidget.findChildren(QPushButton):
                current_style = child.styleSheet()
                text_color = self.extract_style_property(current_style, "color")
                child.setStyleSheet(
                    f"background-color: {self.colors[element]}; color: {text_color or 'black'};"
                )
        elif element == "button_text":
            for child in self.centralwidget.findChildren(QPushButton):
                current_style = child.styleSheet()
                background_color = self.extract_style_property(
                    current_style, "background-color"
                )
                child.setStyleSheet(
                    f"background-color: {background_color or 'default'}; color: {self.colors[element]};"
                )
            for child in self.settingform.centralwidget.findChildren(QPushButton):
                current_style = child.styleSheet()
                background_color = self.extract_style_property(
                    current_style, "background-color"
                )
                child.setStyleSheet(
                    f"background-color: {background_color or 'default'}; color: {self.colors[element]};"
                )

    def extract_style_property(self, style, property_name):
        pattern = rf"{property_name}\s*:\s*([^;]+);"
        match = re.search(pattern, style)
        return match.group(1).strip() if match else None

    def update_time(self):
        self.settingbutton.updatingtime(
            self.selected_time_zone, self.settingform.Systemtime
        )

    def update_memory(self):
        memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
        self.settingform.SystemMemory.setText(
            f"System Memory Usage: {memory_usage:.2f} MB"
        )

    def apply_font_to_widgets(self, parent, font):
        parent.setFont(font)
        for child in parent.findChildren(QWidget):
            child.setFont(font)
