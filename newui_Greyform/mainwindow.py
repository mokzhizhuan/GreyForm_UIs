from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys, vtk , rospy , warnings
from pyvistaqt import QtInteractor
from vtkmodules.qt import QVTKRenderWindowInteractor
import mainwindowlayout as mainwindowuilayout
import mainwindowbuttoninteraction as mainwindowbuttonUIinteraction
from src.talker_listener.talker_listener import talker_node as RosPublisher
import argsfiles as fileimport
import exceldatavtk as dataplacement

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
        print(self.args.output_excel)
        self.mainwindow.progresslabel.hide()
        self.mainwindow.nextstepButton.hide()
        iconindicator = "placementindicator1.png"
        icon = "placement1.png"
        html = f'<div style="text-align:left;"><img src="{icon}" width="800" height="600" style="display:block; margin:0 auto;"></div>'
        htmlindicator = f'<div style="text-align:center;"><img src="{iconindicator}"  style="display:block; margin:0 auto;"></div>'
        self.mainwindow.imagelabel.setTextFormat(Qt.RichText)
        self.mainwindow.imagelabel.setText(html)
        self.mainwindow.imageplacelabel.setTextFormat(Qt.RichText)
        self.mainwindow.imageplacelabel.setText(htmlindicator)
        sheets_dict = dataplacement._coerce_to_dataframe(self.args.output_excel, sheet_name=None)
        self.wall_numbers_by_placement = dataplacement.exceldataextractor(sheets_dict)
        self.mainwindow.leftButton.hide()
        self.mainwindow.beginButton.hide()
        self.mainwindow.rightButton.hide()
        self.button_UI()
        self.setStretch()

    def button_UI(self):
        self.buttonui = mainwindowbuttonUIinteraction.mainwindowbuttonUI(
            self.mainwindow,
            self.mainwindow.stackedWidget,
            self.mainwindow.nextButton,
            self.mainwindow.leftButton,
            self.mainwindow.beginButton,
            self.mainwindow.rightButton,
            self.mainwindow.warninglabel,
            self.mainwindow.progresslabel,
            self.stl_file,
            self.ros_node,
            self.args,
            self.wall_numbers_by_placement,
            self.mainwindow.indicatelabel,
            self.mainwindow.nextstepButton
        )

    def setStretch(self):
        self.boxLayout = QVBoxLayout()
        self.boxLayout.addWidget(self.mainwindow.stackedWidget)
        self.mainwindow.centralwidget.setLayout(self.boxLayout)
        mainwindowuilayout.Ui_MainWindow_layout(
            self.mainwindow.stackedWidget,
            self.mainwindow.titlelabel,
            self.mainwindow.verticalLayoutWidget_3,
            self.mainwindow.page,
        )


# start ros
def ros_spin():
    rospy.spin()


if __name__ == "__main__":
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
