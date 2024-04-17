# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'changepass.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(480, 620)
        Dialog.setStyleSheet(u"background-color: rgb(54, 54, 54);")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(100, 50, 300, 71))
        self.label.setStyleSheet(u"color:rgb(225, 225, 225); font-size:28pt;")
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(40, 260, 111, 31))
        self.label_3.setStyleSheet(u"font-size:15pt; color:rgb(255, 0, 127)")
        self.password = QLineEdit(Dialog)
        self.password.setObjectName(u"password")
        self.password.setGeometry(QRect(200, 260, 241, 51))
        self.password.setStyleSheet(u"font-size:14pt; color:rgb(243, 243, 243)")
        self.changepassbutton = QPushButton(Dialog)
        self.changepassbutton.setObjectName(u"changepassbutton")
        self.changepassbutton.setGeometry(QRect(270, 420, 180, 41))
        self.changepassbutton.setStyleSheet(u"background-color: rgb(167, 168, 167); font-size:14pt; color:rgb(255, 255, 255)")
        self.backbutton = QPushButton(Dialog)
        self.backbutton.setObjectName(u"backbutton")
        self.backbutton.setGeometry(QRect(80, 420, 140, 40))
        self.backbutton.setStyleSheet(u"background-color: rgb(167, 168, 167); font-size:14pt; color:rgb(255, 255, 255)")

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Change Password", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Change Password", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Password", None))
        self.password.setText("")
        self.changepassbutton.setText(QCoreApplication.translate("Dialog", u"Change Password", None))
        self.backbutton.setText(QCoreApplication.translate("Dialog", u"Back", None))
    # retranslateUi

