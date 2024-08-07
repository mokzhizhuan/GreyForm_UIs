from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont


class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Save Settings')
        self.setFixedSize(600, 200) 
        layout = QVBoxLayout()
        self.label = QLabel('Do you want to save the settings?')
        self.label.setFont(QFont('Arial', 20)) 
        layout.addWidget(self.label)
        buttonLayout = QHBoxLayout()
        self.confirmButton = QPushButton('Confirm')
        self.confirmButton.setFont(QFont('Arial', 20))
        self.confirmButton.setFixedSize(200, 100) 
        self.confirmButton.clicked.connect(self.accept)
        buttonLayout.addWidget(self.confirmButton)
        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.setFont(QFont('Arial', 20))  
        self.cancelButton.setFixedSize(200, 100)  
        self.cancelButton.clicked.connect(self.reject)
        buttonLayout.addWidget(self.cancelButton)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)