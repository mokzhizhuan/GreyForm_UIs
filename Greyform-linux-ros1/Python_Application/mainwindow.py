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
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

class FileItemDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setWidth(size.width() + 50)  # Increase the width for better visibility
        return size

    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignLeft | Qt.AlignVCenter  # Align text for readability
        super().paint(painter, option, index)

class FileFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(FileFilterProxyModel, self).__init__(parent)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterKeyColumn(0)

    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index(source_row, 0, source_parent)
        if not index.isValid():
            return False
        file_name = self.sourceModel().fileName(index)
        file_info = self.sourceModel().fileInfo(index)
        if file_info.isDir():
            return True
        allowed_extensions = {".dxf", ".ifc", ".stl"}
        return any(file_name.lower().endswith(ext) for ext in allowed_extensions)
    
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
        usb_path = "/media/ubuntu/DF4A-89D8/"
        self.check_usb_directory(usb_path)
        self.model = QFileSystemModel()
        self.model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Drives)
        self.model.setRootPath(usb_path)
        self.mainwindow.Selectivefiledirectoryview.setModel(self.model)
        root_index = self.model.index(usb_path)
        self.mainwindow.Selectivefiledirectoryview.setRootIndex(
            root_index
        )  # Now safe to set
        self.file_model = QFileSystemModel()
        self.file_model.setFilter(QDir.Files | QDir.NoDotAndDotDot)
        self.file_model.setRootPath(usb_path)
        self.mainwindow.Selectivefiledirectoryview.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.mainwindow.Selectivefiledirectoryview.setHeaderHidden(True)
        self.mainwindow.Selectivefiledirectoryview.setAnimated(
            True
        )  # Smooth folder expansion
        self.mainwindow.Selectivefiledirectoryview.setIndentation(
            20
        )  # Indentation for nested folders
        self.proxy_model = FileFilterProxyModel()
        self.proxy_model.setSourceModel(self.file_model)
        self.mainwindow.Selectivefilelistview.setModel(self.proxy_model)
        self.mainwindow.Selectivefilelistview.setRootIndex(
            self.proxy_model.mapFromSource(self.file_model.index(usb_path))
        )
        self.mainwindow.Selectivefilelistview.setHeaderHidden(False)
        self.mainwindow.Selectivefilelistview.setSortingEnabled(
            True
        )  # Allow sorting by columns
        self.mainwindow.Selectivefilelistview.setUniformRowHeights(
            True
        )  # Optimize performance
        self.mainwindow.Selectivefilelistview.setAlternatingRowColors(
            True
        )  # Better visibility
        self.mainwindow.Selectivefilelistview.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        header = self.mainwindow.Selectivefilelistview.header()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)  # Stretch the last column to fill space
        self.file_model.setHeaderData(0, Qt.Horizontal, "Name")
        self.file_model.setHeaderData(1, Qt.Horizontal, "Size")
        self.file_model.setHeaderData(2, Qt.Horizontal, "Type")
        self.file_model.setHeaderData(3, Qt.Horizontal, "Date Modified")
        self.mainwindow.Selectivefilelistview.sortByColumn(
            0, Qt.AscendingOrder
        )  # Sort by Name initially
        self.mainwindow.Selectivefilelistview.setItemsExpandable(
            False
        )  # Disable folder expansion
        self.mainwindow.Selectivefilelistview.setRootIsDecorated(
            False
        )  # Hide tree structure in the right panel
        self.mainwindow.Selectivefilelistview.setColumnWidth(
            0, 250
        )  # Minimum width for "Name"
        self.mainwindow.Selectivefilelistview.setIconSize(
            QSize(32, 32)
        )  # Slightly larger icon size
        delegate = FileItemDelegate()
        self.mainwindow.Selectivefilelistview.setItemDelegate(delegate)
        self.mainwindow.Selectivefiledirectoryview.clicked.connect(
            self.on_folder_selected
        )
        self.mainwindow.Selectivefilelistview.clicked.connect(self.on_file_selected)
        self.mainwindow.horizontalLayout_16.addWidget(self.plotterloader.interactor)
        self.mainwindow.verticalLayoutframe.addWidget(self.renderWindowInteractor)
        self.button_UI()
        self.setStretch()

    def check_usb_directory(self, path):
        """Check the folder structure manually to verify visibility."""
        try:
            contents = os.listdir(path)
            return
        except PermissionError:
            return
        except Exception as e:
            return

    def on_folder_selected(self, index):
        folder_path = self.model.filePath(index)
        self.file_model.setRootPath(folder_path)
        if self.mainwindow.Selectivefilelistview.model() != self.proxy_model:
            self.mainwindow.Selectivefilelistview.setModel(self.proxy_model)
        if self.proxy_model.sourceModel() != self.file_model:
            self.proxy_model.setSourceModel(self.file_model)
        source_index = self.file_model.index(folder_path)
        proxy_index = self.proxy_model.mapFromSource(source_index)
        if proxy_index.isValid():
            self.mainwindow.Selectivefilelistview.setRootIndex(proxy_index)

    
    def on_file_selected(self, index):
        selected_path = self.file_model.filePath(self.proxy_model.mapToSource(index))
        if self.file_model.isDir(self.proxy_model.mapToSource(index)):  
            new_source_index = self.file_model.index(selected_path)
            new_proxy_index = self.proxy_model.mapFromSource(new_source_index)
            if new_proxy_index.isValid():
                self.mainwindow.Selectivefilelistview.setRootIndex(new_proxy_index)
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
        source_index = self.proxy_model.mapToSource(index)
        file_path = self.file_model.filePath(source_index)
        self.file_path = file_path
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
            self.mainwindow.scanprogressBar,
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
            self.mainwindow.scanprogressBar,
            self.mainwindow.scanpage,
            self.mainwindow.verticalLayoutWidgetpage4frame,
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
