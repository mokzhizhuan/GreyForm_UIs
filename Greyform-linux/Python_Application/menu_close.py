from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QDialog, QVBoxLayout, QLabel, QApplication
from PyQt5.QtGui import QFont
import appinit as initlizemenu
import sys
import os


#menu dialog to close the app
class Ui_Dialog_Close(QMainWindow):
    def show_dialog_close(self, ros_node):
        dialog = QDialog(self)
        dialog.setWindowTitle("Dialog Box")
        dialog.resize(400, 300)
        label = QLabel("Are you sure you want to close the window??")
        label.setGeometry(QtCore.QRect(100, 40, 171, 31))
        label.setFont(QFont('Arial', 20)) 
        label.setWordWrap(True)
        label.setObjectName("label")
        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(label)
        dialog.setLayout(dialog_layout)
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
        buttonBox.accepted.connect(dialog.close)
        buttonBox.accepted.connect(self.close)
        buttonBox.rejected.connect(dialog.close)
        dialog_layout.addWidget(buttonBox)
        dialog.exec_()

    #back to init window
    def runbacktomenuUI(self, ros_node):
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        #main_window_menu = initlizemenu.Ui_InitilizeWindow(ros_node)
        #main_window_menu.show()
        self.close()