from PyQt5 import QtCore, QtWidgets, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PythonApplication.setting as setting


class restoredefaultsetting(object):
    def __init__(
        self,
        accountinfo,
        themebox,
        Text_size,
        resolutioncomboBox,
        country,
        default_settings,
        PasslineEdit,
        stackedwidgetpage,
        MainWindow,
        windowwidth,
        windowheight,
    ):
        self.stackedWidget = stackedwidgetpage
        self.MainWindow = MainWindow
        self.accountinfo = accountinfo
        self.themebox = themebox
        self.Text_size = Text_size
        self.resolutioncomboBox = resolutioncomboBox
        self.country = country
        self.default_settings = default_settings
        self.PasslineEdit = PasslineEdit
        self.windowwidth = windowwidth
        self.windowheight = windowheight
        self.restore_defaults()

    def restore_defaults(self):
        self.accountinfo[0]["Pass"] = "pass"
        theme_index = self.themebox.findText(
            self.default_settings["theme"], Qt.MatchFixedString
        )
        if theme_index >= 0:
            self.themebox.setCurrentIndex(theme_index)
        font_index = self.Text_size.findText(
            self.default_settings["font_size"], Qt.MatchFixedString
        )
        if font_index >= 0:
            self.Text_size.setCurrentIndex(font_index)
        resolution_index = self.resolutioncomboBox.findText(
            self.default_settings["resolution"], Qt.MatchFixedString
        )
        if resolution_index >= 0:
            self.resolutioncomboBox.setCurrentIndex(resolution_index)
        timezone_index = self.country.findText(
            self.default_settings["timezone"], Qt.MatchFixedString
        )
        if timezone_index >= 0:
            self.country.setCurrentIndex(timezone_index)
        self.accountinfo[0]["Pass"] = self.default_settings["password"]
        self.PasslineEdit.setText(self.default_settings["password"])
        self.settingchange = setting.Setting(
            self.stackedWidget, self.MainWindow, self.windowwidth, self.windowheight
        )
        self.settingchange.colorchange(theme_index)
        self.settingchange.update_font(font_index)
        self.settingchange.change_resolution(resolution_index)
        self.settingchange.updateTimeLabel(timezone_index)
