import sys
import os
import json
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtGui import *

#reset and close widget
class RestartCloseWidget(QWidget):
    def __init__(
        self,
        MainWindow,
        saved_setting,
        themebox,
        Text_size,
        resolutioncomboBox,
        country,
        font_size,
        password,
    ):
        # starting initialize
        super().__init__()
        self.MainWindow = MainWindow
        self.savesetting = saved_setting
        self.themebox = themebox
        self.Text_size = Text_size
        self.resolutioncomboBox = resolutioncomboBox
        self.country = country
        self.font_size = font_size
        self.password = password

        self.initUI()

    #restart and close ui
    def initUI(self):
        button_layout = QHBoxLayout()
        restart_btn = QPushButton("Restart App", self)
        restart_btn.setFont(QFont("Arial", self.font_size))
        restart_btn.setFixedHeight(200)
        restart_btn.clicked.connect(self.show_restart_dialog)
        button_layout.addWidget(restart_btn)
        close_btn = QPushButton("Close App", self)
        close_btn.setFont(QFont("Arial", self.font_size))
        close_btn.setFixedHeight(200)
        close_btn.clicked.connect(self.show_close_dialog)
        button_layout.addWidget(close_btn)
        self.setLayout(button_layout)

    #show restart
    def show_restart_dialog(self):
        reply = QMessageBox(self)
        reply.setIcon(QMessageBox.Question)
        reply.setWindowTitle("Restart App")
        reply.setText("Are you sure you want to restart the app?")
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply.setDefaultButton(QMessageBox.No)
        self.setstylesheet(reply)
        reply = reply.exec_()
        if reply == QMessageBox.Yes:
            self.save_settings()
            self.restart()

    #set stylesheet for ui
    def setstylesheet(self, reply):
        reply.setStyleSheet(
            """
            QMessageBox {
                min-width: 400px;   
                min-height: 200px;  
                icon-size: 100px 100px; 
            }
            QLabel {
                min-width: 300px;   
                font-size: 20px;
                icon-size: 100px 100px;     
            }
            QPushButton {
                min-width: 200px;   
                min-height: 100px; 
                font-size: 20px;   
                icon-size: 100px 100px; 
            }
            """
        )

    #save setting
    def save_settings(self):
        self.savesettings = {
            "theme": self.themebox.currentText(),
            "font_size": self.Text_size.currentText(),
            "resolution": self.resolutioncomboBox.currentText(),
            "timezone": self.country.currentText(),
            "password": self.password,
        }
        with open("settings.json", "w") as f:
            json.dump(self.savesettings, f)

    #show close dialog
    def show_close_dialog(self):
        reply = QMessageBox(self)
        reply.setIcon(QMessageBox.Question)
        reply.setWindowTitle("Close App")
        reply.setText("Are you sure you want to close the app?")
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply.setDefaultButton(QMessageBox.No)
        self.setstylesheet(reply)
        reply = reply.exec_()
        if reply == QMessageBox.Yes:
            self.save_settings()
            self.MainWindow.close()

    #restart implementation
    def restart(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)
