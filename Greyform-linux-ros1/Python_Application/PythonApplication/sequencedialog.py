from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
import sys

class SeqnumberDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Set up the dialog layout
        self.setWindowTitle("Select a Number")
        self.layout = QVBoxLayout()
        self.selected_seqnumber = None

        # Text input field
        self.label = QLabel("Choose a Sequence number by clicking a button or entering a number (1(Sequence 1), 2(Sequence 2), or 3(Sequence 3)):")
        self.layout.addWidget(self.label)

        self.input_field = QLineEdit(self)
        self.layout.addWidget(self.input_field)

        # Buttons for numbers
        self.button1 = QPushButton("Sequence 1")
        self.button2 = QPushButton("Sequence 2")
        self.button3 = QPushButton("Sequence 3")
        self.confirm_button = QPushButton("Confirm")

        # Connect buttons to the input field
        self.button1.clicked.connect(lambda: self.set_input("1"))
        self.button2.clicked.connect(lambda: self.set_input("2"))
        self.button3.clicked.connect(lambda: self.set_input("3"))
        self.confirm_button.clicked.connect(self.confirm_selection)

        # Add buttons to layout
        self.layout.addWidget(self.button1)
        self.layout.addWidget(self.button2)
        self.layout.addWidget(self.button3)
        self.layout.addWidget(self.confirm_button)

        self.setLayout(self.layout)

    def set_input(self, number):
        self.input_field.setText(number)

    def confirm_selection(self):
        selected_seqnumber = self.input_field.text()
        if selected_seqnumber in ["1", "2", "3"]:
            self.selected_seqnumber = int(selected_seqnumber)  # Store the selected number as an integer
            self.accept()  # Close the dialog with an accept status
        else:
            QMessageBox.warning(self, "Invalid Selection", "Please select 1, 2, or 3.")
    
    def get_selected_seqnumber(self):
        return self.selected_seqnumber  # Return the selected number
