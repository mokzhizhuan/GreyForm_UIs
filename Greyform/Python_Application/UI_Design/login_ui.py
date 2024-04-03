# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login.ui'
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
        self.label.setGeometry(QRect(190, 50, 121, 71))
        self.label.setStyleSheet(u"color:rgb(225, 225, 225); font-size:28pt;")
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(40, 160, 101, 31))
        self.label_2.setStyleSheet(u"font-size:15pt; color:rgb(255, 0, 127)")
        self.email = QLineEdit(Dialog)
        self.email.setObjectName(u"email")
        self.email.setGeometry(QRect(170, 150, 241, 51))
        self.email.setStyleSheet(u"font-size:14pt; color:rgb(243, 243, 243)")
        self.password = QLineEdit(Dialog)
        self.password.setObjectName(u"password")
        self.password.setGeometry(QRect(170, 260, 241, 51))
        self.password.setStyleSheet(u"font-size:14pt; color:rgb(243, 243, 243)")
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(40, 270, 111, 31))
        self.label_3.setStyleSheet(u"font-size:15pt; color:rgb(255, 0, 127)")
        self.loginbutton = QPushButton(Dialog)
        self.loginbutton.setObjectName(u"loginbutton")
        self.loginbutton.setGeometry(QRect(270, 390, 141, 41))
        self.loginbutton.setStyleSheet(u"background-color: rgb(167, 168, 167); font-size:14pt; color:rgb(255, 255, 255)")
        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(180, 350, 171, 16))
        self.label_4.setStyleSheet(u"color:rgb(255, 255, 255)")
        self.createaccbutton = QPushButton(Dialog)
        self.createaccbutton.setObjectName(u"createaccbutton")
        self.createaccbutton.setGeometry(QRect(320, 340, 93, 28))
        self.createaccbutton.setStyleSheet(u"color:rgb(255, 255, 255)")

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Login", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Email", None))
        self.password.setText("")
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Password", None))
        self.loginbutton.setText(QCoreApplication.translate("Dialog", u"Login", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"Don't have an account?", None))
        self.createaccbutton.setText(QCoreApplication.translate("Dialog", u"Create Account", None))
    # retranslateUi

