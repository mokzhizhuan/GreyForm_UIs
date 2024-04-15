import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QDialog, QApplication
import PythonApplication.BIMFile as BIMfile


class Login(QDialog):
    def __init__(self, accountinfo, widget, userlabel, file):
        super(Login, self).__init__()
        self.form = uic.loadUi("UI_Design/login.ui", self)
        self.accountinfo = accountinfo
        self.widget = widget
        self.userlabel = userlabel
        self.file = file
        self.form.userid = self.accountinfo[0]["UserID"]
        self.loginbutton.clicked.connect(self.loginfunction)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.changepassbutton.clicked.connect(self.changepassword)

    def loginfunction(self):
        password = self.form.password.text()
        counter = 0
        for acc in range(len(self.accountinfo)):
            if self.accountinfo[acc]["Pass"] == password:
                counter = counter + 1
        if counter == 1:
            Bimfiles = BIMfile.BimfileInterpretor(
                self.accountinfo, self.widget, self.userlabel, self.file
            )
            self.widget.addWidget(Bimfiles)
            self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
        else:
            print("Password is incorrect , please try again")

    def changepassword(self):
        ChangePassword = ChangePass(
            self.accountinfo, self.widget, self.userlabel, self.file
        )
        self.widget.addWidget(ChangePassword)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)


class ChangePass(QDialog):
    def __init__(self, accountinfo, widget, userlabel, file):
        super(ChangePass, self).__init__()
        self.form = uic.loadUi("UI_Design/changepass.ui", self)
        self.form.changepassbutton.clicked.connect(self.changepassfunction)
        self.form.backbutton.clicked.connect(self.backtologin)
        self.form.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.accountinfo = accountinfo
        self.widget = widget
        self.userlabel = userlabel
        self.file = file

    def changepassfunction(self):
        password = self.form.password.text()
        if password != self.accountinfo[0]["Pass"]:
            self.accountinfo[0]["Pass"] = password
            login = Login(self.accountinfo, self.widget, self.userlabel)
            self.widget.addWidget(login)
            self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
        else:
            print(
                "The Password that you inputed is the same as the password , please input the different password."
            )

    def backtologin(self):
        login = Login(self.accountinfo, self.widget, self.userlabel, self.file)
        self.widget.addWidget(login)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
