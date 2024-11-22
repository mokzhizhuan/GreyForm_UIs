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
import PythonApplication.usermanual as userHelper
import PythonApplication.setting as setting
import jsonimport as jsonfileopener
import mainthheme as mainthemebuilder
import vtk
import os
from src.talker_listener.talker_listener import talker_node as RosPublisher
import rospy


# load the mainwindow application
class Ui_MainWindow(QMainWindow):
    # starting ui
    def __init__(self, ros_node):
        # starting initialize
        super(Ui_MainWindow, self).__init__()
        self.mainwindow = uic.loadUi("UI_Design/mainframe.ui", self)
        self.mainwindow.setMouseTracking(False)
        jsonfile = "settings.json"
        (
            font,
            self.theme,
            self.themecolor,
            self.texttheme,
            self.text_labelothercolor,
            self.buttontheme,
            self.buttonthemeothercolor,
            self.buttontexttheme,
            self.buttontextothercolor,
            self.password,
            self.selected_time_zone,
            self.width,
            self.height,
        ) = jsonfileopener.jsopen(jsonfile)
        self.font_size = int(font)
        self.font = QFont()
        self.font.setPointSize(self.font_size)
        self.filepaths = os.getcwd()
        self.file = None
        self.file_path = None
        self.ros_node = ros_node
        self.default_settings = {
            "theme": str(self.theme),
            "themeothercolor": str(self.themecolor),
            "text_label": self.texttheme,
            "text_labelothercolor": self.text_labelothercolor,
            "buttontheme": self.buttontheme,
            "buttonthemeothercolor": self.buttonthemeothercolor,
            "buttontext": self.buttontexttheme,
            "buttontextothercolor": self.buttontextothercolor,
            "font_size": self.font_size,
            "resolution": f"{self.width} x {self.height}",
            "timezone": self.selected_time_zone,
            "password": str(self.password),
        }
        if self.width == 1920 and self.height == 1080:
            self.mainwindow.showMaximized()
        else:
            self.mainwindow.showNormal()
            self.mainwindow.resize(self.width, self.height)
        self.renderer = vtk.vtkRenderer()
        self._translate = QCoreApplication.translate
        self.apply_font_to_widgets(self.mainwindow, self.font)
        self.excelfilepath = None
        self.excel_file_selected = False
        self.file_list_selected = False
        config = {
            'maincolor': self.theme,
            'themecolor': self.themecolor,
            'maincolortext': self.texttheme,
            'text_labelothercolor': self.text_labelothercolor,
            'buttoncolor': self.buttontheme,
            'buttonthemeothercolor': self.buttonthemeothercolor,
            'buttontextcolor': self.buttontexttheme,
            'buttontextothercolor': self.buttontextothercolor
        }
        self.themebuilder = mainthemebuilder.themechange(
            config,
            self.mainwindow.centralwidget,
            self.mainwindow,
        )
        self.setupUi()

    # apply font
    def apply_font_to_widgets(self, parent, font):
        if hasattr(parent, "setFont"):
            parent.setFont(font)
        if hasattr(parent, "children"):
            for child in parent.children():
                self.apply_font_to_widgets(child, font)

    # setup UI
    def setupUi(self):
        self.mainwindow.NextButton_Page_2.hide()
        self.mainwindow.NextButton_Page_3.hide()
        self.plotterloader = QtInteractor(
            self.mainwindow.pyvistaframe,
            line_smoothing=True,
            point_smoothing=True,
            polygon_smoothing=True,
            multi_samples=8,
        )
        self.plotterloader.enable()
        self.plotterloader_2 = QtInteractor(
            self.mainwindow.pyvistaframe_2,
            line_smoothing=True,
            point_smoothing=True,
            polygon_smoothing=True,
            multi_samples=8,
        )
        self.plotterloader_2.enable()
        self.renderWindowInteractor = (
            QVTKRenderWindowInteractor.QVTKRenderWindowInteractor(
                self.mainwindow.vtkframe
            )
        )
        self.SettingButton.clicked.connect(self.directtosettingpage)
        self.mainwindow.horizontalLayout_2.addWidget(self.plotterloader.interactor)
        self.mainwindow.horizontalLayout_4.addWidget(self.plotterloader_2.interactor)
        self.mainwindow.verticalLayout.addWidget(self.renderWindowInteractor)
        self.retranslateUi()
        self.button_UI()
        self.settingpageuipage = setting.Setting(
            self.mainwindow.stackedWidget,
            self.mainwindow,
            self.mainwindow.centralwidget,
            self.width,
            self.height,
            self.default_settings,
            self.mainwindow.stackedWidget_main,
        )  # insert setting
        self.usermanualinstruct = userHelper.Usermanual(
            self.font,
            self.mainwindow.stackedWidget_main,
            self.mainwindow.usermanualpage,
        )  # users manual instruction page
        self.mainwindow.LocalizationButton.hide()
        self.setStretch()

    # button interaction
    def button_UI(self):
        self.mainwindow.Selectivefilelistview.clicked.connect(self.on_selection_changed)
        self.mainwindow.FilePathButton.clicked.connect(self.browsefilesdirectory)
        self.mainwindow.SettingButton.clicked.connect(self.directtosettingpage)
        self.mainwindow.usermanualButton.clicked.connect(self.directtousermanualpage)
        self.mainwindow.excelFilePathButton.clicked.connect(self.excelfilesdirectory)
        self.buttonui = mainwindowbuttonUIinteraction.mainwindowbuttonUI(
            self.mainwindow,
            self.mainwindow.stackedWidget,
            self.mainwindow.menuStartButton,
            self.mainwindow.menuCloseButton,
            self.mainwindow.NextButton_Page_2,
            self.mainwindow.BacktoMenuButton,
            self.mainwindow.BackButton_Page_2,
            self.mainwindow.BackButton_2,
            self.mainwindow.NextButton_Page_3,
            self.mainwindow.ConfirmButton,
            self.mainwindow.HomeButton,
            self.mainwindow.CloseButton,
            self.mainwindow.FeedbackButton,
            self.mainwindow.MarkingButton,
            self.ros_node,
        )

    # main ui page interaction
    def directtosettingpage(self):
        self.mainwindow.stackedWidget_main.setCurrentIndex(1)

    def directtousermanualpage(self):
        self.mainwindow.stackedWidget_main.setCurrentIndex(2)

    # file directory for 3d objects
    def browsefilesdirectory(self):
        self.filepaths = QFileDialog.getExistingDirectory(
            None, "Choose Directory", self.filepaths
        )
        model = QFileSystemModel()
        model.setRootPath(self.filepaths)
        model.setFilter(QDir.NoDotAndDotDot | QDir.Files)
        model.setNameFilters(["*.dxf", "*.stl", "*.ifc"])
        model.setNameFilterDisables(False)
        self.mainwindow.Selectivefilelistview.setModel(model)
        self.mainwindow.Selectivefilelistview.setRootIndex(model.index(self.filepaths))
        self.mainwindow.Selectivefilelistview.setAlternatingRowColors(True)

    # excel file directory info
    def excelfilesdirectory(self):
        self.excelfilepath, _ = QFileDialog.getOpenFileName(
            self, "Choose Excel File", "", "Excel Files (*.xlsx *.xls)"
        )
        if self.excelfilepath:
            self.mainwindow.excelfilpathtext.setText(self.excelfilepath)
        self.excel_file_selected = True
        self.check_if_both_selected()

    # file selection when clicked
    def on_selection_changed(self, index):
        model = self.mainwindow.Selectivefilelistview.model()
        self.file_path = model.filePath(index)
        file = self.mainwindow.Selectivefilelistview.model().itemData(index)[0]
        mainwindowforfileselection = [
            self.plotterloader,
            self.plotterloader_2,
            self.renderer,
            self.renderWindowInteractor,
            self.mainwindow.Ylabel,
            self.mainwindow.Xlabel,
            self.mainwindow.Xlabel_2,
            self.mainwindow.Ylabel_2,
            self.mainwindow.Zlabel,
            self.mainwindow.SequenceButton,
            self.mainwindow.NextButton_Page_3,
            self.mainwindow.LocalizationButton,
            self.ros_node,
            self.mainwindow.excelfilpathtext,
            self.mainwindow.seqlabel_2,
            self.mainwindow.Stagelabel,
            self.mainwindow.StageButton,
        ]
        fileselectionmesh.FileSelectionMesh(
            self.file_path, mainwindowforfileselection, self.mainwindow
        )
        if ".stl" in file:
            self.file = file.replace(".stl", "")
        elif ".ifc" in file:
            self.file = file.replace(".ifc", "")
        elif ".dxf" in file:
            self.file = file.replace(".dxf", "")
        self.mainwindow.Itemlabel.setText(
            self._translate("MainWindow", "Product : " + str(self.file))
        )
        self.mainwindow.Itemlabel_2.setText(
            self._translate("MainWindow", "Product: " + str(self.file))
        )
        self.file_list_selected = True
        self.show_completion_message()
        self.check_if_both_selected()

    # condition for excel file and stl loader have been loaded
    def check_if_both_selected(self):
        if self.excel_file_selected == True and self.file_list_selected == True:
            self.mainwindow.NextButton_Page_2.show()
        else:
            self.mainwindow.NextButton_Page_2.hide()

    # main window layout
    def setStretch(self):
        self.boxLayout = QVBoxLayout()
        self.boxLayout.addWidget(self.mainwindow.stackedWidget_main)
        self.mainwindow.centralwidget.setLayout(self.boxLayout)
        mainwindowuilayout.Ui_MainWindow_layout(
            self.mainwindow.stackedWidget,
            self.mainwindow.QTitle,
            self.mainwindow.layoutWidget,
            self.mainwindow.horizontalLayout,
            self.mainwindow.mainmenu,
            self.mainwindow.horizontalLayoutWidget,
            self.mainwindow.horizontalLayoutWidgetPage2,
            self.mainwindow.page,
            self.mainwindow.Itemlabel,
            self.mainwindow.layoutWidgetpage3,
            self.mainwindow.page_2,
            self.mainwindow.layoutWidgetpage4,
            self.mainwindow.horizontalLayoutWidgetpage4,
            self.mainwindow.page_3,
            self.mainwindow.layoutWidgetpage5,
            self.mainwindow.page_4,
            self.settingpageuipage,
            self.mainwindow.mainconfiguration,
            self.mainwindow.usermanualButton,
            self.mainwindow.SettingButton,
            self.mainwindow.settingpage,
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

    # text filter
    def retranslateUi(self):
        self.mainwindow.displaybeforelabel.setText(
            self._translate("MainWindow", "Mesh Camera Dimensions")
        )
        self.mainwindow.label_2.setText(
            self._translate("MainWindow", "Click Position", None)
        )
        self.mainwindow.FilePathButton.setToolTip(
            "Please insert File path, for stl , ifc , dxf , etc."
        )

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
