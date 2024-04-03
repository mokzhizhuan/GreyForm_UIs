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

class Ui_SettingForm(object):
    def setupUi(self, SettingForm):
        if not SettingForm.objectName():
            SettingForm.setObjectName(u"SettingForm")
        SettingForm.resize(1168, 796)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SettingForm.sizePolicy().hasHeightForWidth())
        SettingForm.setSizePolicy(sizePolicy)
        self.labeltitlsetting = QLabel(SettingForm)
        self.labeltitlsetting.setObjectName(u"labeltitlsetting")
        self.labeltitlsetting.setGeometry(QRect(480, 10, 381, 32))
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.labeltitlsetting.sizePolicy().hasHeightForWidth())
        self.labeltitlsetting.setSizePolicy(sizePolicy1)
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.labeltitlsetting.setFont(font)
        self.labeltitlsetting.setTextFormat(Qt.AutoText)
        self.labeltitlsetting.setAlignment(Qt.AlignCenter)
        self.WifiButton = QPushButton(SettingForm)
        self.WifiButton.setObjectName(u"WifiButton")
        self.WifiButton.setGeometry(QRect(50, 80, 400, 80))
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.WifiButton.sizePolicy().hasHeightForWidth())
        self.WifiButton.setSizePolicy(sizePolicy2)
        self.serviceIPAddressButton = QPushButton(SettingForm)
        self.serviceIPAddressButton.setObjectName(u"serviceIPAddressButton")
        self.serviceIPAddressButton.setGeometry(QRect(50, 180, 400, 80))
        self.ServicesButton = QPushButton(SettingForm)
        self.ServicesButton.setObjectName(u"ServicesButton")
        self.ServicesButton.setGeometry(QRect(50, 280, 400, 80))
        self.UserButton = QPushButton(SettingForm)
        self.UserButton.setObjectName(u"UserButton")
        self.UserButton.setGeometry(QRect(50, 380, 400, 80))
        self.PowerButton = QPushButton(SettingForm)
        self.PowerButton.setObjectName(u"PowerButton")
        self.PowerButton.setGeometry(QRect(50, 480, 400, 80))
        self.AboutButton = QPushButton(SettingForm)
        self.AboutButton.setObjectName(u"AboutButton")
        self.AboutButton.setGeometry(QRect(50, 580, 400, 80))
        self.MarkingbackButton = QPushButton(SettingForm)
        self.MarkingbackButton.setObjectName(u"MarkingbackButton")
        self.MarkingbackButton.setGeometry(QRect(50, 680, 400, 80))
        self.stackedWidgetsetting = QStackedWidget(SettingForm)
        self.stackedWidgetsetting.setObjectName(u"stackedWidgetsetting")
        self.stackedWidgetsetting.setGeometry(QRect(560, 80, 511, 671))
        self.settingHomepage = QWidget()
        self.settingHomepage.setObjectName(u"settingHomepage")
        self.stackedWidgetsetting.addWidget(self.settingHomepage)
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

        self.retranslateUi(SettingForm)

        QMetaObject.connectSlotsByName(SettingForm)
    # setupUi

    def retranslateUi(self, SettingForm):
        SettingForm.setWindowTitle(QCoreApplication.translate("SettingForm", u"SettingForm", None))
        self.labeltitlsetting.setText(QCoreApplication.translate("SettingForm", u"Settings", None))
        self.WifiButton.setText(QCoreApplication.translate("SettingForm", u"Wifi", None))
        self.serviceIPAddressButton.setText(QCoreApplication.translate("SettingForm", u"Service IP Address", None))
        self.ServicesButton.setText(QCoreApplication.translate("SettingForm", u"Services", None))
        self.UserButton.setText(QCoreApplication.translate("SettingForm", u"User", None))
        self.PowerButton.setText(QCoreApplication.translate("SettingForm", u"Power/ShutDown/Restart", None))
        self.AboutButton.setText(QCoreApplication.translate("SettingForm", u"About", None))
        self.MarkingbackButton.setText(QCoreApplication.translate("SettingForm", u"Back to Marking Menu", None))
    # retranslateUi

