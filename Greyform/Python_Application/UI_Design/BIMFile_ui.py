# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'BIMFile.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QListView, QPushButton,
    QSizePolicy, QStackedWidget, QTextEdit, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(700, 800)
        self.DeleteButton = QPushButton(Form)
        self.DeleteButton.setObjectName(u"DeleteButton")
        self.DeleteButton.setGeometry(QRect(30, 430, 231, 131))
        font = QFont()
        font.setPointSize(18)
        self.DeleteButton.setFont(font)
        self.BacktoLoginButton = QPushButton(Form)
        self.BacktoLoginButton.setObjectName(u"BacktoLoginButton")
        self.BacktoLoginButton.setGeometry(QRect(310, 70, 181, 51))
        font1 = QFont()
        font1.setPointSize(13)
        self.BacktoLoginButton.setFont(font1)
        self.stackedWidgetbimfile = QStackedWidget(Form)
        self.stackedWidgetbimfile.setObjectName(u"stackedWidgetbimfile")
        self.stackedWidgetbimfile.setGeometry(QRect(310, 160, 371, 411))
        self.homepage = QWidget()
        self.homepage.setObjectName(u"homepage")
        self.stackedWidgetbimfile.addWidget(self.homepage)
        self.uploadpage = QWidget()
        self.uploadpage.setObjectName(u"uploadpage")
        self.uploadlistView = QListView(self.uploadpage)
        self.uploadlistView.setObjectName(u"uploadlistView")
        self.uploadlistView.setGeometry(QRect(35, 10, 291, 261))
        self.modellabel = QLabel(self.uploadpage)
        self.modellabel.setObjectName(u"modellabel")
        self.modellabel.setGeometry(QRect(30, 310, 121, 21))
        font2 = QFont()
        font2.setPointSize(14)
        self.modellabel.setFont(font2)
        self.modeltextEdit = QTextEdit(self.uploadpage)
        self.modeltextEdit.setObjectName(u"modeltextEdit")
        self.modeltextEdit.setGeometry(QRect(150, 300, 171, 41))
        self.modeltextEdit.setFont(font2)
        self.UploadconfirmButton = QPushButton(self.uploadpage)
        self.UploadconfirmButton.setObjectName(u"UploadconfirmButton")
        self.UploadconfirmButton.setGeometry(QRect(190, 360, 131, 41))
        self.FilePathButton = QPushButton(self.uploadpage)
        self.FilePathButton.setObjectName(u"FilePathButton")
        self.FilePathButton.setGeometry(QRect(30, 360, 131, 41))
        self.stackedWidgetbimfile.addWidget(self.uploadpage)
        self.Uploadpage_2 = QWidget()
        self.Uploadpage_2.setObjectName(u"Uploadpage_2")
        self.uploadlabel = QLabel(self.Uploadpage_2)
        self.uploadlabel.setObjectName(u"uploadlabel")
        self.uploadlabel.setGeometry(QRect(20, 20, 181, 51))
        font3 = QFont()
        font3.setPointSize(20)
        self.uploadlabel.setFont(font3)
        self.stackedWidgetbimfile.addWidget(self.Uploadpage_2)
        self.Deletepage = QWidget()
        self.Deletepage.setObjectName(u"Deletepage")
        self.DeleteconfirmButton = QPushButton(self.Deletepage)
        self.DeleteconfirmButton.setObjectName(u"DeleteconfirmButton")
        self.DeleteconfirmButton.setGeometry(QRect(120, 300, 131, 41))
        self.deletelistView = QListView(self.Deletepage)
        self.deletelistView.setObjectName(u"deletelistView")
        self.deletelistView.setGeometry(QRect(35, 10, 291, 261))
        self.stackedWidgetbimfile.addWidget(self.Deletepage)
        self.Deletepage_2 = QWidget()
        self.Deletepage_2.setObjectName(u"Deletepage_2")
        self.deletelabel = QLabel(self.Deletepage_2)
        self.deletelabel.setObjectName(u"deletelabel")
        self.deletelabel.setGeometry(QRect(50, 30, 181, 51))
        self.deletelabel.setFont(font3)
        self.stackedWidgetbimfile.addWidget(self.Deletepage_2)
        self.UploadButton = QPushButton(Form)
        self.UploadButton.setObjectName(u"UploadButton")
        self.UploadButton.setGeometry(QRect(30, 160, 231, 131))
        self.UploadButton.setFont(font)
        self.ExitButton = QPushButton(Form)
        self.ExitButton.setObjectName(u"ExitButton")
        self.ExitButton.setGeometry(QRect(520, 70, 131, 51))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.DeleteButton.setText(QCoreApplication.translate("Form", u"Delete BIM File", None))
        self.BacktoLoginButton.setText(QCoreApplication.translate("Form", u"Back to Admin Login", None))
        self.modellabel.setText(QCoreApplication.translate("Form", u"Model Name:", None))
        self.UploadconfirmButton.setText(QCoreApplication.translate("Form", u"Confirm", None))
        self.FilePathButton.setText(QCoreApplication.translate("Form", u"File Path", None))
        self.uploadlabel.setText(QCoreApplication.translate("Form", u"File Uploaded.", None))
        self.DeleteconfirmButton.setText(QCoreApplication.translate("Form", u"Delete", None))
        self.deletelabel.setText(QCoreApplication.translate("Form", u"File Deleted.", None))
        self.UploadButton.setText(QCoreApplication.translate("Form", u"Upload BIM File", None))
        self.ExitButton.setText(QCoreApplication.translate("Form", u"Exit", None))
    # retranslateUi

