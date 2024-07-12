# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Profile.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QPushButton, QSizePolicy,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(300, 300)
        self.profileiconlabel = QLabel(Form)
        self.profileiconlabel.setObjectName(u"profileiconlabel")
        self.profileiconlabel.setGeometry(QRect(110, 0, 111, 101))
        self.profileiconlabel.setPixmap(QPixmap(u"\u2014Pngtree\u2014avatar icon profile icon member_5247852.png"))
        self.profileiconlabel.setScaledContents(True)
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(100, 100, 141, 20))
        font = QFont()
        font.setPointSize(15)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)
        self.userlabel = QLabel(Form)
        self.userlabel.setObjectName(u"userlabel")
        self.userlabel.setGeometry(QRect(70, 130, 201, 51))
        self.userlabel.setFont(font)
        self.loginbutton = QPushButton(Form)
        self.loginbutton.setObjectName(u"loginbutton")
        self.loginbutton.setGeometry(QRect(100, 230, 121, 25))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.profileiconlabel.setText("")
        self.label.setText(QCoreApplication.translate("Form", u"Welcome", None))
        self.userlabel.setText("")
        self.loginbutton.setText(QCoreApplication.translate("Form", u"Back To Login", None))
    # retranslateUi

