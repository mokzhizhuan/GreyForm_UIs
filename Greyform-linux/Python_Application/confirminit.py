from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QDialog, QVBoxLayout, QLabel, QApplication , QMessageBox
from PyQt5.QtGui import QFont
import subprocess
import mainwindow as locMarapplication
import rclpy
from rclpy.node import Node
import os
import sys
import threading


#confirm dialog runner
class ConfirminitDialog(QMainWindow):
    def show_dialog_confirm(self, ros_node):
        dialog = QDialog(self)
        dialog.setWindowTitle("Dialog Box")
        dialog.resize(400, 300)
        label = QLabel("Are you sure you want to initialize the LOC and MAR modules??")
        label.setGeometry(QtCore.QRect(100, 40, 171, 31))
        label.setFont(QFont("Arial", 20))
        label.setWordWrap(True)
        label.setObjectName("label")
        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(label)
        dialog.setLayout(dialog_layout)
        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.setStyleSheet(
            """
            QDialogButtonBox QPushButton {
                font-size: 20px;      
                min-width: 200px;      
                min-height: 100px;   
                icon-size: 100px 100px;        
            }
            """
        )
        buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 100))
        buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
            | QtWidgets.QDialogButtonBox.StandardButton.Ok
        )
        ok_button = buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Confirm")
        buttonBox.setObjectName("buttonBox")
        buttonBox.accepted.connect(
            lambda: ConfirminitDialog.run_subprocess_commands(self, ros_node, dialog)
        )
        buttonBox.rejected.connect(dialog.close)
        dialog_layout.addWidget(buttonBox)
        dialog.exec_()

    def run_subprocess_commands(self, ros_node, dialog):
        try:
            print("Running colcon build...")
            subprocess.run(["colcon", "build"], check=True) 
            print("Sourcing setup.bash...")
            command = "bash -c 'source /home/ubuntu/ros2_ws/src/Greyform-linux/Python_Application/install/setup.bash && env'"
            proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            output = proc.communicate()[0].decode("utf-8")
            for line in output.splitlines():
                key, _, value = line.partition("=")
                os.environ[key] = value
            ros_thread = threading.Thread(target=ConfirminitDialog.run_ros_node, args=(ros_node,))
            ros_thread.start()
            print("Running the ROS node and starting the Qt application...")
            if not QApplication.instance(): 
                app = QApplication(sys.argv)
            else:
                app = QApplication.instance()
            main_window = locMarapplication.Ui_MainWindow(ros_node)
            main_window.show()
            ConfirminitDialog.show_completion_message()
            dialog.close()
            self.close()
        except subprocess.CalledProcessError as e:
            print(f"Error while executing subprocess: {e}")

    def run_ros_node(ros_node):
        if not rclpy.ok():  
            rclpy.init()

    
    def show_completion_message():
        msg_box = QMessageBox()
        msg_box.setStyleSheet(
            """
        QMessageBox {
            font-family: Helvetica;
            font-size: 20px;
            color: blue;
            }
        QPushButton {
            font-family: Helvetica;
            font-size: 20px;
            padding: 5px;
            }
            """
        )
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Initialization Complete")
        msg_box.setText("Initialization of LOC and MAR app is completed.")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
