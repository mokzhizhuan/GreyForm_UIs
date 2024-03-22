from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PythonApplication.fileselectionmesh as fileselectionmesh
import PythonApplication.menuconfirm as backtomenudialog
import PythonApplication.mainframe_part2 as mainframe_part2
from pyvistaqt import QtInteractor
import os


class Ui_MainWindow(object):
    def __init__(self, MainWindow, stackedwidgetpage):
        self.filepaths = os.getcwd()
        self.stackedWidget = stackedwidgetpage
        self.file = None
        self.file_path = None
        self.MainWindow = MainWindow
        self.setupUi_Page1(self.MainWindow)

    # Page 1 UI setup
    def setupUi_Page1(self, MainWindow):
        self.page = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.page.sizePolicy().hasHeightForWidth())
        self.page.setSizePolicy(sizePolicy)
        self.page.setObjectName("page")
        self.Selectivefilelistview = QtWidgets.QListView(parent=self.page)
        self.Selectivefilelistview.setGeometry(QtCore.QRect(100, 80, 431, 861))
        self.Selectivefilelistview.setObjectName("Selectivefilelistview")
        self.Selectivefilelistview.clicked.connect(self.on_selection_changed)
        self.NextButton_Page_2 = QtWidgets.QPushButton(parent=self.page)
        self.NextButton_Page_2.setGeometry(QtCore.QRect(400, 980, 101, 25))
        self.NextButton_Page_2.setObjectName("NextButton_Page_2")
        self.NextButton_Page_2.hide()
        self.BacktoMenuButton = QtWidgets.QPushButton(parent=self.page)
        self.BacktoMenuButton.setGeometry(QtCore.QRect(240, 980, 121, 25))
        self.BacktoMenuButton.setObjectName("BacktoMenuButton")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(parent=self.page)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(840, 90, 1060, 840))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pyvistaframe = QFrame(self.horizontalLayoutWidget_2)
        self.pyvistaframe.setObjectName("pyvistaframe")
        self.pyvistaframe.setFrameShape(QFrame.Panel)
        self.pyvistaframe.setFrameShadow(QFrame.Raised)
        self.plotterloader = QtInteractor(
            self.pyvistaframe,
            line_smoothing=True,
            point_smoothing=True,
            polygon_smoothing=True,
            multi_samples=8,
        )
        self.plotterloader.enable()
        self.FilePathButton = QtWidgets.QPushButton(parent=self.page)
        self.FilePathButton.setGeometry(QtCore.QRect(100, 980, 89, 25))
        self.FilePathButton.setObjectName("FilePathButton")
        self.stackedWidget.addWidget(self.page)
        self.setupUi_Page2(MainWindow)

    # Page 2 Ui Setup
    def setupUi_Page2(self, MainWindow):
        self.page_2 = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.page_2.sizePolicy().hasHeightForWidth())
        self.page_2.setSizePolicy(sizePolicy)
        self.page_2.setObjectName("page_2")
        font1 = QFont()
        font1.setPointSize(30)
        self.seq1Button = QtWidgets.QPushButton(parent=self.page_2)
        self.seq1Button.setGeometry(QtCore.QRect(100, 210, 281, 171))
        self.seq1Button.setFont(font1)
        self.seq1Button.setObjectName("seq1Button")
        self.seq2Button = QtWidgets.QPushButton(parent=self.page_2)
        self.seq2Button.setGeometry(QtCore.QRect(100, 440, 281, 171))
        self.seq2Button.setObjectName("seq2Button_3")
        self.seq2Button.setFont(font1)
        self.seq3Button = QtWidgets.QPushButton(parent=self.page_2)
        self.seq3Button.setGeometry(QtCore.QRect(100, 660, 281, 171))
        self.seq3Button.setObjectName("seq3Button")
        self.seq3Button.setFont(font1)
        self.Itemlabel = QtWidgets.QLabel(parent=self.page_2)
        self.Itemlabel.setGeometry(QtCore.QRect(450, 30, 1079, 170))
        self.Itemlabel.setObjectName("Itemlabel")
        self.BackButton = QtWidgets.QPushButton(parent=self.page_2)
        self.BackButton.setGeometry(QtCore.QRect(220, 980, 80, 25))
        self.BackButton.setObjectName("BackButton")
        self.NextButton_Page_3 = QtWidgets.QPushButton(parent=self.page_2)
        self.NextButton_Page_3.setGeometry(QtCore.QRect(100, 980, 80, 25))
        self.NextButton_Page_3.setObjectName("NextButton_Page_3")
        self.NextButton_Page_3.hide()
        self.horizontalLayoutWidget = QtWidgets.QWidget(parent=self.page_2)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(660, 210, 1221, 691))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pyvistaframe_2 = QFrame(self.horizontalLayoutWidget)
        self.pyvistaframe_2.setObjectName("pyvistaframe_2")
        self.pyvistaframe_2.setFrameShape(QFrame.StyledPanel)
        self.pyvistaframe_2.setFrameShadow(QFrame.Raised)
        self.plotterloader_2 = QtInteractor(
            self.pyvistaframe_2,
            line_smoothing=True,
            point_smoothing=True,
            polygon_smoothing=True,
            multi_samples=8,
        )
        self.plotterloader_2.enable()
        self.stackedWidget.addWidget(self.page_2)
        self.button_UI(MainWindow)
        self.finalizeUI(MainWindow)

    def finalizeUI(self, MainWindow):
        self.retranslateUi(MainWindow)

    # button interaction
    def button_UI(self, MainWindow):
        self.NextButton_Page_2.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(2)
        )
        self.BacktoMenuButton.clicked.connect(
            lambda: backtomenudialog.Ui_Dialog_Confirm.show_dialog_confirm(
                MainWindow, self.stackedWidget
            )
        )
        self.FilePathButton.clicked.connect(self.browsefilesdirectory)
        self.BackButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))

    def on_selection_changed(self, index):
        model = self.Selectivefilelistview.model()
        self.file_path = model.filePath(index)
        file = self.Selectivefilelistview.model().itemData(index)[0]
        fileselectionmesh.FileSelectionMesh(
            self.horizontalLayout_2,
            self.horizontalLayout_4,
            self.file_path,
            self.plotterloader,
            self.plotterloader_2,
            self.pyvistaframe,
            self.pyvistaframe_2,
            self.horizontalLayoutWidget,
            self.horizontalLayoutWidget_2,
        )

        self.file = file.replace(".stl", "")
        self.NextButton_Page_2.show()

        _translate = QtCore.QCoreApplication.translate
        self.Itemlabel.setText(_translate("MainWindow", "Product : " + str(self.file)))
        mainframe_part2.Ui_MainWindow(
            self.file_path,
            self.stackedWidget,
            self.NextButton_Page_3,
            self.MainWindow,
            self.file,
            self.seq1Button,
            self.seq2Button,
            self.seq3Button,
        )

    # browse file directory
    def browsefilesdirectory(self):
        self.filepaths = QFileDialog.getExistingDirectory(
            None, "Choose Directory", self.filepaths
        )
        model = QFileSystemModel()
        model.setRootPath(self.filepaths)
        model.setFilter(QDir.NoDotAndDotDot | QDir.Files)
        self.Selectivefilelistview.setModel(model)
        self.Selectivefilelistview.setRootIndex(model.index(self.filepaths))
        self.Selectivefilelistview.setAlternatingRowColors(True)

    # Connect close event of the main window to a cleanup function
    def closeEvent(self, event):
        self.clearLayout()
        self.horizontalLayoutWidget.close()
        self.horizontalLayoutWidget_2.close()
        self.pyvistaframe.close()
        self.plotterloader.close()
        self.plotterloader_2.close()
        self.pyvistaframe_2.close()
        event.accept()

    def clearLayout(self):
        while self.horizontalLayout_2.count():
            child = self.horizontalLayout_2.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        while self.horizontalLayout_4.count():
            child = self.horizontalLayout_4.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.NextButton_Page_2.setText(_translate("MainWindow", "Next"))
        self.BacktoMenuButton.setText(_translate("MainWindow", "Back To Menu"))
        self.FilePathButton.setText(_translate("MainWindow", "File_Path"))
        self.seq1Button.setText(_translate("MainWindow", "Sequence 1"))
        self.seq2Button.setText(_translate("MainWindow", "Sequence 2"))
        self.seq3Button.setText(_translate("MainWindow", "Sequence 3"))
        self.Itemlabel.setText(_translate("MainWindow", "Product :"))
        self.BackButton.setText(_translate("MainWindow", "Back"))
        self.NextButton_Page_3.setText(_translate("MainWindow", "Next"))
