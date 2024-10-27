import sys
from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class markingitemdialog(QDialog):
    def __init__(self, excel_elementsdata, counter, maxlen):
        super().__init__()
        self.setWindowTitle("Marking Dialog")
        self.counter = counter
        self.maxlen = maxlen
        self.excel_elementsdata = excel_elementsdata
        self.setGeometry(200, 200, 300, 200)
        self.spacing = "\n"
        labelitem = (
            f"Marking item {excel_elementsdata['markingidentifiers'][counter]} {self.spacing}"
            f"Position [{excel_elementsdata['Position X (m)'][counter]},"
            f"{excel_elementsdata['Position Y (m)'][counter]}, {excel_elementsdata['Position Z (m)'][counter]}"
            f" ] {self.spacing} Shape Type : {excel_elementsdata['Shape type'][counter]} "
        )
        layout = QVBoxLayout()
        self.label = QLabel(labelitem)
        layout.addWidget(self.label)
        next_item_button = QPushButton("Next Marking Item")
        next_item_button.clicked.connect(self.updatemarkingitem)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(next_item_button)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def updatemarkingitem(self):
        self.counter = self.counter + 1
        if self.counter < self.maxlen:
            labelitem = (
                f"Marking item {self.excel_elementsdata['markingidentifiers'][self.counter]} {self.spacing}"
                f"Position [{self.excel_elementsdata['Position X (m)'][self.counter]},"
                f"{self.excel_elementsdata['Position Y (m)'][self.counter]},"
                f" {self.excel_elementsdata['Position Z (m)'][self.counter]}"
                f" ] {self.spacing} Shape Type : {self.excel_elementsdata['Shape type'][self.counter]} "
            )
            self.label.setText(labelitem)
            self.show()
