from PyQt5 import QtCore, QtWidgets, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class SettingLayout(object):
    def __init__(
        self,
        settingform,
        labeltitlsetting,
        settinglayoutWidget,
        layoutWidgethome,
        restoreDefaultsButton,
        settingHomepage,
        interface_label,
        treeWidget,
        wifipage,
        ip_label,
        Portnumipadd,
        serviceipaddresspage,
        layoutWidgetservicestextsize,
        host,
        layoutWidgetservicesresolution,
        layoutWidgetservicescountryGMT,
        layoutWidgetservicessetpass,
        SystemDate,
        Systemtime,
        SystemMemory,
        servicespage,
        userlabel,
        loginwidget,
        UserPage,
        version_label,
        titlelabel,
        author_label,
        info_label,
        AboutPage,
        restartwidget,
        RestartPowerOffPage,
    ):
        self.settingform = settingform
        self.labeltitlsetting = labeltitlsetting
        self.settinglayoutWidget = settinglayoutWidget
        self.layoutWidgethome = layoutWidgethome
        self.restoreDefaultsButton = restoreDefaultsButton
        self.settingHomepage = settingHomepage
        self.interface_label = interface_label
        self.treeWidget = treeWidget
        self.wifipage = wifipage
        self.ip_label = ip_label
        self.Portnumipadd = Portnumipadd
        self.serviceipaddresspage = serviceipaddresspage
        self.layoutWidgetservicestextsize = layoutWidgetservicestextsize
        self.host = host
        self.layoutWidgetservicesresolution = layoutWidgetservicesresolution
        self.layoutWidgetservicescountryGMT = layoutWidgetservicescountryGMT
        self.layoutWidgetservicessetpass = layoutWidgetservicessetpass
        self.SystemDate = SystemDate
        self.Systemtime = Systemtime
        self.SystemMemory = SystemMemory
        self.servicespage = servicespage
        self.userlabel = userlabel
        self.loginwidget = loginwidget
        self.UserPage = UserPage
        self.version_label = version_label
        self.titlelabel = titlelabel
        self.author_label = author_label
        self.info_label = info_label
        self.AboutPage = AboutPage
        self.restartwidget = restartwidget
        self.RestartPowerOffPage = RestartPowerOffPage
        self.setStretch()

    def setStretch(self):
        self.settingboxlayout = QVBoxLayout()
        self.settingboxlayout.addWidget(self.labeltitlsetting)
        self.settingboxlayout.addWidget(self.settinglayoutWidget)
        self.settingform.setLayout(self.settingboxlayout)
        self.settingboxhomelayout = QVBoxLayout()
        self.settingboxhomelayout.addWidget(self.layoutWidgethome)
        self.settingboxhomelayout.addWidget(self.restoreDefaultsButton)
        self.settingboxhomelayout.setStretch(0, 1)
        self.settingboxhomelayout.setStretch(1, 1)
        self.settingHomepage.setLayout(self.settingboxhomelayout)
        self.settingboxwifilayout = QVBoxLayout()
        self.settingboxwifilayout.addWidget(self.interface_label)
        self.settingboxwifilayout.addWidget(self.treeWidget)
        self.wifipage.setLayout(self.settingboxwifilayout)
        self.settingboxserviceipaddresslayout = QVBoxLayout()
        self.settingboxserviceipaddresslayout.addWidget(self.ip_label)
        self.settingboxserviceipaddresslayout.addWidget(self.Portnumipadd)
        self.serviceipaddresspage.setLayout(self.settingboxserviceipaddresslayout)
        self.settingboxserviceslayout = QVBoxLayout()
        self.settingboxserviceslayout.addWidget(self.layoutWidgetservicestextsize)
        self.settingboxserviceslayout.addWidget(self.host)
        self.settingboxserviceslayout.addWidget(self.layoutWidgetservicesresolution)
        self.settingboxserviceslayout.addWidget(self.layoutWidgetservicescountryGMT)
        self.settingboxserviceslayout.addWidget(self.layoutWidgetservicessetpass)
        self.settingboxserviceslayout.addWidget(self.SystemDate)
        self.settingboxserviceslayout.addWidget(self.Systemtime)
        self.settingboxserviceslayout.addWidget(self.SystemMemory)
        self.servicespage.setLayout(self.settingboxserviceslayout)
        self.settingformuserlayout = QVBoxLayout()
        self.settingformuserlayout.addWidget(self.userlabel)
        self.settingformuserlayout.addWidget(self.loginwidget)
        self.UserPage.setLayout(self.settingformuserlayout)
        self.settingboxaboutlayout = QVBoxLayout()
        self.settingboxaboutlayout.addWidget(self.version_label)
        self.settingboxaboutlayout.addWidget(self.titlelabel)
        self.settingboxaboutlayout.addWidget(self.author_label)
        self.settingboxaboutlayout.addWidget(self.info_label)
        self.AboutPage.setLayout(self.settingboxaboutlayout)
        self.settingboxrestartlayout = QVBoxLayout()
        self.settingboxrestartlayout.addWidget(self.restartwidget)
        self.RestartPowerOffPage.setLayout(self.settingboxrestartlayout)
