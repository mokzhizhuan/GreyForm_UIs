from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QMainWindow,
    QDialog,
    QVBoxLayout,
    QLabel,
)
from PyQt5.QtGui import QFont
import vtk


# menu dialog to confirm the robot marking
class Ui_Dialog_ConfirmAck(QMainWindow):
    def show_dialog_ConfirmAck(self):
        self.dialog = QDialog(self)
        self.dialog.setWindowTitle("Dialog Box")
        self.dialog.resize(400, 300)
        label = QLabel("Are you sure you want to finalize the marking?")
        label.setGeometry(QtCore.QRect(100, 40, 171, 31))
        label.setFont(QFont('Arial', 20)) 
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
        buttonBox.accepted.connect(lambda: Ui_Dialog_ConfirmAck.appendasSTL(self))
        buttonBox.rejected.connect(self.dialog.close)
        dialog_layout.addWidget(buttonBox)
        self.dialog.exec_()

    def appendasSTL(self):
        self.dialog.close()
        self.close()
