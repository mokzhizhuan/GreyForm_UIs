from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (
    QMainWindow,
    QDialog,
    QVBoxLayout,
    QLabel,
)
from PyQt5.QtGui import QFont


# menu dialog to confirm the robot marking
class Ui_Dialog_ConfirmAck(QMainWindow):
    def show_dialog_ConfirmAck(self):
        self.dialog = QDialog(self)
        self.dialog.setWindowTitle("Dialog Box")
        self.dialog.resize(400, 300)
        label = QLabel("Are you sure you want to finalize the marking?")
        label.setGeometry(QtCore.QRect(100, 40, 171, 31))
        label.setFont(QFont("Arial", 20))
        label.setWordWrap(True)
        label.setObjectName("label")
        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(label)
        self.dialog.setLayout(dialog_layout)
        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.setStyleSheet(
            """
            QDialogButtonBox QPushButton {
                font-size: 20px;      
                min-width: 200px;      
                min-height: 100px;   
                icon-size: 100px 100px;        
            }
            """
        )
        buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 100))
        buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
            | QtWidgets.QDialogButtonBox.StandardButton.Ok
        )
        buttonBox.setObjectName("buttonBox")
        # buttonBox.accepted.connect(self.trigger_alarm)
        buttonBox.rejected.connect(self.dialog.close)
        dialog_layout.addWidget(buttonBox)
        self.dialog.exec_()

    def trigger_alarm(self):
        # Set up serial connection
        # scan alarm if it is not needed . Dont need to implement it.
        # ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

        # Send command to trigger alarm
        # ser.write(b'ALARM_ON\n')  # Replace with the actual command to trigger the alarm
        self.dialog.close()
        self.close()
