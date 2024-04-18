import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
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
        self.password.returnPressed.connect(self.loginfunction)
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
                "Incorrect Password, please try again or press the change password button."
            )
            msg_box.setStandardButtons(QMessageBox.Ok)

            # Show the message box
            msg_box.exec_()

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
        self.form.password.returnPressed.connect(self.changepassfunction)
        self.accountinfo = accountinfo
        self.widget = widget
        self.userlabel = userlabel
        self.file = file

    def changepassfunction(self):
        password = self.form.password.text()
        if password != self.accountinfo[0]["Pass"]:
            self.accountinfo[0]["Pass"] = password
            login = Login(self.accountinfo, self.widget, self.userlabel , self.file)
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

    def backtologin(self):
        login = Login(self.accountinfo, self.widget, self.userlabel, self.file)
        self.widget.addWidget(login)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
