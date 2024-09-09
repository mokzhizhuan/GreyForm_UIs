from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import confirminit as initconfirm
import talker_listener.talker_node as RosPublisher
import rclpy
from rclpy.executors import MultiThreadedExecutor
from std_msgs.msg import String
from threading import Thread


class Ui_InitilizeWindow(QMainWindow):
    def __init__(self, ros_node):
        super(Ui_InitilizeWindow, self).__init__()
        self.initstart = uic.loadUi("UI_Design/initalize.ui", self)
        self.initstart.CloseButton.clicked.connect(self.initstart.close)
        self.initstart.StartButton.clicked.connect(
            lambda: initconfirm.ConfirminitDialog.show_dialog_confirm(self, ros_node)
            )

def ros_spin(node):
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        executor.shutdown()
        node.destroy_node()           

if __name__ == "__main__":
    # Initialize the ROS node
    rclpy.init()
    talker_node = RosPublisher.TalkerNode()
    app = QApplication(sys.argv)
    main_window = Ui_InitilizeWindow(talker_node)
    main_window.show()
    talker_thread = Thread(target=ros_spin, args=(talker_node,))
    talker_thread.start()
    try:
        sys.exit(app.exec_())
    except SystemExit:
        pass
    rclpy.shutdown()
