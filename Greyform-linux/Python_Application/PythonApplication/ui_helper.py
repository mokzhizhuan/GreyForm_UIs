from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget
import sys


class Ui_Dialog_Helper(QWidget):
    def __init__(self, interface_helper,main_window):
        super().__init__()
        self.interfacehelper = interface_helper
        self.main_window = main_window 
        self.main_window.hide()
        
    def ask_first_time_user(self):
        # Create a message box
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Helper")
        msg_box.setText("Are you a first-time user?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # Execute the message box and capture the user's response
        response = msg_box.exec_()

        # Set interfacehelper based on the response
        if response == QMessageBox.Yes:
            self.interfacehelper = "on"
            print("Interface helper is set to ON.")
        else:
            self.interfacehelper = "off"
            print("Interface helper is set to OFF.")
        self.main_window.show()
        return self.interfacehelper
