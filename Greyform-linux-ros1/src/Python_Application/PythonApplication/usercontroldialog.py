import sys
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QHBoxLayout,
)


class TControlsDialog(QDialog):
    def __init__(self, parent=None):
        super(TControlsDialog, self).__init__(parent)
        self.setWindowTitle("Users Controls")

        # Set up the layout and widgets
        layout = QVBoxLayout(self)

        # Label to instruct the user
        title_label = QLabel("Please read the user controls below:")
        layout.addWidget(title_label)

        # Terms text (can be loaded from a file)
        controls_text = (
            "GUI (Graphical User Interface) Instruction:\n"
            "1. Press right click to go inside the PBU (Pre-Fabricated Bathroom Unit) view.\n"
            "2. Use Up, Down, Left, Right keys for camera movement.\n"
            "3. Left click is to move the inside view.\n"
            "4. Right click is to move the camera from toilet room to shower room and then revert back to the toilet room.\n"
            "5. Middle click is to add the position in a sequence (this will include a storing position variable UI).\n"
            "6. Press 'L' key to reset to the default view."
        )
        controls_text_edit = QTextEdit(self)
        controls_text_edit.setText(controls_text)
        controls_text_edit.setReadOnly(True)
        layout.addWidget(controls_text_edit)
        button_layout = QHBoxLayout()
        accept_button = QPushButton("Accept")
        button_layout.addWidget(accept_button)
        layout.addLayout(button_layout)
        accept_button.clicked.connect(self.accept)
