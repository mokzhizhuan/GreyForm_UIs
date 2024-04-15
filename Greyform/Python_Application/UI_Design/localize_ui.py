# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'localize.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QListView, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QStackedWidget,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(700, 800)
        self.uploaduiButton = QPushButton(Form)
        self.uploaduiButton.setObjectName(u"uploaduiButton")
        self.uploaduiButton.setGeometry(QRect(30, 170, 111, 41))
        self.stackedWidget_localisation = QStackedWidget(Form)
        self.stackedWidget_localisation.setObjectName(u"stackedWidget_localisation")
        self.stackedWidget_localisation.setGeometry(QRect(190, 50, 491, 591))
        self.selectionmodelpage = QWidget()
        self.selectionmodelpage.setObjectName(u"selectionmodelpage")
        self.modellocaliselistview = QListView(self.selectionmodelpage)
        self.modellocaliselistview.setObjectName(u"modellocaliselistview")
        self.modellocaliselistview.setGeometry(QRect(50, 20, 371, 411))
        self.selectbutton = QPushButton(self.selectionmodelpage)
        self.selectbutton.setObjectName(u"selectbutton")
        self.selectbutton.setGeometry(QRect(60, 470, 89, 25))
        self.cancelbutton = QPushButton(self.selectionmodelpage)
        self.cancelbutton.setObjectName(u"cancelbutton")
        self.cancelbutton.setGeometry(QRect(280, 470, 89, 25))
        self.stackedWidget_localisation.addWidget(self.selectionmodelpage)
        self.localisationpage = QWidget()
        self.localisationpage.setObjectName(u"localisationpage")
        self.modelselectedlabel = QLabel(self.localisationpage)
        self.modelselectedlabel.setObjectName(u"modelselectedlabel")
        self.modelselectedlabel.setGeometry(QRect(130, 30, 291, 41))
        font = QFont()
        font.setPointSize(13)
        self.modelselectedlabel.setFont(font)
        self.localisationlabel = QLabel(self.localisationpage)
        self.localisationlabel.setObjectName(u"localisationlabel")
        self.localisationlabel.setGeometry(QRect(130, 80, 291, 41))
        self.localisationlabel.setFont(font)
        self.derivingreferlabel = QLabel(self.localisationpage)
        self.derivingreferlabel.setObjectName(u"derivingreferlabel")
        self.derivingreferlabel.setGeometry(QRect(130, 130, 291, 41))
        self.derivingreferlabel.setFont(font)
        self.markingpointslabel = QLabel(self.localisationpage)
        self.markingpointslabel.setObjectName(u"markingpointslabel")
        self.markingpointslabel.setGeometry(QRect(130, 180, 291, 41))
        self.markingpointslabel.setFont(font)
        self.markinglistWidget = QListWidget(self.localisationpage)
        QListWidgetItem(self.markinglistWidget)
        QListWidgetItem(self.markinglistWidget)
        QListWidgetItem(self.markinglistWidget)
        self.markinglistWidget.setObjectName(u"markinglistWidget")
        self.markinglistWidget.setGeometry(QRect(150, 240, 260, 160))
        font1 = QFont()
        font1.setPointSize(20)
        self.markinglistWidget.setFont(font1)
        self.markinglistWidget.setLineWidth(0)
        self.markinglistWidget.setSpacing(8)
        self.selectmarkingbutton = QPushButton(self.localisationpage)
        self.selectmarkingbutton.setObjectName(u"selectmarkingbutton")
        self.selectmarkingbutton.setGeometry(QRect(148, 500, 111, 51))
        self.cancelbutton_2 = QPushButton(self.localisationpage)
        self.cancelbutton_2.setObjectName(u"cancelbutton_2")
        self.cancelbutton_2.setGeometry(QRect(288, 500, 101, 51))
        self.markinglabelselected = QLabel(self.localisationpage)
        self.markinglabelselected.setObjectName(u"markinglabelselected")
        self.markinglabelselected.setGeometry(QRect(170, 360, 300, 51))
        font2 = QFont()
        font2.setPointSize(16)
        self.markinglabelselected.setFont(font2)
        self.redoprocessbutton = QPushButton(self.localisationpage)
        self.redoprocessbutton.setObjectName(u"redoprocessbutton")
        self.redoprocessbutton.setGeometry(QRect(290, 500, 101, 51))
        self.markingstartbutton = QPushButton(self.localisationpage)
        self.markingstartbutton.setObjectName(u"markingstartbutton")
        self.markingstartbutton.setGeometry(QRect(150, 500, 111, 51))
        self.stackedWidget_localisation.addWidget(self.localisationpage)
        self.loadingpage = QWidget()
        self.loadingpage.setObjectName(u"loadingpage")
        self.localisationlabelselected = QLabel(self.loadingpage)
        self.localisationlabelselected.setObjectName(u"localisationlabelselected")
        self.localisationlabelselected.setGeometry(QRect(150, 40, 291, 41))
        self.localisationlabelselected.setFont(font)
        self.leftwalllabel = QLabel(self.loadingpage)
        self.leftwalllabel.setObjectName(u"leftwalllabel")
        self.leftwalllabel.setGeometry(QRect(150, 90, 291, 41))
        self.leftwalllabel.setFont(font)
        self.frontwalllabel = QLabel(self.loadingpage)
        self.frontwalllabel.setObjectName(u"frontwalllabel")
        self.frontwalllabel.setGeometry(QRect(150, 140, 291, 41))
        self.frontwalllabel.setFont(font)
        self.rightwalllabel = QLabel(self.loadingpage)
        self.rightwalllabel.setObjectName(u"rightwalllabel")
        self.rightwalllabel.setGeometry(QRect(150, 190, 291, 41))
        self.rightwalllabel.setFont(font)
        self.floorlabel = QLabel(self.loadingpage)
        self.floorlabel.setObjectName(u"floorlabel")
        self.floorlabel.setGeometry(QRect(150, 240, 291, 41))
        self.floorlabel.setFont(font)
        self.markingcompletedlabel = QLabel(self.loadingpage)
        self.markingcompletedlabel.setObjectName(u"markingcompletedlabel")
        self.markingcompletedlabel.setGeometry(QRect(150, 300, 291, 41))
        self.markingcompletedlabel.setFont(font)
        self.cancelloadButton = QPushButton(self.loadingpage)
        self.cancelloadButton.setObjectName(u"cancelloadButton")
        self.cancelloadButton.setGeometry(QRect(100, 530, 89, 25))
        self.stackedWidget_localisation.addWidget(self.loadingpage)
        self.backtologinbutton = QPushButton(Form)
        self.backtologinbutton.setObjectName(u"backtologinbutton")
        self.backtologinbutton.setGeometry(QRect(30, 290, 111, 41))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.uploaduiButton.setText(QCoreApplication.translate("Form", u"Upload Page", None))
        self.selectbutton.setText(QCoreApplication.translate("Form", u"Select", None))
        self.cancelbutton.setText(QCoreApplication.translate("Form", u"Cancel", None))
        self.modelselectedlabel.setText("")
        self.localisationlabel.setText("")
        self.derivingreferlabel.setText("")
        self.markingpointslabel.setText("")

        __sortingEnabled = self.markinglistWidget.isSortingEnabled()
        self.markinglistWidget.setSortingEnabled(False)
        ___qlistwidgetitem = self.markinglistWidget.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("Form", u"Stage 1 Marking", None));
        ___qlistwidgetitem1 = self.markinglistWidget.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("Form", u"Stage 2 Marking", None));
        ___qlistwidgetitem2 = self.markinglistWidget.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("Form", u"Stage 3 Marking", None));
        self.markinglistWidget.setSortingEnabled(__sortingEnabled)

        self.selectmarkingbutton.setText(QCoreApplication.translate("Form", u"Select", None))
        self.cancelbutton_2.setText(QCoreApplication.translate("Form", u"Cancel", None))
        self.markinglabelselected.setText("")
        self.redoprocessbutton.setText(QCoreApplication.translate("Form", u"Re-do", None))
        self.markingstartbutton.setText(QCoreApplication.translate("Form", u"Start Marking", None))
        self.localisationlabelselected.setText("")
        self.leftwalllabel.setText("")
        self.frontwalllabel.setText("")
        self.rightwalllabel.setText("")
        self.floorlabel.setText("")
        self.markingcompletedlabel.setText("")
        self.cancelloadButton.setText(QCoreApplication.translate("Form", u"Cancel", None))
        self.backtologinbutton.setText(QCoreApplication.translate("Form", u"Back to Login", None))
    # retranslateUi

