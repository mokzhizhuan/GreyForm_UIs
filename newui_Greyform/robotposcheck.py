from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QMainWindow, QScrollArea
from PyQt5.QtCore import QTimer

#include dialog
class LogDialog(QDialog):
    def __init__(self):
        # starting initialize
        super(LogDialog, self).__init__()
        self.setWindowTitle(f"message")
        layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        label = QLabel("The robot is correctly centered.")
        label.setStyleSheet(
            """
            QLabel {
                font-size: 20px;              
            }
            """
        )
        label.setWordWrap(True)
        scroll_area.setWidget(label)
        layout.addWidget(scroll_area)
        self.setLayout(layout)
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
