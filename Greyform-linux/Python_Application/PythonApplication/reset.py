import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
    QSizePolicy,
)
from PyQt5.QtGui import *
import json


class RestartCloseWidget(QWidget):
    def __init__(
        self,
        MainWindow,
        saved_setting,
        themebox,
        Text_size,
        resolutioncomboBox,
        country,
        password
    ):
        super().__init__()
        self.MainWindow = MainWindow
        self.savesetting = saved_setting
        self.themebox = themebox
        self.Text_size = Text_size
        self.resolutioncomboBox = resolutioncomboBox
        self.country = country
        self.password = password
        self.initUI()

    def initUI(self):
        button_layout = QHBoxLayout()
        restart_btn = QPushButton("Restart App", self)
        restart_btn.setFont(QFont("Arial", 18))
        restart_btn.clicked.connect(self.show_restart_dialog)
        button_layout.addWidget(restart_btn)
        close_btn = QPushButton("Close App", self)
        close_btn.setFont(QFont("Arial", 18))
        close_btn.clicked.connect(self.show_close_dialog)
        button_layout.addWidget(close_btn)
        self.setLayout(button_layout)

    def show_restart_dialog(self):
        reply = QMessageBox(self)
        reply.setIcon(QMessageBox.Question)
        reply.setWindowTitle("Close App")
        reply.setText("Are you sure you want to close the app?")
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply.setDefaultButton(QMessageBox.No)
        reply.setStyleSheet(
            """
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
        """
        )
        reply = reply.exec_()
        if reply == QMessageBox.Yes:
            self.save_settings()
            self.restart()

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

    def show_close_dialog(self):
        reply = QMessageBox(self)
        reply.setIcon(QMessageBox.Question)
        reply.setWindowTitle("Close App")
        reply.setText("Are you sure you want to close the app?")
        reply.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply.setDefaultButton(QMessageBox.No)
        reply.setStyleSheet(
            """
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
        """
        )
        reply = reply.exec_()
        if reply == QMessageBox.Yes:
            self.save_settings()
            self.MainWindow.close()

    def restart(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)
