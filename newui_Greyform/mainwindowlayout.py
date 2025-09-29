from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


# main window layout
class Ui_MainWindow_layout(object):
    def __init__(
        self,
        stackedWidget,
        titlelabel,
        verticalLayoutWidget_3,
        page,
    ):
        # starting initialize
        super().__init__()
        self.stackedWidget = stackedWidget
        self.titlelabel = titlelabel
        self.verticalLayoutWidget_3 = verticalLayoutWidget_3
        self.page = page
        self.setStretch()
        
    def setStretch(self):
        self.page1boxlayout = QVBoxLayout()
        self.page1boxlayout.addWidget(self.titlelabel)
        self.page1boxlayout.addWidget(self.verticalLayoutWidget_3)
        self.page1boxlayout.setStretch(0, 1)
        self.page1boxlayout.setStretch(1, 5)
        self.page.setLayout(self.page1boxlayout)
