import sys
import os
from PyQt5 import QtGui, uic
from UI_Design import main_ui
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import * 
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
file = os.path.abspath(main_ui.__file__)



class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.files = file
        self.files = self.files.replace("_ui.py" , ".ui")
        print(self.files)
        uic.loadUi(self.files, self)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())