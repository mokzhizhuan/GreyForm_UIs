from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


# user login function will include profile also later
class Login(QDialog):
    def __init__(self, accountinfo, widget, userlabel, file, stackedWidgetusersetting):
        super(Login, self).__init__()
        self.form = uic.loadUi("UI_Design/login.ui", self)
        self.accountinfo = accountinfo
        self.widget = widget
        self.userlabel = userlabel
        self.file = file
        self.stackedWidgetusersetting = stackedWidgetusersetting
        self.form.userid = self.accountinfo[0]["UserID"]
        self.setupUI()
        self.form.loginbutton.clicked.connect(self.loginfunction)
        self.form.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.form.password.returnPressed.connect(self.loginfunction)
        self.form.changepassbutton.clicked.connect(self.changepassword)

    def setupUI(self):
        self.loginboxlayout = QVBoxLayout()
        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding
        )
        self.verticalSpacer_2 = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding
        )
        self.loginboxlayout.addWidget(self.form.label)
        self.loginboxlayout.addItem(self.verticalSpacer)
        self.loginboxlayout.addWidget(self.form.horizontalLayoutWidget)
        self.loginboxlayout.addItem(self.verticalSpacer_2)
        self.loginboxlayout.addWidget(self.form.horizontalLayoutWidget_2)
        self.loginboxlayout.setStretch(1, 1)
        self.loginboxlayout.setStretch(3, 1)
        self.setLayout(self.loginboxlayout)

    # login success or fail
    def loginfunction(self):
        password = self.form.password.text()
        counter = 0
        for acc in range(len(self.accountinfo)):
            if self.accountinfo[acc]["Pass"] == password:
                counter = counter + 1
        if counter == 1:
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Information)
            message_box.setWindowTitle("Success")
            message_box.setText("Login Success " + self.form.userid)
            message_box.setStandardButtons(QMessageBox.Ok)
            returnValue = message_box.exec()
            if returnValue == QMessageBox.Ok:
                profile = Profile(
                    self.accountinfo,
                    self.widget,
                    self.userlabel,
                    self.file,
                    self.stackedWidgetusersetting,
                )
            self.widget.addWidget(profile)
            self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
        else:
            # warning message box
            msg_box = QMessageBox()

            # Apply a stylesheet to the QMessageBox
            msg_box.setStyleSheet(
                "QLabel{color: red;} QPushButton{ width: 100px; font-size: 16px; }"
            )

            # Set the icon, title, text and buttons for the message box
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Error")
            msg_box.setText(
                "Incorrect Password, please try again or press the change password button."
            )
            msg_box.setStandardButtons(QMessageBox.Ok)

            # Show the message box
            msg_box.exec()

    # access to change pass ui
    def changepassword(self):
        ChangePassword = ChangePass(
            self.accountinfo,
            self.widget,
            self.userlabel,
            self.file,
            self.stackedWidgetusersetting,
        )
        self.widget.addWidget(ChangePassword)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)


# change password.
class ChangePass(QDialog):
    def __init__(self, accountinfo, widget, userlabel, file, stackedWidgetusersetting):
        super(ChangePass, self).__init__()
        self.form = uic.loadUi("UI_Design/changepass.ui", self)
        self.form.changepassbutton.clicked.connect(self.changepassfunction)
        self.form.backbutton.clicked.connect(self.backtologin)
        self.form.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.form.password.returnPressed.connect(self.changepassfunction)
        self.accountinfo = accountinfo
        self.widget = widget
        self.userlabel = userlabel
        self.file = file
        self.stackedWidgetusersetting = stackedWidgetusersetting
        self.setupUI()

    def setupUI(self):
        self.changepassboxlayout = QVBoxLayout()
        self.verticalSpacer = QSpacerItem(
            20, 70, QSizePolicy.Minimum, QSizePolicy.Maximum
        )
        self.verticalSpacer_2 = QSpacerItem(
            20, 70, QSizePolicy.Minimum, QSizePolicy.Maximum
        )
        self.changepassboxlayout.addWidget(self.form.label)
        self.changepassboxlayout.addItem(self.verticalSpacer)
        self.changepassboxlayout.addWidget(self.form.horizontalLayoutWidget)
        self.changepassboxlayout.addItem(self.verticalSpacer_2)
        self.changepassboxlayout.addWidget(self.form.horizontalLayoutWidget_2)
        self.setLayout(self.changepassboxlayout)

    # change pass ui
    def changepassfunction(self):
        password = self.form.password.text()
        if password != self.accountinfo[0]["Pass"]:
            self.accountinfo[0]["Pass"] = password
            login = Login(self.accountinfo, self.widget, self.userlabel, self.file)
            self.widget.addWidget(login)
            self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
        else:
            # Create a QMessageBox
            msg_box = QMessageBox()

            # Apply a stylesheet to the QMessageBox
            msg_box.setStyleSheet(
                "QLabel{color: red;} QPushButton{ width: 100px; font-size: 16px; }"
            )

            # Set the icon, title, text and buttons for the message box
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Error")
            msg_box.setText(
                "The Password that you inputed is the same as the password , please input the different password."
            )
            msg_box.setStandardButtons(QMessageBox.Ok)

            # Show the message box
            msg_box.exec_()

    # back to login ui
    def backtologin(self):
        login = Login(
            self.accountinfo,
            self.widget,
            self.userlabel,
            self.file,
            self.stackedWidgetusersetting,
        )
        self.widget.addWidget(login)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)


class Profile(QDialog):
    def __init__(self, accountinfo, widget, userlabel, file, stackedWidgetusersetting):
        super(Profile, self).__init__()
        self.form = uic.loadUi("UI_Design/Profile.ui", self)
        self.accountinfo = accountinfo
        self.widget = widget
        self.userlabel = userlabel
        self.file = file
        self.stackedWidgetusersetting = stackedWidgetusersetting
        self.form.userlabel.setText(self.accountinfo[0]["UserID"])
        self.setupUI()
        self.form.loginbutton.clicked.connect(self.backtologin)

    def setupUI(self):

        self.form.userlabel.setAlignment(Qt.AlignCenter)
        self.profilelayout = QVBoxLayout()
        self.profilelayout.addWidget(self.form.profileiconlabel)
        pixmap = QPixmap("—Pngtree—avatar icon profile icon member_5247852.png")
        self.form.profileiconlabel.setPixmap(pixmap)
        self.form.profileiconlabel.resize(
            int(pixmap.width() / 2), int(pixmap.height() / 2)
        )
        scaled_pixmap = pixmap.scaled(
            self.form.profileiconlabel.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.form.profileiconlabel.setAlignment(Qt.AlignCenter)
        self.form.profileiconlabel.setScaledContents(True)
        self.form.profileiconlabel.setPixmap(scaled_pixmap)
        self.profilelayout.addWidget(self.form.label)
        self.profilelayout.addWidget(self.form.userlabel)
        self.profilelayout.addWidget(self.form.loginbutton)
        self.setLayout(self.profilelayout)

    def backtologin(self):
        login = Login(
            self.accountinfo,
            self.widget,
            self.userlabel,
            self.file,
            self.stackedWidgetusersetting,
        )
        self.widget.addWidget(login)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
