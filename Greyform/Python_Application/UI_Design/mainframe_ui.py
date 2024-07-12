# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainframe.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGroupBox, QHBoxLayout,
    QLabel, QLayout, QListView, QMainWindow,
    QPushButton, QSizePolicy, QStackedWidget, QStatusBar,
    QVBoxLayout, QWidget)
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setGeometry(QRect(0, 0, 800, 600))
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(11)
        self.stackedWidget.setFont(font)
        self.mainmenu = QWidget()
        self.mainmenu.setObjectName(u"mainmenu")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.mainmenu.sizePolicy().hasHeightForWidth())
        self.mainmenu.setSizePolicy(sizePolicy1)
        self.QTitle = QLabel(self.mainmenu)
        self.QTitle.setObjectName(u"QTitle")
        self.QTitle.setGeometry(QRect(40, 230, 707, 55))
        self.QTitle.setScaledContents(False)
        self.QTitle.setAlignment(Qt.AlignCenter)
        self.layoutWidget = QWidget(self.mainmenu)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(40, 550, 709, 27))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.menuStartButton = QPushButton(self.layoutWidget)
        self.menuStartButton.setObjectName(u"menuStartButton")
        self.menuStartButton.setCheckable(False)

        self.horizontalLayout.addWidget(self.menuStartButton)

        self.menuCloseButton = QPushButton(self.layoutWidget)
        self.menuCloseButton.setObjectName(u"menuCloseButton")
        self.menuCloseButton.setCheckable(False)

        self.horizontalLayout.addWidget(self.menuCloseButton)

        self.stackedWidget.addWidget(self.mainmenu)
        self.page = QWidget()
        self.page.setObjectName(u"page")
        sizePolicy1.setHeightForWidth(self.page.sizePolicy().hasHeightForWidth())
        self.page.setSizePolicy(sizePolicy1)
        self.layoutWidgetpage2 = QWidget(self.page)
        self.layoutWidgetpage2.setObjectName(u"layoutWidgetpage2")
        self.layoutWidgetpage2.setGeometry(QRect(0, 10, 331, 559))
        self.verticalLayout_17 = QVBoxLayout(self.layoutWidgetpage2)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.Selectivefilelistview = QListView(self.layoutWidgetpage2)
        self.Selectivefilelistview.setObjectName(u"Selectivefilelistview")

        self.verticalLayout_17.addWidget(self.Selectivefilelistview)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.FilePathButton = QPushButton(self.layoutWidgetpage2)
        self.FilePathButton.setObjectName(u"FilePathButton")

        self.horizontalLayout_8.addWidget(self.FilePathButton)

        self.BacktoMenuButton = QPushButton(self.layoutWidgetpage2)
        self.BacktoMenuButton.setObjectName(u"BacktoMenuButton")

        self.horizontalLayout_8.addWidget(self.BacktoMenuButton)

        self.NextButton_Page_2 = QPushButton(self.layoutWidgetpage2)
        self.NextButton_Page_2.setObjectName(u"NextButton_Page_2")

        self.horizontalLayout_8.addWidget(self.NextButton_Page_2)

        self.horizontalLayout_8.setStretch(0, 1)
        self.horizontalLayout_8.setStretch(1, 1)
        self.horizontalLayout_8.setStretch(2, 1)

        self.verticalLayout_17.addLayout(self.horizontalLayout_8)

        self.layoutWidgetframe = QWidget(self.page)
        self.layoutWidgetframe.setObjectName(u"layoutWidgetframe")
        self.layoutWidgetframe.setGeometry(QRect(340, 10, 451, 559))
        self.horizontalLayout_2 = QHBoxLayout(self.layoutWidgetframe)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.pyvistaframe = QFrame(self.layoutWidgetframe)
        self.pyvistaframe.setObjectName(u"pyvistaframe")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pyvistaframe.sizePolicy().hasHeightForWidth())
        self.pyvistaframe.setSizePolicy(sizePolicy2)
        self.pyvistaframe.setFrameShape(QFrame.StyledPanel)
        self.pyvistaframe.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_2.addWidget(self.pyvistaframe)

        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        sizePolicy1.setHeightForWidth(self.page_2.sizePolicy().hasHeightForWidth())
        self.page_2.setSizePolicy(sizePolicy1)
        self.Itemlabel = QLabel(self.page_2)
        self.Itemlabel.setObjectName(u"Itemlabel")
        self.Itemlabel.setGeometry(QRect(10, 10, 797, 17))
        sizePolicy2.setHeightForWidth(self.Itemlabel.sizePolicy().hasHeightForWidth())
        self.Itemlabel.setSizePolicy(sizePolicy2)
        self.layoutWidgetpage3 = QWidget(self.page_2)
        self.layoutWidgetpage3.setObjectName(u"layoutWidgetpage3")
        self.layoutWidgetpage3.setGeometry(QRect(0, 30, 801, 541))
        self.horizontalLayout_16 = QHBoxLayout(self.layoutWidgetpage3)
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.horizontalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_18 = QVBoxLayout()
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.seq1Button = QPushButton(self.layoutWidgetpage3)
        self.seq1Button.setObjectName(u"seq1Button")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.seq1Button.sizePolicy().hasHeightForWidth())
        self.seq1Button.setSizePolicy(sizePolicy3)
        font1 = QFont()
        font1.setPointSize(30)
        self.seq1Button.setFont(font1)

        self.verticalLayout_18.addWidget(self.seq1Button)

        self.seq2Button = QPushButton(self.layoutWidgetpage3)
        self.seq2Button.setObjectName(u"seq2Button")
        sizePolicy3.setHeightForWidth(self.seq2Button.sizePolicy().hasHeightForWidth())
        self.seq2Button.setSizePolicy(sizePolicy3)
        self.seq2Button.setFont(font1)

        self.verticalLayout_18.addWidget(self.seq2Button)

        self.seq3Button = QPushButton(self.layoutWidgetpage3)
        self.seq3Button.setObjectName(u"seq3Button")
        sizePolicy3.setHeightForWidth(self.seq3Button.sizePolicy().hasHeightForWidth())
        self.seq3Button.setSizePolicy(sizePolicy3)
        self.seq3Button.setFont(font1)

        self.verticalLayout_18.addWidget(self.seq3Button)

        self.verticalLayout_18.setStretch(0, 1)
        self.verticalLayout_18.setStretch(1, 1)
        self.verticalLayout_18.setStretch(2, 1)

        self.verticalLayout_4.addLayout(self.verticalLayout_18)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.NextButton_Page_3 = QPushButton(self.layoutWidgetpage3)
        self.NextButton_Page_3.setObjectName(u"NextButton_Page_3")

        self.horizontalLayout_9.addWidget(self.NextButton_Page_3)

        self.BackButton_Page_2 = QPushButton(self.layoutWidgetpage3)
        self.BackButton_Page_2.setObjectName(u"BackButton_Page_2")

        self.horizontalLayout_9.addWidget(self.BackButton_Page_2)


        self.verticalLayout_4.addLayout(self.horizontalLayout_9)


        self.horizontalLayout_16.addLayout(self.verticalLayout_4)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.pyvistaframe_2 = QFrame(self.layoutWidgetpage3)
        self.pyvistaframe_2.setObjectName(u"pyvistaframe_2")
        self.pyvistaframe_2.setFrameShape(QFrame.StyledPanel)
        self.pyvistaframe_2.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_4.addWidget(self.pyvistaframe_2)


        self.horizontalLayout_16.addLayout(self.horizontalLayout_4)

        self.stackedWidget.addWidget(self.page_2)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        sizePolicy1.setHeightForWidth(self.page_3.sizePolicy().hasHeightForWidth())
        self.page_3.setSizePolicy(sizePolicy1)
        self.layoutWidgetpage4 = QWidget(self.page_3)
        self.layoutWidgetpage4.setObjectName(u"layoutWidgetpage4")
        self.layoutWidgetpage4.setGeometry(QRect(10, 10, 781, 351))
        self.verticalLayout = QVBoxLayout(self.layoutWidgetpage4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.vtkframe = QFrame(self.layoutWidgetpage4)
        self.vtkframe.setObjectName(u"vtkframe")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy4.setHorizontalStretch(5)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.vtkframe.sizePolicy().hasHeightForWidth())
        self.vtkframe.setSizePolicy(sizePolicy4)
        self.vtkframe.setFrameShape(QFrame.StyledPanel)
        self.vtkframe.setFrameShadow(QFrame.Raised)

        self.verticalLayout.addWidget(self.vtkframe)

        self.horizontalLayoutWidgetpage4 = QWidget(self.page_3)
        self.horizontalLayoutWidgetpage4.setObjectName(u"horizontalLayoutWidgetpage4")
        self.horizontalLayoutWidgetpage4.setGeometry(QRect(10, 370, 781, 201))
        self.horizontalLayout_3 = QHBoxLayout(self.horizontalLayoutWidgetpage4)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.horizontalLayout_17.setSizeConstraint(QLayout.SetNoConstraint)
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_21 = QVBoxLayout()
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.verticalLayout_21.setSizeConstraint(QLayout.SetNoConstraint)
        self.Seqlabel = QLabel(self.horizontalLayoutWidgetpage4)
        self.Seqlabel.setObjectName(u"Seqlabel")

        self.verticalLayout_21.addWidget(self.Seqlabel)

        self.Itemlabel_2 = QLabel(self.horizontalLayoutWidgetpage4)
        self.Itemlabel_2.setObjectName(u"Itemlabel_2")
        self.Itemlabel_2.setWordWrap(True)

        self.verticalLayout_21.addWidget(self.Itemlabel_2)

        self.verticalLayout_21.setStretch(0, 1)
        self.verticalLayout_21.setStretch(1, 1)

        self.verticalLayout_6.addLayout(self.verticalLayout_21)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.ConfirmButton = QPushButton(self.horizontalLayoutWidgetpage4)
        self.ConfirmButton.setObjectName(u"ConfirmButton")

        self.horizontalLayout_10.addWidget(self.ConfirmButton)

        self.BackButton_2 = QPushButton(self.horizontalLayoutWidgetpage4)
        self.BackButton_2.setObjectName(u"BackButton_2")

        self.horizontalLayout_10.addWidget(self.BackButton_2)

        self.horizontalLayout_10.setStretch(0, 1)
        self.horizontalLayout_10.setStretch(1, 1)

        self.verticalLayout_6.addLayout(self.horizontalLayout_10)


        self.horizontalLayout_17.addLayout(self.verticalLayout_6)


        self.horizontalLayout_3.addLayout(self.horizontalLayout_17)

        self.verticalLayout_22 = QVBoxLayout()
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.label_2 = QLabel(self.horizontalLayoutWidgetpage4)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_22.addWidget(self.label_2)

        self.Xgroupbox = QGroupBox(self.horizontalLayoutWidgetpage4)
        self.Xgroupbox.setObjectName(u"Xgroupbox")
        self.horizontalLayoutWidget_9 = QWidget(self.Xgroupbox)
        self.horizontalLayoutWidget_9.setObjectName(u"horizontalLayoutWidget_9")
        self.horizontalLayoutWidget_9.setGeometry(QRect(0, 0, 191, 61))
        self.horizontalLayout_13 = QHBoxLayout(self.horizontalLayoutWidget_9)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.titleXlabel = QLabel(self.horizontalLayoutWidget_9)
        self.titleXlabel.setObjectName(u"titleXlabel")

        self.horizontalLayout_13.addWidget(self.titleXlabel)

        self.Xlabel = QLabel(self.horizontalLayoutWidget_9)
        self.Xlabel.setObjectName(u"Xlabel")

        self.horizontalLayout_13.addWidget(self.Xlabel)


        self.verticalLayout_22.addWidget(self.Xgroupbox)

        self.Ygroupbox = QGroupBox(self.horizontalLayoutWidgetpage4)
        self.Ygroupbox.setObjectName(u"Ygroupbox")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.Ygroupbox.sizePolicy().hasHeightForWidth())
        self.Ygroupbox.setSizePolicy(sizePolicy5)
        self.horizontalLayoutWidget_10 = QWidget(self.Ygroupbox)
        self.horizontalLayoutWidget_10.setObjectName(u"horizontalLayoutWidget_10")
        self.horizontalLayoutWidget_10.setGeometry(QRect(0, 0, 191, 61))
        self.horizontalLayout_14 = QHBoxLayout(self.horizontalLayoutWidget_10)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.titleYlabel = QLabel(self.horizontalLayoutWidget_10)
        self.titleYlabel.setObjectName(u"titleYlabel")

        self.horizontalLayout_14.addWidget(self.titleYlabel)

        self.Ylabel = QLabel(self.horizontalLayoutWidget_10)
        self.Ylabel.setObjectName(u"Ylabel")

        self.horizontalLayout_14.addWidget(self.Ylabel)


        self.verticalLayout_22.addWidget(self.Ygroupbox)

        self.verticalLayout_22.setStretch(0, 1)
        self.verticalLayout_22.setStretch(1, 1)
        self.verticalLayout_22.setStretch(2, 1)

        self.horizontalLayout_3.addLayout(self.verticalLayout_22)

        self.verticalLayout_20 = QVBoxLayout()
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.displaybeforelabel = QLabel(self.horizontalLayoutWidgetpage4)
        self.displaybeforelabel.setObjectName(u"displaybeforelabel")

        self.verticalLayout_20.addWidget(self.displaybeforelabel)

        self.Xgroupbox_2 = QGroupBox(self.horizontalLayoutWidgetpage4)
        self.Xgroupbox_2.setObjectName(u"Xgroupbox_2")
        self.horizontalLayoutWidget_4 = QWidget(self.Xgroupbox_2)
        self.horizontalLayoutWidget_4.setObjectName(u"horizontalLayoutWidget_4")
        self.horizontalLayoutWidget_4.setGeometry(QRect(0, 0, 161, 51))
        self.horizontalLayout_5 = QHBoxLayout(self.horizontalLayoutWidget_4)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.titleXlabel_2 = QLabel(self.horizontalLayoutWidget_4)
        self.titleXlabel_2.setObjectName(u"titleXlabel_2")

        self.horizontalLayout_5.addWidget(self.titleXlabel_2)

        self.Xlabel_2 = QLabel(self.horizontalLayoutWidget_4)
        self.Xlabel_2.setObjectName(u"Xlabel_2")

        self.horizontalLayout_5.addWidget(self.Xlabel_2)


        self.verticalLayout_20.addWidget(self.Xgroupbox_2)

        self.Ygroupbox_2 = QGroupBox(self.horizontalLayoutWidgetpage4)
        self.Ygroupbox_2.setObjectName(u"Ygroupbox_2")
        sizePolicy5.setHeightForWidth(self.Ygroupbox_2.sizePolicy().hasHeightForWidth())
        self.Ygroupbox_2.setSizePolicy(sizePolicy5)
        self.horizontalLayoutWidget_7 = QWidget(self.Ygroupbox_2)
        self.horizontalLayoutWidget_7.setObjectName(u"horizontalLayoutWidget_7")
        self.horizontalLayoutWidget_7.setGeometry(QRect(0, 0, 161, 51))
        self.horizontalLayout_6 = QHBoxLayout(self.horizontalLayoutWidget_7)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.titleYlabel_2 = QLabel(self.horizontalLayoutWidget_7)
        self.titleYlabel_2.setObjectName(u"titleYlabel_2")

        self.horizontalLayout_6.addWidget(self.titleYlabel_2)

        self.Ylabel_2 = QLabel(self.horizontalLayoutWidget_7)
        self.Ylabel_2.setObjectName(u"Ylabel_2")

        self.horizontalLayout_6.addWidget(self.Ylabel_2)


        self.verticalLayout_20.addWidget(self.Ygroupbox_2)

        self.Zgroupbox = QGroupBox(self.horizontalLayoutWidgetpage4)
        self.Zgroupbox.setObjectName(u"Zgroupbox")
        sizePolicy5.setHeightForWidth(self.Zgroupbox.sizePolicy().hasHeightForWidth())
        self.Zgroupbox.setSizePolicy(sizePolicy5)
        self.horizontalLayoutWidget_8 = QWidget(self.Zgroupbox)
        self.horizontalLayoutWidget_8.setObjectName(u"horizontalLayoutWidget_8")
        self.horizontalLayoutWidget_8.setGeometry(QRect(0, 0, 161, 51))
        self.horizontalLayout_7 = QHBoxLayout(self.horizontalLayoutWidget_8)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.titleZlabel = QLabel(self.horizontalLayoutWidget_8)
        self.titleZlabel.setObjectName(u"titleZlabel")

        self.horizontalLayout_7.addWidget(self.titleZlabel)

        self.Zlabel = QLabel(self.horizontalLayoutWidget_8)
        self.Zlabel.setObjectName(u"Zlabel")

        self.horizontalLayout_7.addWidget(self.Zlabel)


        self.verticalLayout_20.addWidget(self.Zgroupbox)

        self.verticalLayout_20.setStretch(0, 1)
        self.verticalLayout_20.setStretch(1, 1)
        self.verticalLayout_20.setStretch(2, 1)
        self.verticalLayout_20.setStretch(3, 1)

        self.horizontalLayout_3.addLayout(self.verticalLayout_20)

        self.horizontalLayout_3.setStretch(0, 2)
        self.horizontalLayout_3.setStretch(1, 1)
        self.horizontalLayout_3.setStretch(2, 1)
        self.stackedWidget.addWidget(self.page_3)
        self.page_4 = QWidget()
        self.page_4.setObjectName(u"page_4")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy6.setHorizontalStretch(1)
        sizePolicy6.setVerticalStretch(1)
        sizePolicy6.setHeightForWidth(self.page_4.sizePolicy().hasHeightForWidth())
        self.page_4.setSizePolicy(sizePolicy6)
        self.SettingButton = QPushButton(self.page_4)
        self.SettingButton.setObjectName(u"SettingButton")
        self.SettingButton.setGeometry(QRect(700, 10, 80, 25))
        self.layoutWidgetpage5 = QWidget(self.page_4)
        self.layoutWidgetpage5.setObjectName(u"layoutWidgetpage5")
        self.layoutWidgetpage5.setGeometry(QRect(0, 40, 791, 531))
        self.verticalLayout_23 = QVBoxLayout(self.layoutWidgetpage5)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.verticalLayout_23.setContentsMargins(0, 0, 0, 0)
        self.MarkingButton = QPushButton(self.layoutWidgetpage5)
        self.MarkingButton.setObjectName(u"MarkingButton")
        sizePolicy3.setHeightForWidth(self.MarkingButton.sizePolicy().hasHeightForWidth())
        self.MarkingButton.setSizePolicy(sizePolicy3)
        font2 = QFont()
        font2.setPointSize(40)
        self.MarkingButton.setFont(font2)

        self.verticalLayout_23.addWidget(self.MarkingButton)

        self.verticalLayout_24 = QVBoxLayout()
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.HomeButton = QPushButton(self.layoutWidgetpage5)
        self.HomeButton.setObjectName(u"HomeButton")
        sizePolicy3.setHeightForWidth(self.HomeButton.sizePolicy().hasHeightForWidth())
        self.HomeButton.setSizePolicy(sizePolicy3)
        self.HomeButton.setFont(font2)

        self.horizontalLayout_11.addWidget(self.HomeButton)

        self.EnableRobotButton = QPushButton(self.layoutWidgetpage5)
        self.EnableRobotButton.setObjectName(u"EnableRobotButton")
        sizePolicy3.setHeightForWidth(self.EnableRobotButton.sizePolicy().hasHeightForWidth())
        self.EnableRobotButton.setSizePolicy(sizePolicy3)
        self.EnableRobotButton.setFont(font2)

        self.horizontalLayout_11.addWidget(self.EnableRobotButton)

        self.horizontalLayout_11.setStretch(0, 1)
        self.horizontalLayout_11.setStretch(1, 1)

        self.verticalLayout_24.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.CloseButton = QPushButton(self.layoutWidgetpage5)
        self.CloseButton.setObjectName(u"CloseButton")
        sizePolicy3.setHeightForWidth(self.CloseButton.sizePolicy().hasHeightForWidth())
        self.CloseButton.setSizePolicy(sizePolicy3)
        self.CloseButton.setFont(font2)

        self.horizontalLayout_12.addWidget(self.CloseButton)

        self.ConfirmAckButton = QPushButton(self.layoutWidgetpage5)
        self.ConfirmAckButton.setObjectName(u"ConfirmAckButton")
        sizePolicy3.setHeightForWidth(self.ConfirmAckButton.sizePolicy().hasHeightForWidth())
        self.ConfirmAckButton.setSizePolicy(sizePolicy3)
        self.ConfirmAckButton.setFont(font2)

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
        self.settingpage = QWidget()
        self.settingpage.setObjectName(u"settingpage")
        self.stackedWidget.addWidget(self.settingpage)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"mainframe", None))
        self.QTitle.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:36pt;\">Automated PBU Robot UI</span></p></body></html>", None))
        self.menuStartButton.setText(QCoreApplication.translate("MainWindow", u"Click to Continue", None))
        self.menuCloseButton.setText(QCoreApplication.translate("MainWindow", u"Click to Close the Window", None))
        self.FilePathButton.setText(QCoreApplication.translate("MainWindow", u"File_Path", None))
        self.BacktoMenuButton.setText(QCoreApplication.translate("MainWindow", u"Back To Menu", None))
        self.NextButton_Page_2.setText(QCoreApplication.translate("MainWindow", u"Next", None))
        self.Itemlabel.setText(QCoreApplication.translate("MainWindow", u"Product :", None))
        self.seq1Button.setText(QCoreApplication.translate("MainWindow", u"Stage 1", None))
        self.seq2Button.setText(QCoreApplication.translate("MainWindow", u"Stage 2", None))
        self.seq3Button.setText(QCoreApplication.translate("MainWindow", u"Stage 3", None))
        self.NextButton_Page_3.setText(QCoreApplication.translate("MainWindow", u"Next", None))
        self.BackButton_Page_2.setText(QCoreApplication.translate("MainWindow", u"Back", None))
        self.Seqlabel.setText(QCoreApplication.translate("MainWindow", u"Sequence:", None))
        self.Itemlabel_2.setText(QCoreApplication.translate("MainWindow", u"Product:", None))
        self.ConfirmButton.setText(QCoreApplication.translate("MainWindow", u"Confirm", None))
        self.BackButton_2.setText(QCoreApplication.translate("MainWindow", u"Back", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Click Mouse Display", None))
        self.Xgroupbox.setTitle("")
        self.titleXlabel.setText(QCoreApplication.translate("MainWindow", u"Width:", None))
        self.Xlabel.setText(QCoreApplication.translate("MainWindow", u"800", None))
        self.Ygroupbox.setTitle("")
        self.titleYlabel.setText(QCoreApplication.translate("MainWindow", u"Height:", None))
        self.Ylabel.setText(QCoreApplication.translate("MainWindow", u"800", None))
        self.displaybeforelabel.setText(QCoreApplication.translate("MainWindow", u"Camera Display", None))
        self.Xgroupbox_2.setTitle("")
        self.titleXlabel_2.setText(QCoreApplication.translate("MainWindow", u"Width:", None))
        self.Xlabel_2.setText(QCoreApplication.translate("MainWindow", u"800", None))
        self.Ygroupbox_2.setTitle("")
        self.titleYlabel_2.setText(QCoreApplication.translate("MainWindow", u"Height:", None))
        self.Ylabel_2.setText(QCoreApplication.translate("MainWindow", u"800", None))
        self.Zgroupbox.setTitle("")
        self.titleZlabel.setText(QCoreApplication.translate("MainWindow", u"Length", None))
        self.Zlabel.setText(QCoreApplication.translate("MainWindow", u"800", None))
        self.SettingButton.setText(QCoreApplication.translate("MainWindow", u"Setting", None))
        self.MarkingButton.setText(QCoreApplication.translate("MainWindow", u"Back to Marking", None))
        self.HomeButton.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.EnableRobotButton.setText(QCoreApplication.translate("MainWindow", u"Enable Robot", None))
        self.CloseButton.setText(QCoreApplication.translate("MainWindow", u"Abort/Close", None))
        self.ConfirmAckButton.setText(QCoreApplication.translate("MainWindow", u"Acknowledge", None))
    # retranslateUi

