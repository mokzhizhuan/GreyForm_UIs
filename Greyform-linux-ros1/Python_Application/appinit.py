from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import confirminit as initconfirm
from src.talker_listener.talker_listener import talker_node as RosPublisher
import rospy

class Ui_InitilizeWindow(QMainWindow):
    def __init__(self, ros_node):
        super(Ui_InitilizeWindow, self).__init__()
        self.initstart = uic.loadUi("UI_Design/initalize.ui", self)
        self.initstart.CloseButton.clicked.connect(self.initstart.close)
        self.initstart.StartButton.clicked.connect(
            lambda: initconfirm.ConfirminitDialog.show_dialog_confirm(self, ros_node)
            )
            
def ros_spin():
    rospy.spin()

if __name__ == "__main__":
    # Initialize the ROS node
    rospy.init_node("talker_node", anonymous=True)
    talker_node = RosPublisher.TalkerNode()
    app = QApplication(sys.argv)
    main_window = Ui_InitilizeWindow(talker_node)
    main_window.show()
    timer = rospy.Timer(rospy.Duration(0.1), lambda event: None)
    try:
        sys.exit(app.exec_())
    except SystemExit:
        pass
    finally:
        rospy.signal_shutdown("Shutting down ROS node")
