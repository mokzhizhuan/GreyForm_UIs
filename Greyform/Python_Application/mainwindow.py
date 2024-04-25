from PyQt5 import QtCore, QtWidgets, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
from PythonApplication import mainframe


# load the mainwindow application
class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.mainwindow = uic.loadUi("UI_Design/mainframe.ui", self)
        self.ui = mainframe.Ui_MainWindow()
        self.ui.setupUi_mainWindow(self.mainwindow)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Ui_MainWindow()
    window.show()

    sys.exit(app.exec_())
