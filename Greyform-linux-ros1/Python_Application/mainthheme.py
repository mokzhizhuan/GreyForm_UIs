from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class themechange(object):
    def __init__(
        self,
        maincolor,
        maincolortext,
        buttoncolor,
        buttontextcolor,
        centralWidget,
        mainwindow,
    ):
        self.maincolor = maincolor
        self.maincolortext = maincolortext
        self.buttoncolor = buttoncolor
        self.buttoncolortext = buttontextcolor
        self.centralwidget = centralWidget
        self.MainWindow = mainwindow
        self.colorchange()
        self.colorchangetext()
        self.colorchangebutton()
        self.colorchangetextbutton

    def colorchange(self):
        if self.maincolor == "Gray":
            self.MainWindow.setStyleSheet("")
        elif self.maincolor == "Black":
            self.MainWindow.setStyleSheet(
                f"color: white; background-color : {self.maincolor}"
            )
        else:
            self.MainWindow.setStyleSheet(f"background-color : {self.maincolor.name()}")

    def colorchangetext(self):
        if self.maincolortext == "Gray":
            for child in self.centralwidget.findChildren(QLabel):
                child.setStyleSheet(f"color: {self.maincolortext}")
        elif self.maincolortext == "Black":
            for child in self.centralwidget.findChildren(QLabel):
                child.setStyleSheet(f"color: {self.maincolortext}")
        else:
            if self.maincolortext.isValid():
                selected_color = self.maincolortext.name()
                for child in self.centralwidget.findChildren(QLabel):
                    child.setStyleSheet(f"color: {selected_color}")

    def colorchangebutton(self):
        if self.buttoncolor == "Gray":
            for child in self.centralwidget.findChildren(QPushButton):
                child.setStyleSheet(
                    f"background-color: {self.buttoncolor}; color: black;"
                )
        elif self.buttoncolor == "Black":
            for child in self.centralwidget.findChildren(QPushButton):
                child.setStyleSheet(
                    f"background-color: {self.buttoncolor}; color: white;"
                )
        else:
            selected_color = self.buttoncolor
            for child in self.centralwidget.findChildren(QPushButton):
                child.setStyleSheet(
                    f"background-color: {selected_color}; color: white;"
                )

    def colorchangetextbutton(self):
        if self.buttoncolortext == "Gray":
            for child in self.centralwidget.findChildren(QPushButton):
                child.setStyleSheet(
                    f"background-color: {self.buttoncolor}; color: {self.buttoncolortext}"
                )
        elif self.buttoncolortext == "Black":
            for child in self.centralwidget.findChildren(QPushButton):
                child.setStyleSheet(
                    f"background-color: {self.buttoncolor}; color: {self.buttoncolortext}"
                )
        else:
            if self.buttoncolortext.isValid():
                selected_color = self.buttoncolortext.name()
                for child in self.centralwidget.findChildren(QPushButton):
                    child.setStyleSheet(
                        f"background-color: {self.buttoncolor}; color: {selected_color}"
                    )
