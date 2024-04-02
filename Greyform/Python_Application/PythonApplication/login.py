import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QDialog, QApplication


class Login(QDialog):
    def __init__(self, accountinfo, widget, userlabel):
        super(Login, self).__init__()
        self.form = uic.loadUi("UI_Design/login.ui", self)
        self.accountinfo = accountinfo
        self.widget = widget
        self.userlabel = userlabel
        self.loginbutton.clicked.connect(self.loginfunction)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.createaccbutton.clicked.connect(self.gotocreate)

    def loginfunction(self):
        email = self.email.text()
        password = self.password.text()
        for acc in range(len(self.accountinfo)):
            if (
                self.accountinfo[acc]["Email"] == email
                and self.accountinfo[acc]["Pass"] == password
            ):
                self.userlabel.setText(f"User: {email}")
                self.form.email.clear()
                self.form.password.clear()
                return

    def gotocreate(self):
        createacc = CreateAcc(self.accountinfo, self.widget, self.userlabel)
        self.widget.addWidget(createacc)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)


class CreateAcc(QDialog):
    def __init__(self, accountinfo, widget, userlabel):
        super(CreateAcc, self).__init__()
        uic.loadUi("UI_Design/createacc.ui", self)
        self.signupbutton.clicked.connect(self.createaccfunction)
        self.backbutton.clicked.connect(self.backtologin)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.accountinfo = accountinfo
        self.widget = widget
        self.userlabel = userlabel

    def createaccfunction(self):
        email = self.email.text()
        if self.password.text() == self.confirmpass.text():
            password = self.password.text()
            newacc = {"Email": email, "Pass": password}
            self.accountinfo.append(newacc)
            print("Successfully created an account")
            login = Login(self.accountinfo, self.widget, self.userlabel)
            self.widget.addWidget(login)
            self.widget.setCurrentIndex(self.widget.currentIndex() + 1)

    def backtologin(self):
        login = Login(self.accountinfo, self.widget, self.userlabel)
        self.widget.addWidget(login)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
