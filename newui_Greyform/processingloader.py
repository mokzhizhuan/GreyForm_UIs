from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QWidget, QSizePolicy
from PyQt5.QtGui import QIcon, QPixmap, QMovie
from PyQt5.QtCore import Qt
from typing import Optional

#include dialog
class LogDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)                 # OK: parent is QWidget or None
        self.setWindowTitle("Processing Loader")
        self.setWindowModality(Qt.WindowModal)   # or Qt.ApplicationModal
        self.setMinimumSize(420, 260)
        layout = QVBoxLayout(self)
        
        scroll = QScrollArea(self); scroll.setWidgetResizable(True)
        self.label = QLabel("", self); self.label.setWordWrap(True)
        self.label.setStyleSheet("QLabel { font-size: 20px; }")
        scroll.setWidget(self.label)
        layout.addWidget(scroll)

    def set_text(self, text: str):
        icon = "processing.png"
        html = f'<img src="{icon}" width="40" height="40" style="vertical-align:middle; margin-right:8px;"> {text}'
        self.label.setTextFormat(Qt.RichText)
        self.label.setText(html)
    
