from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class Ui_MainWindow_layout(object):
    def __init__(
        self,
        stackedWidget,
        maintitle,
        mainlayoutwidget,
        mainlayoutpagebutton,
        mainmenu,
        page2layout,
        framepage2layout,
        page2,
        itemlabel_page3,
        page3layout,
        page3,
        page4layout,
        page4frame,
        page4,
        page5layout,
        page5,
        settinguipage,
        stackedWidget_main,
        usermanualButton,
        SettingButton,
        settingpage,
    ):
        self.stackedWidget = stackedWidget
        self.maintitle = maintitle
        self.mainlayoutwidget = mainlayoutwidget
        self.mainlayoutpagebutton = mainlayoutpagebutton
        self.mainmenu = mainmenu
        self.page2Layout = page2layout
        self.framepage2layout = framepage2layout
        self.page2 = page2
        self.itemlabel_page3 = itemlabel_page3
        self.page3Layout = page3layout
        self.page3 = page3
        self.page4Layout = page4layout
        self.page4frame = page4frame
        self.page4 = page4
        self.page5Layout = page5layout
        self.page5 = page5
        self.settinguipage = settinguipage
        self.settingpage = settingpage
        self.stackedWidget_main = stackedWidget_main
        self.SettingButton = SettingButton
        self.usermanualButton = usermanualButton
        self.setStretch()

    def setStretch(self):
        self.boxLayout = QVBoxLayout()
        self.settingusermanuallayout = QHBoxLayout()
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        self.settingusermanuallayout.addWidget(self.usermanualButton)
        self.settingusermanuallayout.addItem(self.horizontalSpacer)
        self.settingusermanuallayout.addWidget(self.SettingButton)
        self.settingusermanuallayout.setStretch(0, 1)
        self.settingusermanuallayout.setStretch(1, 4)
        self.settingusermanuallayout.setStretch(2, 1)
        self.boxLayout.addLayout(self.settingusermanuallayout)
        self.boxLayout.addWidget(self.stackedWidget)
        self.boxLayout.setStretch(0, 1)
        self.boxLayout.setStretch(1, 4)
        self.stackedWidget_main.setLayout(self.boxLayout)

        self.page1boxlayout = QVBoxLayout()
        self.verticalSpacer = QSpacerItem(
            20, 400, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        self.verticalSpacer_2 = QSpacerItem(
            20, 220, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        self.page1boxlayout.setSizeConstraint(QLayout.SetNoConstraint)
        self.page1boxlayout.addItem(self.verticalSpacer)
        self.page1boxlayout.addWidget(self.maintitle)
        self.page1boxlayout.addItem(self.verticalSpacer_2)
        self.page1boxlayout.addWidget(self.mainlayoutwidget)
        self.page1boxlayout.setStretch(0, 1)
        self.page1boxlayout.setStretch(1, 1)
        self.page1boxlayout.setStretch(2, 1)
        self.page1boxlayout.setStretch(3, 1)
        self.mainlayoutpagebutton.setStretch(0, 1)
        self.mainlayoutpagebutton.setStretch(1, 1)
        self.mainmenu.setLayout(self.page1boxlayout)
        self.page2boxLayout = QHBoxLayout()
        self.page2boxLayout.addWidget(self.page2Layout)
        self.page2boxLayout.addWidget(self.framepage2layout)
        self.page2boxLayout.setStretch(0, 1)
        self.page2boxLayout.setStretch(1, 1)
        self.page2.setLayout(self.page2boxLayout)
        self.page3boxLayout = QVBoxLayout()
        self.page3boxLayout.addWidget(self.itemlabel_page3)
        self.page3boxLayout.addWidget(self.page3Layout)
        self.page3boxLayout.setStretch(1, 1)
        self.page3.setLayout(self.page3boxLayout)
        self.page4boxLayout = QVBoxLayout()
        self.page4boxLayout.addWidget(self.page4Layout)
        self.page4boxLayout.addWidget(self.page4frame)
        self.page4boxLayout.setStretch(0, 2)
        self.page4boxLayout.setStretch(1, 2)
        self.page4.setLayout(self.page4boxLayout)
        self.page5boxLayout = QVBoxLayout()
        self.page5boxLayout.addWidget(self.page5Layout)
        self.page5.setLayout(self.page5boxLayout)
        self.page6boxLayout = QVBoxLayout()
        self.page6boxLayout.addWidget(self.settinguipage)
        self.settingpage.setLayout(self.page6boxLayout)
