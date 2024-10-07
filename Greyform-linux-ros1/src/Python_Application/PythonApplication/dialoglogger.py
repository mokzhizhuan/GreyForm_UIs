from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QMainWindow
from PyQt5.QtCore import QTimer
import subprocess

#include dialog
class LogDialog(QDialog):
    def __init__(self, message, title, log_type="info"):
        super(LogDialog, self).__init__()
        self.setWindowTitle(f"{title} {log_type.capitalize()} Message")
        layout = QVBoxLayout()
        label = QLabel(message)
        label.setStyleSheet(
            """
            QLabel {
                font-size: 20px;              
            }
            """
        )
        layout.addWidget(label)
        ok_button = QPushButton("OK")
        ok_button.setStyleSheet(
            """
            QPushButton {
                font-size: 20px;           
                min-height: 100px;   
                icon-size: 100px 100px;        
            }
            """
        )
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
        self.setLayout(layout)

    def show_dialog(self):
        self.show()
