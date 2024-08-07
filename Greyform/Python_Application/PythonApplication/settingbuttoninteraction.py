from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import PythonApplication.savesetting as SaveSettingsDialog
import json
import datetime
import pytz


class settingbuttonUI(object):
    def __init__(
        self,
        MarkingbackButton,
        stackedWidgetsetting,
        stackedWidget,
        HomeButton,
        WifiButton,
        serviceIPAddressButton,
        ServicesButton,
        UserButton,
        AboutButton,
        PowerButton,
        maintitlelabel,
        themebox,
        fontsizebox,
        resolutionbox,
        timezonebox,
        passwordedit,
        MainWindow,
        saved_setting,
        settingButton,
        stackedWidget_main,
    ):
        self.MarkingbackButton = MarkingbackButton
        self.stackedWidgetsetting = stackedWidgetsetting
        self.stackedWidget = stackedWidget
        self.HomeButton = HomeButton
        self.WifiButton = WifiButton
        self.serviceIPAddressButton = serviceIPAddressButton
        self.ServicesButton = ServicesButton
        self.UserButton = UserButton
        self.AboutButton = AboutButton
        self.PowerButton = PowerButton
        self.maintitlelabel = maintitlelabel
        self.themebox = themebox
        self.fontsizebox = fontsizebox
        self.resolutionbox = resolutionbox
        self.timezonebox = timezonebox
        self.passwordedit = passwordedit
        self.MainWindow = MainWindow
        self.savesettings = saved_setting
        self.windowwidth, self.windowheight = map(
            int, self.savesettings["resolution"].split("x")
        )
        self.stackedWidget_main = stackedWidget_main
        self.button_UI()

    def button_UI(self):
        self.MarkingbackButton.clicked.connect(self.confirm_save_settings)
        self.HomeButton.clicked.connect(self.homepages)
        self.HomeButton.clicked.connect(
            lambda: self.stackedWidgetsetting.setCurrentIndex(0)
        )
        self.WifiButton.clicked.connect(
            lambda: self.stackedWidgetsetting.setCurrentIndex(1)
        )
        self.WifiButton.clicked.connect(self.wifipages)
        self.serviceIPAddressButton.clicked.connect(
            lambda: self.stackedWidgetsetting.setCurrentIndex(2)
        )
        self.serviceIPAddressButton.clicked.connect(self.serviceIPAddresspages)
        self.ServicesButton.clicked.connect(
            lambda: self.stackedWidgetsetting.setCurrentIndex(3)
        )
        self.ServicesButton.clicked.connect(self.Servicespages)
        self.UserButton.clicked.connect(
            lambda: self.stackedWidgetsetting.setCurrentIndex(4)
        )
        self.UserButton.clicked.connect(self.Userpages)
        self.AboutButton.clicked.connect(
            lambda: self.stackedWidgetsetting.setCurrentIndex(5)
        )
        self.AboutButton.clicked.connect(self.Aboutpages)
        self.PowerButton.clicked.connect(
            lambda: self.stackedWidgetsetting.setCurrentIndex(6)
        )
        self.PowerButton.clicked.connect(self.Powerpages)

    # ui button setting
    def homepages(self):
        self.maintitlelabel.setText("<h3>Home Setting</h3>")

    def wifipages(self):
        self.maintitlelabel.setText("<h3>Wifi Setting</h3>")

    def serviceIPAddresspages(self):
        self.maintitlelabel.setText("<h3>Host Services</h3>")

    def Servicespages(self):
        self.maintitlelabel.setText("<h3>Services and Resolution Setting</h3>")

    def Userpages(self):
        self.maintitlelabel.setText("<h3>User Administration Localization Setting</h3>")

    def Aboutpages(self):
        self.maintitlelabel.setText("<h3>About Setting</h3>")

    def Powerpages(self):
        self.maintitlelabel.setText("<h3>Power Setting</h3>")

    def confirm_save_settings(self):
        dialog = SaveSettingsDialog.SettingsDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.save_settings()

    def save_settings(self):
        self.savesettings = {
            "theme": self.themebox.currentText(),
            "font_size": self.fontsizebox.currentText(),
            "resolution": self.resolutionbox.currentText(),
            "timezone": self.timezonebox.currentText(),
            "password": self.passwordedit.text(),
        }
        with open("settings.json", "w") as f:
            json.dump(self.savesettings, f)

        self.show_save_dialog()

    def show_save_dialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Settings have been saved successfully!")
        msg.setWindowTitle("Save Settings")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                min-width: 400px;   
                min-height: 200px;  
            }
            QLabel {
                min-width: 300px;   
                font-size: 20px;    
            }
            QPushButton {
                min-width: 200px;   
                min-height: 100px; 
                font-size: 20px;   
            }
        """)
        self.stackedWidgetsetting.setCurrentIndex(0)
        self.homepages()
        self.stackedWidget_main.setCurrentIndex(0)
        msg.exec_()

    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.themebox.setCurrentText(settings.get("theme", "Gray"))
                self.fontsizebox.setCurrentText(settings.get("font_size", "15"))
                self.resolutionbox.setCurrentText(
                    settings.get(
                        "resolution", f"{self.windowwidth} x {self.windowheight}"
                    )
                )
                self.timezonebox.setCurrentText(
                    settings.get("timezone", str(datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo))
                )
                self.passwordedit.setText(settings.get("password", "pass"))
        except FileNotFoundError:
            pass

    def colorchange(self):
        if self.themebox.currentIndex() == 1:
            self.color = "#D3D3D3"
            self.MainWindow.setStyleSheet(f"background-color : {self.color}")
        else:
            color = QColorDialog.getColor()
            self.MainWindow.setStyleSheet(f"background-color : {color.name()}")
