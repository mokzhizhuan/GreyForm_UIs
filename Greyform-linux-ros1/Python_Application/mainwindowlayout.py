from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


#main window layout
class Ui_MainWindow_layout(object):
    def __init__(
        self,
        stackedWidget,
        maintitle,
        mainlayoutwidget,
        mainlayoutpagebutton,
        mainmenu,
        horizontalLayoutWidget,
        horizontalLayoutWidget2,
        page,
        page2,
        page2layout,
        page2frame,
        page3,
        page3layout,
        stackedWidget_main,
        SettingButton,
        settingpage,
    ):
        # starting initialize
        super().__init__()
        self.stackedWidget = stackedWidget
        self.maintitle = maintitle
        self.mainlayoutwidget = mainlayoutwidget
        self.mainlayoutpagebutton = mainlayoutpagebutton
        self.mainmenu = mainmenu
        self.horizontalLayoutWidget = horizontalLayoutWidget
        self.horizontalLayoutWidget2 = horizontalLayoutWidget2
        self.page = page
        self.page2 = page2
        self.page2Layout = page2layout
        self.page2frame = page2frame
        self.page3 = page3
        self.page3Layout = page3layout
        self.settingpage = settingpage
        self.stackedWidget_main = stackedWidget_main
        self.SettingButton = SettingButton
        self.setStretch()

    #stretch layout
    def setStretch(self):
        self.boxLayout = QVBoxLayout()
        self.settingusermanuallayout = QHBoxLayout()
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        self.settingusermanuallayout.addItem(self.horizontalSpacer)
        self.settingusermanuallayout.addWidget(self.SettingButton)
        self.settingusermanuallayout.setStretch(0, 1)
        self.settingusermanuallayout.setStretch(1, 1)
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
        self.page2boxLayout = QVBoxLayout()
        self.page2boxLayout.addWidget(self.page2Layout)
        self.page2boxLayout.setStretch(1, 1)
        self.page2.setLayout(self.page2boxLayout)
        self.page3boxLayout = QVBoxLayout()
        self.page3boxLayout.addWidget(self.page3Layout)
        self.page3boxLayout.addWidget(self.page2frame)
        self.page3boxLayout.setStretch(0, 2)
        self.page3boxLayout.setStretch(1, 2)
        self.page3.setLayout(self.page3boxLayout)
