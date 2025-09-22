from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import vtk
from pyvistaqt import QtInteractor
from vtkmodules.qt import QVTKRenderWindowInteractor
import mainwindowlayout as mainwindowuilayout
import mainwindowbuttoninteraction as mainwindowbuttonUIinteraction
from src.talker_listener.talker_listener import talker_node as RosPublisher
import rospy
import warnings
import argsfiles as fileimport
import exceldatavtk as dataplacement
import dataanalysis as datadraft

warnings.filterwarnings("ignore", category=DeprecationWarning)


class Ui_MainWindow(QMainWindow):
    def __init__(self, ros_node):
        super().__init__()
        self.args = fileimport.parse_args()
        self.mainwindow = uic.loadUi(self.args.mainui, self)
        self.mainwindow.showMaximized()
        self.stl_file = self.args.ifc_file
        self.renderer = vtk.vtkRenderer()
        self.ros_node = ros_node
        self.setupUi()

    # setup UI
    def setupUi(self):
        self.renderWindowInteractor = (
            QVTKRenderWindowInteractor.QVTKRenderWindowInteractor(
                self.mainwindow.pbuframe
            )
        )
        datadrafter = datadraft.data_draft(self.stl_file, self.args)
        df_combined_data = datadrafter.analysis()
        iconindicator = "placementindicator1.png"
        icon = "placement1.png"
        html = f'<div style="text-align:center;"><img src="{icon}" width="800" height="600" style="display:block; margin:0 auto;"></div>'
        htmlindicator = f'<div style="text-align:center;"><img src="{iconindicator}"  style="display:block; margin:0 auto;"></div>'
        self.mainwindow.imagelabel.setTextFormat(Qt.RichText)
        self.mainwindow.imagelabel.setText(html)
        self.mainwindow.imageplacelabel.setTextFormat(Qt.RichText)
        self.mainwindow.imageplacelabel.setText(htmlindicator)
        self.wall_numbers_by_placement = dataplacement.exceldataextractor(df_combined_data)
        self.mainwindow.confirmButton_2.hide()
        self.mainwindow.nextstepButton.hide()
        self.button_UI()
        self.setStretch()

    def button_UI(self):
        self.buttonui = mainwindowbuttonUIinteraction.mainwindowbuttonUI(
            self.mainwindow,
            self.mainwindow.stackedWidget,
            self.mainwindow.confirmButton,
            self.mainwindow.confirmButton_2,
            self.mainwindow.nextstepButton,
            self.mainwindow.machinelabel,
            self.ros_node,
            self.stl_file,
            self.args,
            self.mainwindow,
            self.renderWindowInteractor,
            self.wall_numbers_by_placement,
        )

    def setStretch(self):
        self.boxLayout = QVBoxLayout()
        self.boxLayout.addWidget(self.mainwindow.stackedWidget)
        self.mainwindow.centralwidget.setLayout(self.boxLayout)
        mainwindowuilayout.Ui_MainWindow_layout(
            self.mainwindow.stackedWidget,
            self.mainwindow.titlelabel,
            self.mainwindow.machinelabel,
            self.mainwindow.verticalLayoutWidget_3,
            self.mainwindow.horizontalLayoutWidget,
            self.mainwindow.page,
        )


# start ros
def ros_spin():
    rospy.spin()


if __name__ == "__main__":
    # Initialize the ROS node
    rospy.init_node("talker_node", anonymous=True)
    talker_node = RosPublisher.TalkerNode()
    app = QApplication(sys.argv)
    main_window = Ui_MainWindow(talker_node)
    main_window.show()
    timer = rospy.Timer(rospy.Duration(0.1), lambda event: None)
    try:
        sys.exit(app.exec_())
    except SystemExit:
        pass
    finally:
        rospy.signal_shutdown("Shutting down ROS node")
