# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'setting.ui'
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
    QStackedWidget, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1168, 796)
        self.labeltitlsetting = QLabel(Form)
        self.labeltitlsetting.setObjectName(u"labeltitlsetting")
        self.labeltitlsetting.setGeometry(QRect(480, 10, 381, 32))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labeltitlsetting.sizePolicy().hasHeightForWidth())
        self.labeltitlsetting.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.labeltitlsetting.setFont(font)
        self.labeltitlsetting.setTextFormat(Qt.AutoText)
        self.labeltitlsetting.setAlignment(Qt.AlignCenter)
        self.WifiButton = QPushButton(Form)
        self.WifiButton.setObjectName(u"WifiButton")
        self.WifiButton.setGeometry(QRect(50, 80, 400, 80))
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.WifiButton.sizePolicy().hasHeightForWidth())
        self.WifiButton.setSizePolicy(sizePolicy1)
        self.serviceIPAddressButton = QPushButton(Form)
        self.serviceIPAddressButton.setObjectName(u"serviceIPAddressButton")
        self.serviceIPAddressButton.setGeometry(QRect(50, 180, 400, 80))
        self.ServicesButton = QPushButton(Form)
        self.ServicesButton.setObjectName(u"ServicesButton")
        self.ServicesButton.setGeometry(QRect(50, 280, 400, 80))
        self.UserButton = QPushButton(Form)
        self.UserButton.setObjectName(u"UserButton")
        self.UserButton.setGeometry(QRect(50, 380, 400, 80))
        self.PowerButton = QPushButton(Form)
        self.PowerButton.setObjectName(u"PowerButton")
        self.PowerButton.setGeometry(QRect(50, 480, 400, 80))
        self.AboutButton = QPushButton(Form)
        self.AboutButton.setObjectName(u"AboutButton")
        self.AboutButton.setGeometry(QRect(50, 580, 400, 80))
        self.MarkingbackButton = QPushButton(Form)
        self.MarkingbackButton.setObjectName(u"MarkingbackButton")
        self.MarkingbackButton.setGeometry(QRect(50, 680, 400, 80))
        self.stackedWidgetsetting = QStackedWidget(Form)
        self.stackedWidgetsetting.setObjectName(u"stackedWidgetsetting")
        self.stackedWidgetsetting.setGeometry(QRect(560, 80, 511, 671))
        self.wifipage = QWidget()
        self.wifipage.setObjectName(u"wifipage")
        self.stackedWidgetsetting.addWidget(self.wifipage)
        self.serviceipaddresspage = QWidget()
        self.serviceipaddresspage.setObjectName(u"serviceipaddresspage")
        self.stackedWidgetsetting.addWidget(self.serviceipaddresspage)
        self.servicespage = QWidget()
        self.servicespage.setObjectName(u"servicespage")
        self.stackedWidgetsetting.addWidget(self.servicespage)
        self.UserPage = QWidget()
        self.UserPage.setObjectName(u"UserPage")
        self.stackedWidgetsetting.addWidget(self.UserPage)
        self.AboutPage = QWidget()
        self.AboutPage.setObjectName(u"AboutPage")
        self.stackedWidgetsetting.addWidget(self.AboutPage)
        self.RestartPowerOffPage = QWidget()
        self.RestartPowerOffPage.setObjectName(u"RestartPowerOffPage")
        self.stackedWidgetsetting.addWidget(self.RestartPowerOffPage)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.labeltitlsetting.setText(QCoreApplication.translate("Form", u"Settings", None))
        self.WifiButton.setText(QCoreApplication.translate("Form", u"Wifi", None))
        self.serviceIPAddressButton.setText(QCoreApplication.translate("Form", u"Service IP Address", None))
        self.ServicesButton.setText(QCoreApplication.translate("Form", u"Services", None))
        self.UserButton.setText(QCoreApplication.translate("Form", u"User", None))
        self.PowerButton.setText(QCoreApplication.translate("Form", u"Power/ShutDown/Restart", None))
        self.AboutButton.setText(QCoreApplication.translate("Form", u"About", None))
        self.MarkingbackButton.setText(QCoreApplication.translate("Form", u"Back to Marking", None))
    # retranslateUi

