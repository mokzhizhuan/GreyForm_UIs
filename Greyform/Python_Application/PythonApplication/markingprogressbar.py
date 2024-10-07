from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QProgressBar, QLabel, QPushButton
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont

#loading mar & loc Progress bar(visual)
class MarkingProgressBar(QDialog):
    def __init__(self):
        super().__init__()
        progress_layout = QVBoxLayout()
        self.setWindowTitle("Progress Window")
        self.setGeometry(100, 100, 600, 200)
        self.setLayout(progress_layout)
        self.status_label = QLabel("Stage of marking")
        self.status_label.setGeometry(QtCore.QRect(50, 30, 200, 100))
        self.status_label.setFont(QFont("Arial", 30))
        self.status_label.setWordWrap(True)
        self.status_label.setObjectName("label")
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFont(QFont("Arial", 30))
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar.setGeometry(30, 130, 340, 200)
        self.confirm_button = QPushButton("Confirm", self)
        self.confirm_button.setFont(QFont("Arial", 20))
        self.confirm_button.setEnabled(False)
        self.confirm_button.hide()  # Initially disabled
        self.confirm_button.clicked.connect(self.close)  # Close the dialog on click
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgressBar)
        self.timer.start(100)
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.confirm_button)
        self.startSequence()

    def startSequence(self):
        self.progress_bar.setValue(0)
        self.timer.start(100)

    def updateProgressBar(self):
        current_value = self.progress_bar.value()
        if current_value < 100:
            self.progress_bar.setValue(current_value + 1)
        else:
            self.timer.stop()
            self.status_label.setText("Completed! Stage of marking")
            self.confirm_button.setEnabled(True)
            self.confirm_button.show()
