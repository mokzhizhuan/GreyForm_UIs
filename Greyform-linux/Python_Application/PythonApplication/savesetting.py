
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout


class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Save Settings')
        layout = QVBoxLayout()
        self.label = QLabel('Do you want to save the settings?')
        layout.addWidget(self.label)
        buttonLayout = QHBoxLayout()
        self.confirmButton = QPushButton('Confirm')
        self.confirmButton.clicked.connect(self.accept)
        buttonLayout.addWidget(self.confirmButton)
        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.reject)
        buttonLayout.addWidget(self.cancelButton)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)