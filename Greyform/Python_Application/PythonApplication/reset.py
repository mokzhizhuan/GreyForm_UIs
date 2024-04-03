import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
)


class RestartCloseWidget(QWidget):
    def __init__(self, MainWindow):
        super().__init__()
        self.MainWindow = MainWindow
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        restart_btn = QPushButton("Restart App", self)
        restart_btn.clicked.connect(self.show_restart_dialog)
        layout.addWidget(restart_btn)

        close_btn = QPushButton("Close App", self)
        close_btn.clicked.connect(self.show_close_dialog)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def show_restart_dialog(self):
        reply = QMessageBox.question(
            self,
            "Restart App",
            "Are you sure you want to restart the app?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.restart()

    def show_close_dialog(self):
        reply = QMessageBox.question(
            self,
            "Close App",
            "Are you sure you want to close the app?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.MainWindow.close()

    def restart(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)
