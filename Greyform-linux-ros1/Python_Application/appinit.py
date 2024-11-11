from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import confirminit as initconfirm
from src.talker_listener.talker_listener import talker_node as RosPublisher
import rospy
import jsonimport as jsonfileopener

#app init window
class Ui_InitilizeWindow(QMainWindow):
    def __init__(self, ros_node):
        # starting initialize
        super(Ui_InitilizeWindow, self).__init__()
        self.initstart = uic.loadUi("UI_Design/initalize.ui", self)
        jsonfile = "settings.json"
        (
            font,
            self.theme,
            self.password,
            self.selected_time_zone,
            self.width,
            self.height,
        ) = jsonfileopener.jsopen(jsonfile)
        self.font_size = int(font)
        self.font = QFont()
        self.font.setPointSize(self.font_size)
        if self.width == 1920 and self.height == 1080:
            self.initstart.showMaximized()
        else:
            self.initstart.showNormal()
            self.initstart.resize(self.width, self.height)
        self.ros_node = ros_node
        self.default_settings = {
            "theme": str(self.theme),
            "font_size": self.font_size,
            "resolution": f"{self.width} x {self.height}",
            "timezone": self.selected_time_zone,
            "password": str(self.password),
        }
        self.initstart.CloseButton.clicked.connect(self.initstart.close)
        self.initstart.StartButton.clicked.connect(
            lambda: initconfirm.ConfirminitDialog.show_dialog_confirm(self, ros_node)
            )
        self.stretch()
    
    #organized strechtable window for init application
    def stretch(self):
        self.boxLayout = QVBoxLayout()
        self.boxLayout.addStretch(1)
        self.boxLayout.addWidget(self.initstart.StartButton)
        self.boxLayout.addStretch(1)
        self.boxLayout.addWidget(self.initstart.CloseButton)
        self.boxLayout.addStretch(1)
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.boxLayout)
        self.initstart.setCentralWidget(self.centralWidget)

#ros_talker start           
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
