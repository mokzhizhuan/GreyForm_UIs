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
        filedirectorylayout,
        buttonfiledirectorylayout,
        page2,
        itemlabel_page3,
        page3layout,
        buttonpage3layout,
        page3,
        labelstatus,
        scanprogressBar,
        scanpage,
        page4layout,
        page4frame,
        page4,
        sendmodelButton,
        CloseButton,
        ChooseButton,
        page5,
    ):
        # starting initialize
        super().__init__()
        self.stackedWidget = stackedWidget
        self.maintitle = maintitle
        self.mainlayoutwidget = mainlayoutwidget
        self.mainlayoutpagebutton = mainlayoutpagebutton
        self.mainmenu = mainmenu
        self.filedirectorylayout = filedirectorylayout
        self.buttonfiledirrectorylayout = buttonfiledirectorylayout
        self.page2 = page2
        self.itemlabel_page3 = itemlabel_page3
        self.page3Layout = page3layout
        self.buttonpage3layout = buttonpage3layout
        self.page3 = page3
        self.labelstatus = labelstatus
        self.scanprogressBar = scanprogressBar
        self.scanpage = scanpage
        self.page4Layout = page4layout
        self.page4frame = page4frame
        self.page4 = page4
        self.page5 = page5
        self.sendmodelButton = sendmodelButton
        self.CloseButton = CloseButton
        self.ChooseButton = ChooseButton
        self.setStretch()

    #stretch layout
    def setStretch(self):
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
        self.page2boxLayout.addWidget(self.filedirectorylayout)
        self.page2boxLayout.addWidget(self.buttonfiledirrectorylayout)
        self.page2boxLayout.setStretch(0, 3)
        self.page2boxLayout.setStretch(1, 1)
        self.page2.setLayout(self.page2boxLayout)
        self.page3boxLayout = QVBoxLayout()
        self.page3boxLayout.addWidget(self.itemlabel_page3)
        self.page3boxLayout.addWidget(self.page3Layout)
        self.page3boxLayout.addWidget(self.buttonpage3layout)
        self.page3boxLayout.setStretch(0, 1)
        self.page3boxLayout.setStretch(1, 4)
        self.page3boxLayout.setStretch(2, 1)
        self.page3.setLayout(self.page3boxLayout)
        self.scaningbox = QVBoxLayout()
        self.verticalSpacer_3 = QSpacerItem(
            20, 400, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        self.verticalSpacer_4 = QSpacerItem(
            20, 220, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        self.scaningbox.addItem(self.verticalSpacer_3)
        self.scaningbox.addWidget(self.labelstatus)
        self.scaningbox.addWidget(self.scanprogressBar)
        self.scaningbox.addItem(self.verticalSpacer_4)
        self.scaningbox.setStretch(0, 3)
        self.scaningbox.setStretch(1, 1)
        self.scaningbox.setStretch(2, 1)
        self.scaningbox.setStretch(3, 3)
        self.scanpage.setLayout(self.scaningbox)
        self.page4boxLayout = QVBoxLayout()
        self.page4boxLayout.addWidget(self.page4Layout)
        self.page4boxLayout.addWidget(self.page4frame)
        self.page4boxLayout.setStretch(0, 1)
        self.page4boxLayout.setStretch(1, 1)
        self.page4.setLayout(self.page4boxLayout)
        self.page5boxLayout = QVBoxLayout()
        self.page5boxLayout.addWidget(self.sendmodelButton)
        self.page5boxLayout.addWidget(self.ChooseButton)
        self.page5boxLayout.addWidget(self.CloseButton) 
        self.page5boxLayout.setStretch(0, 1)
        self.page5boxLayout.setStretch(1, 1)
        self.page5boxLayout.setStretch(2, 1)
        self.page5.setLayout(self.page5boxLayout)


