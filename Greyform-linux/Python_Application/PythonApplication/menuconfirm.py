from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QDialog,
    QVBoxLayout,
    QLabel,
    QWidget,
)

#menu dialog to go back to the menu
class Ui_Dialog_Confirm(QMainWindow):
    def show_dialog_confirm(self, stacked_widget):
        # Create a QDialog instance
        dialog = QDialog(self)
        dialog.setWindowTitle("Dialog Box")
        dialog.resize(400, 300)
        # Create a label with a mes sage
        label = QLabel("Are you sure you want to go back to the menu?")
        label.setGeometry(QtCore.QRect(100, 40, 171, 31))
        label.setWordWrap(True)
        label.setObjectName("label")
        # Create a layout for the dialog
        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(label)

        # Set the layout for the dialog
        dialog.setLayout(dialog_layout)

        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
            | QtWidgets.QDialogButtonBox.StandardButton.Ok
        )
        buttonBox.setObjectName("buttonBox")
        buttonBox.accepted.connect(lambda: stacked_widget.setCurrentIndex(0))
        buttonBox.accepted.connect(dialog.close)
        buttonBox.rejected.connect(dialog.close)
        dialog_layout.addWidget(buttonBox)

        # Show the dialog as a modal dialog (blocks the main window)
        dialog.exec_()
