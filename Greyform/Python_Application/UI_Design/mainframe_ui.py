# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\MokZhiZhuan\OneDrive - WINSYS TECHNOLOGY PTE LTD\Documents\GitHub\GreyForm_UI\Greyform\Python_Application\UI_Design\mainframe.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.stackedWidget_main = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget_main.setGeometry(QtCore.QRect(0, 10, 800, 600))
        self.stackedWidget_main.setObjectName("stackedWidget_main")
        self.mainconfiguration = QtWidgets.QWidget()
        self.mainconfiguration.setObjectName("mainconfiguration")
        self.SettingButton = QtWidgets.QPushButton(self.mainconfiguration)
        self.SettingButton.setGeometry(QtCore.QRect(620, 10, 151, 51))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SettingButton.sizePolicy().hasHeightForWidth())
        self.SettingButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.SettingButton.setFont(font)
        self.SettingButton.setObjectName("SettingButton")
        self.stackedWidget = QtWidgets.QStackedWidget(self.mainconfiguration)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 79, 800, 481))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.stackedWidget.setFont(font)
        self.stackedWidget.setObjectName("stackedWidget")
        self.mainmenu = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainmenu.sizePolicy().hasHeightForWidth())
        self.mainmenu.setSizePolicy(sizePolicy)
        self.mainmenu.setObjectName("mainmenu")
        self.QTitle = QtWidgets.QLabel(self.mainmenu)
        self.QTitle.setGeometry(QtCore.QRect(40, 170, 707, 55))
        self.QTitle.setScaledContents(False)
        self.QTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.QTitle.setObjectName("QTitle")
        self.layoutWidget = QtWidgets.QWidget(self.mainmenu)
        self.layoutWidget.setGeometry(QtCore.QRect(40, 400, 709, 71))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.menuStartButton = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.menuStartButton.sizePolicy().hasHeightForWidth())
        self.menuStartButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.menuStartButton.setFont(font)
        self.menuStartButton.setCheckable(False)
        self.menuStartButton.setObjectName("menuStartButton")
        self.horizontalLayout.addWidget(self.menuStartButton)
        self.menuCloseButton = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.menuCloseButton.sizePolicy().hasHeightForWidth())
        self.menuCloseButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.menuCloseButton.setFont(font)
        self.menuCloseButton.setCheckable(False)
        self.menuCloseButton.setObjectName("menuCloseButton")
        self.horizontalLayout.addWidget(self.menuCloseButton)
        self.stackedWidget.addWidget(self.mainmenu)
        self.page = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.page.sizePolicy().hasHeightForWidth())
        self.page.setSizePolicy(sizePolicy)
        self.page.setObjectName("page")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.page)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 10, 791, 72))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout_18 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.excelfilpathtext = QtWidgets.QTextEdit(self.horizontalLayoutWidget)
        self.excelfilpathtext.setObjectName("excelfilpathtext")
        self.horizontalLayout_18.addWidget(self.excelfilpathtext)
        self.excelFilePathButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.excelFilePathButton.sizePolicy().hasHeightForWidth())
        self.excelFilePathButton.setSizePolicy(sizePolicy)
        self.excelFilePathButton.setObjectName("excelFilePathButton")
        self.horizontalLayout_18.addWidget(self.excelFilePathButton)
        self.horizontalLayout_18.setStretch(0, 2)
        self.horizontalLayout_18.setStretch(1, 1)
        self.horizontalLayoutWidgetPage2 = QtWidgets.QWidget(self.page)
        self.horizontalLayoutWidgetPage2.setGeometry(QtCore.QRect(0, 90, 791, 381))
        self.horizontalLayoutWidgetPage2.setObjectName("horizontalLayoutWidgetPage2")
        self.horizontalLayout_20 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidgetPage2)
        self.horizontalLayout_20.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_20.setObjectName("horizontalLayout_20")
        self.verticalLayout_17 = QtWidgets.QVBoxLayout()
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.Selectivefilelistview = QtWidgets.QListView(self.horizontalLayoutWidgetPage2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Selectivefilelistview.sizePolicy().hasHeightForWidth())
        self.Selectivefilelistview.setSizePolicy(sizePolicy)
        self.Selectivefilelistview.setObjectName("Selectivefilelistview")
        self.verticalLayout_17.addWidget(self.Selectivefilelistview)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.FilePathButton = QtWidgets.QPushButton(self.horizontalLayoutWidgetPage2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FilePathButton.sizePolicy().hasHeightForWidth())
        self.FilePathButton.setSizePolicy(sizePolicy)
        self.FilePathButton.setObjectName("FilePathButton")
        self.horizontalLayout_8.addWidget(self.FilePathButton)
        self.BacktoMenuButton = QtWidgets.QPushButton(self.horizontalLayoutWidgetPage2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BacktoMenuButton.sizePolicy().hasHeightForWidth())
        self.BacktoMenuButton.setSizePolicy(sizePolicy)
        self.BacktoMenuButton.setObjectName("BacktoMenuButton")
        self.horizontalLayout_8.addWidget(self.BacktoMenuButton)
        self.NextButton_Page_2 = QtWidgets.QPushButton(self.horizontalLayoutWidgetPage2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.NextButton_Page_2.sizePolicy().hasHeightForWidth())
        self.NextButton_Page_2.setSizePolicy(sizePolicy)
        self.NextButton_Page_2.setObjectName("NextButton_Page_2")
        self.horizontalLayout_8.addWidget(self.NextButton_Page_2)
        self.verticalLayout_17.addLayout(self.horizontalLayout_8)
        self.verticalLayout_17.setStretch(0, 2)
        self.verticalLayout_17.setStretch(1, 1)
        self.horizontalLayout_20.addLayout(self.verticalLayout_17)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pyvistaframe = QtWidgets.QFrame(self.horizontalLayoutWidgetPage2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pyvistaframe.sizePolicy().hasHeightForWidth())
        self.pyvistaframe.setSizePolicy(sizePolicy)
        self.pyvistaframe.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.pyvistaframe.setFrameShadow(QtWidgets.QFrame.Raised)
        self.pyvistaframe.setObjectName("pyvistaframe")
        self.horizontalLayout_2.addWidget(self.pyvistaframe)
        self.horizontalLayout_20.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_20.setStretch(0, 1)
        self.horizontalLayout_20.setStretch(1, 1)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.page_2.sizePolicy().hasHeightForWidth())
        self.page_2.setSizePolicy(sizePolicy)
        self.page_2.setObjectName("page_2")
        self.Itemlabel = QtWidgets.QLabel(self.page_2)
        self.Itemlabel.setGeometry(QtCore.QRect(10, 10, 781, 17))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Itemlabel.sizePolicy().hasHeightForWidth())
        self.Itemlabel.setSizePolicy(sizePolicy)
        self.Itemlabel.setObjectName("Itemlabel")
        self.layoutWidgetpage3 = QtWidgets.QWidget(self.page_2)
        self.layoutWidgetpage3.setGeometry(QtCore.QRect(0, 30, 801, 451))
        self.layoutWidgetpage3.setObjectName("layoutWidgetpage3")
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout(self.layoutWidgetpage3)
        self.horizontalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_18 = QtWidgets.QVBoxLayout()
        self.verticalLayout_18.setObjectName("verticalLayout_18")
        self.seq1Button = QtWidgets.QPushButton(self.layoutWidgetpage3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.seq1Button.sizePolicy().hasHeightForWidth())
        self.seq1Button.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(30)
        self.seq1Button.setFont(font)
        self.seq1Button.setObjectName("seq1Button")
        self.verticalLayout_18.addWidget(self.seq1Button)
        self.seq2Button = QtWidgets.QPushButton(self.layoutWidgetpage3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.seq2Button.sizePolicy().hasHeightForWidth())
        self.seq2Button.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(30)
        self.seq2Button.setFont(font)
        self.seq2Button.setObjectName("seq2Button")
        self.verticalLayout_18.addWidget(self.seq2Button)
        self.seq3Button = QtWidgets.QPushButton(self.layoutWidgetpage3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.seq3Button.sizePolicy().hasHeightForWidth())
        self.seq3Button.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(30)
        self.seq3Button.setFont(font)
        self.seq3Button.setObjectName("seq3Button")
        self.verticalLayout_18.addWidget(self.seq3Button)
        self.verticalLayout_18.setStretch(0, 1)
        self.verticalLayout_18.setStretch(1, 1)
        self.verticalLayout_18.setStretch(2, 1)
        self.verticalLayout_4.addLayout(self.verticalLayout_18)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.NextButton_Page_3 = QtWidgets.QPushButton(self.layoutWidgetpage3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.NextButton_Page_3.sizePolicy().hasHeightForWidth())
        self.NextButton_Page_3.setSizePolicy(sizePolicy)
        self.NextButton_Page_3.setObjectName("NextButton_Page_3")
        self.horizontalLayout_9.addWidget(self.NextButton_Page_3)
        self.BackButton_Page_2 = QtWidgets.QPushButton(self.layoutWidgetpage3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BackButton_Page_2.sizePolicy().hasHeightForWidth())
        self.BackButton_Page_2.setSizePolicy(sizePolicy)
        self.BackButton_Page_2.setObjectName("BackButton_Page_2")
        self.horizontalLayout_9.addWidget(self.BackButton_Page_2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_9)
        self.verticalLayout_4.setStretch(0, 2)
        self.verticalLayout_4.setStretch(1, 1)
        self.horizontalLayout_16.addLayout(self.verticalLayout_4)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pyvistaframe_2 = QtWidgets.QFrame(self.layoutWidgetpage3)
        self.pyvistaframe_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.pyvistaframe_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.pyvistaframe_2.setObjectName("pyvistaframe_2")
        self.horizontalLayout_4.addWidget(self.pyvistaframe_2)
        self.horizontalLayout_16.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_16.setStretch(0, 1)
        self.horizontalLayout_16.setStretch(1, 1)
        self.stackedWidget.addWidget(self.page_2)
        self.page_3 = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.page_3.sizePolicy().hasHeightForWidth())
        self.page_3.setSizePolicy(sizePolicy)
        self.page_3.setObjectName("page_3")
        self.horizontalLayoutWidgetpage4 = QtWidgets.QWidget(self.page_3)
        self.horizontalLayoutWidgetpage4.setGeometry(QtCore.QRect(0, 280, 791, 201))
        self.horizontalLayoutWidgetpage4.setObjectName("horizontalLayoutWidgetpage4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidgetpage4)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_17.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout_21 = QtWidgets.QVBoxLayout()
        self.verticalLayout_21.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.verticalLayout_21.setObjectName("verticalLayout_21")
        self.Seqlabel = QtWidgets.QLabel(self.horizontalLayoutWidgetpage4)
        self.Seqlabel.setObjectName("Seqlabel")
        self.verticalLayout_21.addWidget(self.Seqlabel)
        self.Itemlabel_2 = QtWidgets.QLabel(self.horizontalLayoutWidgetpage4)
        self.Itemlabel_2.setWordWrap(True)
        self.Itemlabel_2.setObjectName("Itemlabel_2")
        self.verticalLayout_21.addWidget(self.Itemlabel_2)
        self.horizontalLayout_19 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_19.setObjectName("horizontalLayout_19")
        self.verticalLayout_21.addLayout(self.horizontalLayout_19)
        self.verticalLayout_21.setStretch(0, 1)
        self.verticalLayout_21.setStretch(1, 1)
        self.verticalLayout_6.addLayout(self.verticalLayout_21)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.ConfirmButton = QtWidgets.QPushButton(self.horizontalLayoutWidgetpage4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ConfirmButton.sizePolicy().hasHeightForWidth())
        self.ConfirmButton.setSizePolicy(sizePolicy)
        self.ConfirmButton.setObjectName("ConfirmButton")
        self.horizontalLayout_10.addWidget(self.ConfirmButton)
        self.BackButton_2 = QtWidgets.QPushButton(self.horizontalLayoutWidgetpage4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BackButton_2.sizePolicy().hasHeightForWidth())
        self.BackButton_2.setSizePolicy(sizePolicy)
        self.BackButton_2.setObjectName("BackButton_2")
        self.horizontalLayout_10.addWidget(self.BackButton_2)
        self.horizontalLayout_10.setStretch(0, 1)
        self.horizontalLayout_10.setStretch(1, 1)
        self.verticalLayout_6.addLayout(self.horizontalLayout_10)
        self.verticalLayout_6.setStretch(0, 2)
        self.verticalLayout_6.setStretch(1, 1)
        self.horizontalLayout_17.addLayout(self.verticalLayout_6)
        self.horizontalLayout_3.addLayout(self.horizontalLayout_17)
        self.verticalLayout_22 = QtWidgets.QVBoxLayout()
        self.verticalLayout_22.setObjectName("verticalLayout_22")
        self.label_2 = QtWidgets.QLabel(self.horizontalLayoutWidgetpage4)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_22.addWidget(self.label_2)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.titleXlabel = QtWidgets.QLabel(self.horizontalLayoutWidgetpage4)
        self.titleXlabel.setObjectName("titleXlabel")
        self.horizontalLayout_13.addWidget(self.titleXlabel)
        self.Xlabel = QtWidgets.QLabel(self.horizontalLayoutWidgetpage4)
        self.Xlabel.setObjectName("Xlabel")
        self.horizontalLayout_13.addWidget(self.Xlabel)
        self.verticalLayout_22.addLayout(self.horizontalLayout_13)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.titleYlabel = QtWidgets.QLabel(self.horizontalLayoutWidgetpage4)
        self.titleYlabel.setObjectName("titleYlabel")
        self.horizontalLayout_14.addWidget(self.titleYlabel)
        self.Ylabel = QtWidgets.QLabel(self.horizontalLayoutWidgetpage4)
        self.Ylabel.setObjectName("Ylabel")
        self.horizontalLayout_14.addWidget(self.Ylabel)
        self.verticalLayout_22.addLayout(self.horizontalLayout_14)
        self.verticalLayout_22.setStretch(0, 1)
        self.verticalLayout_22.setStretch(1, 1)
        self.verticalLayout_22.setStretch(2, 1)
        self.horizontalLayout_3.addLayout(self.verticalLayout_22)
        self.verticalLayout_20 = QtWidgets.QVBoxLayout()
        self.verticalLayout_20.setObjectName("verticalLayout_20")
        self.displaybeforelabel = QtWidgets.QLabel(self.horizontalLayoutWidgetpage4)
        self.displaybeforelabel.setObjectName("displaybeforelabel")
        self.verticalLayout_20.addWidget(self.displaybeforelabel)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.titleXlabel_2 = QtWidgets.QLabel(self.horizontalLayoutWidgetpage4)
        self.titleXlabel_2.setWordWrap(True)
        self.titleXlabel_2.setObjectName("titleXlabel_2")
        self.horizontalLayout_5.addWidget(self.titleXlabel_2)
        self.Xlabel_2 = QtWidgets.QLabel(self.horizontalLayoutWidgetpage4)
        self.Xlabel_2.setWordWrap(True)
        self.Xlabel_2.setObjectName("Xlabel_2")
        self.horizontalLayout_5.addWidget(self.Xlabel_2)
        self.verticalLayout_20.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.titleYlabel_2 = QtWidgets.QLabel(self.horizontalLayoutWidgetpage4)
        self.titleYlabel_2.setWordWrap(True)
        self.titleYlabel_2.setObjectName("titleYlabel_2")
        self.horizontalLayout_6.addWidget(self.titleYlabel_2)
        self.Ylabel_2 = QtWidgets.QLabel(self.horizontalLayoutWidgetpage4)
        self.Ylabel_2.setWordWrap(True)
        self.Ylabel_2.setObjectName("Ylabel_2")
        self.horizontalLayout_6.addWidget(self.Ylabel_2)
        self.verticalLayout_20.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.titleZlabel = QtWidgets.QLabel(self.horizontalLayoutWidgetpage4)
        self.titleZlabel.setWordWrap(True)
        self.titleZlabel.setObjectName("titleZlabel")
        self.horizontalLayout_7.addWidget(self.titleZlabel)
        self.Zlabel = QtWidgets.QLabel(self.horizontalLayoutWidgetpage4)
        self.Zlabel.setWordWrap(True)
        self.Zlabel.setObjectName("Zlabel")
        self.horizontalLayout_7.addWidget(self.Zlabel)
        self.verticalLayout_20.addLayout(self.horizontalLayout_7)
        self.verticalLayout_20.setStretch(0, 1)
        self.verticalLayout_20.setStretch(1, 1)
        self.verticalLayout_20.setStretch(2, 1)
        self.verticalLayout_20.setStretch(3, 1)
        self.horizontalLayout_3.addLayout(self.verticalLayout_20)
        self.horizontalLayout_3.setStretch(0, 2)
        self.horizontalLayout_3.setStretch(1, 1)
        self.horizontalLayout_3.setStretch(2, 1)
        self.layoutWidgetpage4 = QtWidgets.QWidget(self.page_3)
        self.layoutWidgetpage4.setGeometry(QtCore.QRect(10, 20, 781, 251))
        self.layoutWidgetpage4.setObjectName("layoutWidgetpage4")
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout(self.layoutWidgetpage4)
        self.horizontalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.vtkframe = QtWidgets.QFrame(self.layoutWidgetpage4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.vtkframe.sizePolicy().hasHeightForWidth())
        self.vtkframe.setSizePolicy(sizePolicy)
        self.vtkframe.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.vtkframe.setFrameShadow(QtWidgets.QFrame.Raised)
        self.vtkframe.setObjectName("vtkframe")
        self.verticalLayout.addWidget(self.vtkframe)
        self.horizontalLayout_15.addLayout(self.verticalLayout)
        self.LocalizationButton = QtWidgets.QPushButton(self.layoutWidgetpage4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LocalizationButton.sizePolicy().hasHeightForWidth())
        self.LocalizationButton.setSizePolicy(sizePolicy)
        self.LocalizationButton.setObjectName("LocalizationButton")
        self.horizontalLayout_15.addWidget(self.LocalizationButton)
        self.horizontalLayout_15.setStretch(0, 2)
        self.horizontalLayout_15.setStretch(1, 1)
        self.stackedWidget.addWidget(self.page_3)
        self.page_4 = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.page_4.sizePolicy().hasHeightForWidth())
        self.page_4.setSizePolicy(sizePolicy)
        self.page_4.setObjectName("page_4")
        self.layoutWidgetpage5 = QtWidgets.QWidget(self.page_4)
        self.layoutWidgetpage5.setGeometry(QtCore.QRect(0, 10, 791, 471))
        self.layoutWidgetpage5.setObjectName("layoutWidgetpage5")
        self.verticalLayout_23 = QtWidgets.QVBoxLayout(self.layoutWidgetpage5)
        self.verticalLayout_23.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_23.setObjectName("verticalLayout_23")
        self.MarkingButton = QtWidgets.QPushButton(self.layoutWidgetpage5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MarkingButton.sizePolicy().hasHeightForWidth())
        self.MarkingButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(40)
        self.MarkingButton.setFont(font)
        self.MarkingButton.setObjectName("MarkingButton")
        self.verticalLayout_23.addWidget(self.MarkingButton)
        self.verticalLayout_24 = QtWidgets.QVBoxLayout()
        self.verticalLayout_24.setObjectName("verticalLayout_24")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.HomeButton = QtWidgets.QPushButton(self.layoutWidgetpage5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.HomeButton.sizePolicy().hasHeightForWidth())
        self.HomeButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(40)
        self.HomeButton.setFont(font)
        self.HomeButton.setObjectName("HomeButton")
        self.horizontalLayout_11.addWidget(self.HomeButton)
        self.horizontalLayout_11.setStretch(0, 1)
        self.verticalLayout_24.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.CloseButton = QtWidgets.QPushButton(self.layoutWidgetpage5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CloseButton.sizePolicy().hasHeightForWidth())
        self.CloseButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(40)
        self.CloseButton.setFont(font)
        self.CloseButton.setObjectName("CloseButton")
        self.horizontalLayout_12.addWidget(self.CloseButton)
        self.ConfirmAckButton = QtWidgets.QPushButton(self.layoutWidgetpage5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ConfirmAckButton.sizePolicy().hasHeightForWidth())
        self.ConfirmAckButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(40)
        self.ConfirmAckButton.setFont(font)
        self.ConfirmAckButton.setObjectName("ConfirmAckButton")
        self.horizontalLayout_12.addWidget(self.ConfirmAckButton)
        self.horizontalLayout_12.setStretch(0, 1)
        self.horizontalLayout_12.setStretch(1, 1)
        self.verticalLayout_24.addLayout(self.horizontalLayout_12)
        self.verticalLayout_24.setStretch(0, 1)
        self.verticalLayout_24.setStretch(1, 1)
        self.verticalLayout_23.addLayout(self.verticalLayout_24)
        self.verticalLayout_23.setStretch(0, 1)
        self.verticalLayout_23.setStretch(1, 1)
        self.stackedWidget.addWidget(self.page_4)
        self.usermanualButton = QtWidgets.QPushButton(self.mainconfiguration)
        self.usermanualButton.setGeometry(QtCore.QRect(20, 10, 151, 51))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.usermanualButton.sizePolicy().hasHeightForWidth())
        self.usermanualButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.usermanualButton.setFont(font)
        self.usermanualButton.setObjectName("usermanualButton")
        self.stackedWidget_main.addWidget(self.mainconfiguration)
        self.settingpage = QtWidgets.QWidget()
        self.settingpage.setObjectName("settingpage")
        self.stackedWidget_main.addWidget(self.settingpage)
        self.usermanualpage = QtWidgets.QWidget()
        self.usermanualpage.setObjectName("usermanualpage")
        self.stackedWidget_main.addWidget(self.usermanualpage)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "mainframe"))
        self.SettingButton.setText(_translate("MainWindow", "Setting"))
        self.QTitle.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:36pt;\">Automated PBU Robot UI</span></p></body></html>"))
        self.menuStartButton.setText(_translate("MainWindow", "Continue"))
        self.menuCloseButton.setText(_translate("MainWindow", "Exit"))
        self.excelFilePathButton.setText(_translate("MainWindow", "Insert Excel File"))
        self.FilePathButton.setText(_translate("MainWindow", "File_Path"))
        self.BacktoMenuButton.setText(_translate("MainWindow", "Back To Menu"))
        self.NextButton_Page_2.setText(_translate("MainWindow", "Next"))
        self.Itemlabel.setText(_translate("MainWindow", "Product :"))
        self.seq1Button.setText(_translate("MainWindow", "Stage 1"))
        self.seq2Button.setText(_translate("MainWindow", "Stage 2"))
        self.seq3Button.setText(_translate("MainWindow", "Stage 3"))
        self.NextButton_Page_3.setText(_translate("MainWindow", "Next"))
        self.BackButton_Page_2.setText(_translate("MainWindow", "Back"))
        self.Seqlabel.setText(_translate("MainWindow", "Sequence:"))
        self.Itemlabel_2.setText(_translate("MainWindow", "Product:"))
        self.ConfirmButton.setText(_translate("MainWindow", "Confirm"))
        self.BackButton_2.setText(_translate("MainWindow", "Back"))
        self.label_2.setText(_translate("MainWindow", "Click Mouse Display"))
        self.titleXlabel.setText(_translate("MainWindow", "Width:"))
        self.Xlabel.setText(_translate("MainWindow", "800"))
        self.titleYlabel.setText(_translate("MainWindow", "Height:"))
        self.Ylabel.setText(_translate("MainWindow", "800"))
        self.displaybeforelabel.setText(_translate("MainWindow", "Camera Display"))
        self.titleXlabel_2.setText(_translate("MainWindow", "Width:"))
        self.Xlabel_2.setText(_translate("MainWindow", "800"))
        self.titleYlabel_2.setText(_translate("MainWindow", "Height:"))
        self.Ylabel_2.setText(_translate("MainWindow", "800"))
        self.titleZlabel.setText(_translate("MainWindow", "Length:"))
        self.Zlabel.setText(_translate("MainWindow", "800"))
        self.LocalizationButton.setText(_translate("MainWindow", "Localization"))
        self.MarkingButton.setText(_translate("MainWindow", "Back to Marking"))
        self.HomeButton.setText(_translate("MainWindow", "Home"))
        self.CloseButton.setText(_translate("MainWindow", "Abort/Close"))
        self.ConfirmAckButton.setText(_translate("MainWindow", "Acknowledge"))
        self.usermanualButton.setText(_translate("MainWindow", "User Manual"))
