import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PythonApplication import mainframe


# main application to execute the main frame
class Ui_MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(Ui_MainWindow, self).__init__(parent)
        self.ui = mainframe.Ui_MainWindow()
        self.ui.setupUi_mainWindow(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Ui_MainWindow()
    window.show()

    sys.exit(app.exec_())
