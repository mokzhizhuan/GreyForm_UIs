from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class themechange(object):
    def __init__(self, config, centralWidget, mainWindow):
        self.config = config
        self.centralWidget = centralWidget
        self.mainWindow = mainWindow
        self.apply_styles()

    def apply_styles(self):
        if self.config['maincolor'] == "Gray":
            self.mainWindow.setStyleSheet("")
        else:
            main_bg_color = self.config['maincolor'] if self.config['maincolor'] != "Other Color" else self.config['themecolor']
            self.mainWindow.setStyleSheet(f"background-color: {main_bg_color};")
        if self.config['maincolortext'] == "Gray":
            self.apply_widget_style(QLabel, "")
        else:
            text_color = self.config['maincolortext'] if self.config['maincolortext'] != "Other Color" else self.config['text_labelothercolor']
            self.apply_widget_style(QLabel, f"color: {text_color};")
        if self.config['buttoncolor'] == "Gray":
            button_style = ""
        else:
            button_bg_color = self.config['buttoncolor'] if self.config['buttoncolor'] != "Other Color" else self.config['buttonthemeothercolor']
            button_style = f"background-color: {button_bg_color};"
        if self.config['buttontextcolor'] == "Gray":
            button_style += ""
        else:
            button_text_color = self.config['buttontextcolor'] if self.config['buttontextcolor'] != "Other Color" else self.config['buttontextothercolor']
            button_style += f" color: {button_text_color};"
        self.apply_widget_style(QPushButton, button_style)

    def apply_widget_style(self, widget_type, style):
        for widget in self.centralWidget.findChildren(widget_type):
            widget.setStyleSheet(style)

