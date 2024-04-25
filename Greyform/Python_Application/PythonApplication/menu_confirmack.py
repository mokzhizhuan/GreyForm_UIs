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
import vtk


# menu dialog to confirm the robot marking
class Ui_Dialog_ConfirmAck(QMainWindow):
    def show_dialog_ConfirmAck(self, append_filter):
        # Create a QDialog instance
        self.dialog = QDialog(self)
        self.dialog.setWindowTitle("Dialog Box")
        self.dialog.resize(400, 300)

        # Create a label with a message
        label = QLabel("Are you sure you want to finalize the marking?")
        label.setGeometry(QtCore.QRect(100, 40, 171, 31))
        label.setWordWrap(True)
        label.setObjectName("label")
        # Create a layout for the dialog
        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(label)
        self.append_filter = append_filter
        # Set the layout for the dialog
        self.dialog.setLayout(dialog_layout)

        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
            | QtWidgets.QDialogButtonBox.StandardButton.Ok
        )
        buttonBox.setObjectName("buttonBox")
        buttonBox.accepted.connect(lambda: Ui_Dialog_ConfirmAck.appendasSTL(self))

        buttonBox.rejected.connect(self.dialog.close)
        dialog_layout.addWidget(buttonBox)

        # Show the dialog as a modal dialog (blocks the main window)
        self.dialog.exec_()

    #finalize output , will fix it after ros research. this is a rough idea.
    def appendasSTL(self):
        # Write initial STL file
        #stl_writer = vtk.vtkSTLWriter()
        #stl_writer.SetFileName("output.stl")
        #stl_writer.SetInputData(self.append_filter.GetOutput())
        #stl_writer.Write()
        self.dialog.close()
        self.close()
