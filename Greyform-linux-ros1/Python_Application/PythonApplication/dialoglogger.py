from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QMainWindow, QScrollArea
from PyQt5.QtCore import QTimer

#include dialog
class LogDialog(QDialog):
    def __init__(self, message, title, log_type="info"):
        # starting initialize
        super(LogDialog, self).__init__()
        self.setWindowTitle(f"{title} {log_type.capitalize()} Message")
        layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        label = QLabel(message)
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
