from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QMainWindow

class LogDialog(QDialog):
    def __init__(self, message, title, log_type="info"):
        super(LogDialog, self).__init__()
        self.setWindowTitle(f"{title} {log_type.capitalize()} Message")
        layout = QVBoxLayout()

        label = QLabel(message)
        layout.addWidget(label)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        self.setLayout(layout)