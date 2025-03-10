from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import mainwindowlayout as mainwindowuilayout
import PythonApplication.fileselectionmesh as fileselectionmesh
from pyvistaqt import QtInteractor
from vtkmodules.qt import QVTKRenderWindowInteractor
import mainwindowbuttoninteraction as mainwindowbuttonUIinteraction
import vtk
import os
from src.talker_listener.talker_listener import talker_node as RosPublisher
import pyvista as pv
import rospy
"""from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, pyqtSlot, QUrl"""

class Bridge(QObject):
    """Bridge between Python and JavaScript."""
    
    @pyqtSlot(str)
    def receiveMessage(self, message):
        print(f"Received from JS: {message}")

    @pyqtSlot(result=str)
    def sendMessage(self):
        return "Hello from PyQt5!"


# load the mainwindow application
class Ui_MainWindow(QMainWindow):
    # starting ui
    def __init__(self, ros_node):
        # starting initialize
        super(Ui_MainWindow, self).__init__()
        self.mainwindow = uic.loadUi("UI_Design/mainframe.ui", self)
        self.mainwindow.setMouseTracking(False)
        self.selected_files = []
        self.filepaths = os.getcwd()
        self.file = None
        self.file_path = None
        self.ros_node = ros_node
        self.mainwindow.showMaximized()
        self.renderer = vtk.vtkRenderer()
        self._translate = QCoreApplication.translate
        self.stagestoring = ["Stage 1", "Stage 2" , "Stage 3", "Obstacles"]
        # Find the promoted QWebEngineView from the UI
        """self.webview = QWebEngineView()
        self.setCentralWidget(self.webview)

        # Setup WebChannel for communication
        self.channel = QWebChannel()
        self.bridge = Bridge()
        self.channel.registerObject("bridge", self.bridge)
        self.webview.page().setWebChannel(self.channel)

        # Load ReactJS index.html from the build folder
        react_app_path = os.path.abspath("my-react-app/build/index.html")
        self.webview.load(QUrl.fromLocalFile(react_app_path))"""

        self.setupUi()

    # setup UI
    def setupUi(self):
        self.plotterloader = QtInteractor(
            self.mainwindow.pyvistaframe,
            line_smoothing=True,
            point_smoothing=True,
            polygon_smoothing=True,
            multi_samples=8,
        )
        self.plotterloader.enable()
        self.renderWindowInteractor = (
            QVTKRenderWindowInteractor.QVTKRenderWindowInteractor(
                self.mainwindow.vtkframe
            )
        )
        self.model = QFileSystemModel()
        self.model.setRootPath("")  # Show entire system
        self.model.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)  # Show only folders
        self.mainwindow.Selectivefiledirectoryview.setModel(self.model)
        root_index = self.model.index("/")  # Set root to '/' for Linux
        self.mainwindow.Selectivefiledirectoryview.setRootIndex(root_index)  # Now safe to set

        # Model for displaying only files
        self.file_model = QFileSystemModel()
        self.file_model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)  
        self.file_model.setRootPath("/")  # Initialize root

        # Attach model to file view
        self.mainwindow.Selectivefilelistview.setModel(self.file_model)
        self.mainwindow.Selectivefiledirectoryview.clicked.connect(self.on_folder_selected)
        self.mainwindow.Selectivefilelistview.clicked.connect(self.on_file_selected)
        self.mainwindow.horizontalLayout_16.addWidget(self.plotterloader.interactor)
        self.mainwindow.horizontalLayout_15.addWidget(self.renderWindowInteractor)

        self.button_UI()
        self.setStretch()

    def on_folder_selected(self, index):
        selected_folder = self.model.filePath(index)  # Get folder path
        # Ensure the model is set before calling setRootIndex()
        self.file_model.setRootPath(selected_folder)
        self.mainwindow.Selectivefilelistview.setRootIndex(self.file_model.index(selected_folder))
    
    def on_file_selected(self, index):
        if not index.isValid():
            return
        selected_path = self.file_model.filePath(index)  # Get clicked item path
        if self.file_model.isDir(index):  
            self.file_model.setRootPath(selected_path)
            self.mainwindow.Selectivefilelistview.setRootIndex(self.file_model.index(selected_path))
        else:
            self.on_selection_changed(index)

    # button interaction
    def button_UI(self):
        self.buttonui = mainwindowbuttonUIinteraction.mainwindowbuttonUI(
            self.mainwindow,
            self.mainwindow.stackedWidget,
            self.mainwindow.menuStartButton,
            self.mainwindow.menuCloseButton,
            self.mainwindow.NextButton_Page_2,
            self.mainwindow.BacktoMenuButton,
            self.mainwindow.BackButton_Page_2,
            self.mainwindow.ChooseButton,
            self.mainwindow.sendmodelButton,
            self.mainwindow.CloseButton,
            self.ros_node,
        )


    # file selection when clicked
    def on_selection_changed(self, index):
        model = self.mainwindow.Selectivefilelistview.model()
        self.file_path = model.filePath(index)
        if self.file_path in self.selected_files:
            self.selected_files.remove(self.file_path) 
        else:
            self.selected_files.append(self.file_path)
        file = self.mainwindow.Selectivefilelistview.model().itemData(index)[0]
        mainwindowforfileselection = [
            self.plotterloader,
            self.renderer,
            self.renderWindowInteractor,
            self.ros_node,
            self.selected_files,
            self.mainwindow.NextButton_Page_3,
            self.mainwindow.Stagelabel,
            self.stagestoring,
            self.mainwindow.labelstatus,
            self.mainwindow.walllabel
        ]
        self.mainwindow.Itemlabel.setText(f"Model Product : {file}")
        fileselectionmesh.FileSelectionMesh(
            file, mainwindowforfileselection, self.mainwindow , self.mainwindow.stackedWidget
        )
        self.show_completion_message()
        self.file_list_selected = True


    # main window layout
    def setStretch(self):
        self.boxLayout = QVBoxLayout()
        self.boxLayout.addWidget(self.mainwindow.stackedWidget)
        self.mainwindow.centralwidget.setLayout(self.boxLayout)
        mainwindowuilayout.Ui_MainWindow_layout(
            self.mainwindow.stackedWidget,
            self.mainwindow.QTitle,
            self.mainwindow.layoutWidget,
            self.mainwindow.horizontalLayout,
            self.mainwindow.mainmenu,
            self.mainwindow.horizontalLayoutWidgetPage2,
            self.mainwindow.buttonpage2layoutWidget,
            self.mainwindow.page,
            self.mainwindow.Itemlabel,
            self.mainwindow.layoutWidgetpage3,
            self.mainwindow.horizontalLayoutWidgetbuttonpage3,
            self.mainwindow.page_2,
            self.mainwindow.labelstatus,
            self.mainwindow.scanpage,
            self.mainwindow.layoutWidgetpage4,
            self.mainwindow.horizontalLayoutWidgetpage4,
            self.mainwindow.page_3,
            self.mainwindow.sendmodelButton,
            self.mainwindow.CloseButton,
            self.mainwindow.ChooseButton,
            self.mainwindow.page_4,
        )

    # clean layout
    def clearLayout(self):
        while self.mainwindow.layoutWidgetframe.count():
            child = self.mainwindow.layoutWidgetframe.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        while self.mainwindow.layoutWidgetpage3.count():
            child = self.mainwindow.layoutWidgetpage3.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def closeEvent(self, event):
        self.mainwindow.vtkframe.close()
        self.renderWindowInteractor.GetRenderWindow().MakeCurrent()
        self.renderWindowInteractor.Finalize()
        self.renderWindowInteractor.GetRenderWindow().ClearInRenderStatus()
        self.renderWindowInteractor.GetRenderWindow().RemoveAllObservers()
        self.renderWindowInteractor.GetRenderWindow().Finalize()
        self.renderWindowInteractor.GetRenderWindow().GetInteractor().TerminateApp()
        event.accept()


    def show_completion_message(self):
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
        msg_box.setWindowTitle("3d Objects file initialize")
        msg_box.setText("3d Objects file initialize is completed.")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


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
