import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QDialogButtonBox,
)


class ResolutionDialog(QDialog):
    def __init__(self, windowwidth, windowheight, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Set Resolution")

        self.width_label = QLabel("Width:")
        self.width_input = QLineEdit(self)
        self.width_input.setText(str(windowwidth))

        self.height_label = QLabel("Height:")
        self.height_input = QLineEdit(self)
        self.height_input.setText(str(windowheight))

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.width_label)
        layout.addWidget(self.width_input)
        layout.addWidget(self.height_label)
        layout.addWidget(self.height_input)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def getResolution(self):
        width = int(self.width_input.text())
        height = int(self.height_input.text())
        return width, height
