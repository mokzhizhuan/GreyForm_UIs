from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget


class Usermanual(QWidget):
    def __init__(self, font, stackedWidget_main, usermanualpage):
        super(Usermanual, self).__init__()
        self.usermanual = uic.loadUi("UI_Design/usermanual.ui", self)
        self.font = font
        self.stackedWidget_main = stackedWidget_main
        self.usermanualpage = usermanualpage
        self.apply_font_to_widgets(self.usermanual, self.font)
        self.setupUi()

    # apply font
    def apply_font_to_widgets(self, parent, font):
        if hasattr(parent, "setFont"):
            parent.setFont(font)
        if hasattr(parent, "children"):
            for child in parent.children():
                self.apply_font_to_widgets(child, font)

    def setupUi(self):
        self.usermanualboxlayout = QVBoxLayout()
        self.usermanualboxlayout.addWidget(self.usermanual.usermanuallabel)
        self.usermanualboxlayout.addWidget(self.usermanual.texthelperBrowser)
        self.usermanualboxlayout.addWidget(self.usermanual.backtoUIButton)
        self.usermanualpage.setLayout(self.usermanualboxlayout)
        self.button_UI()

    def button_UI(self):
        self.usermanual.backtoUIButton.clicked.connect(
            lambda: self.stackedWidget_main.setCurrentIndex(0)
        )
