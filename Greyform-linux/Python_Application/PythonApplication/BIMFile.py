import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PythonApplication.login as Login
import os
import PythonApplication.localise as localisewin


class CustomFileSystemModel(QFileSystemModel):
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and index.isValid():
            if index.column() == 0:
                file_info = self.fileInfo(index)
                file_name = file_info.fileName()
                created_date = file_info.created().toString("d/M/yyyy")  # Format date
                return f"{file_name} {created_date}"
        return super().data(index, role)


class BimfileInterpretor(QWidget):
    def __init__(self, accountinfo, widget, userlabel, file):
        super(BimfileInterpretor, self).__init__()
        self.file = file
        self.form = uic.loadUi("UI_Design/BIMFile.ui", self)
        self.accountinfo = accountinfo
        self.widget = widget
        self.userlabel = userlabel
        self.filepaths = os.getcwd()
        self.font = QFont()
        self.dest_model = QStringListModel()
        self.buttonUI()

    def buttonUI(self):
        self.form.BacktoLoginButton.clicked.connect(self.login)
        self.form.ExitButton.clicked.connect(self.localize)
        self.form.UploadButton.clicked.connect(self.uploadfile)
        self.form.DeleteButton.clicked.connect(self.deletefile)
        self.form.uploadlistView.clicked.connect(self.on_selection_changed)
        self.form.UploadconfirmButton.clicked.connect(self.Uploadcompleted)
        self.form.deletelistView.clicked.connect(self.removeSelectedText)

    def login(self):
        LoginUI = Login.Login(self.accountinfo, self.widget, self.userlabel)
        self.widget.addWidget(LoginUI)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)

    def uploadfile(self):
        self.form.stackedWidgetbimfile.setCurrentIndex(1)
        self.form.FilePathButton.clicked.connect(self.browsefilesdirectory)

    def deletefile(self):
        self.form.stackedWidgetbimfile.setCurrentIndex(3)
        self.dest_model = QStringListModel()
        # Set font size
        self.font.setPointSize(12)  # Set your desired font size here
        self.form.deletelistView.setFont(self.font)
        self.form.deletelistView.setModel(self.dest_model)
        for i in range(len(self.file)):
            self.dest_model.insertRows(self.dest_model.rowCount(), 1)
            self.dest_model.setData(self.dest_model.index(self.dest_model.rowCount() - 1), self.file[i])

    # browse file directory
    def browsefilesdirectory(self):
        self.filepaths = QFileDialog.getExistingDirectory(None, "Choose Directory")
        if self.filepaths:
            # Create QFileSystemModel and set directory
            model = CustomFileSystemModel()

            model.setRootPath(self.filepaths)
            # Set filter to only show files and directories
            model.setFilter(QDir.NoDotAndDotDot | QDir.Files)

            # Set filter to only show .ifc files
            model.setNameFilters(["*.ifc"])
            model.setNameFilterDisables(False)

            self.form.uploadlistView.setModel(model)
            self.form.uploadlistView.setRootIndex(model.index(self.filepaths))
            self.form.uploadlistView.setAlternatingRowColors(True)
            self.form.uploadlistView.setSelectionMode(QListView.SingleSelection)
            self.form.uploadlistView.setSelectionBehavior(QListView.SelectRows)
            self.form.uploadlistView.setEditTriggers(QListView.NoEditTriggers)
            # Display creation date in dd/mm/yyyy format
            self.form.uploadlistView.setStyleSheet("QListView::item { padding: 5px; }")
            # Set font size
            self.font.setPointSize(12)  # Set your desired font size here
            self.form.uploadlistView.setFont(self.font)
            model.setHeaderData(0, Qt.Horizontal, "File Name")
            self.form.uploadlistView.setModel(model)
            self.form.uploadlistView.show()

    def on_selection_changed(self, index):
        model = self.form.uploadlistView.model()
        self.file_path = model.filePath(index)
        file_info = model.fileInfo(index)
        file = file_info.fileName()
        self.files = file.replace(".ifc", "")
        self.file.append(self.files)
        self.form.modeltextEdit.setReadOnly(True)
        self.form.modeltextEdit.setPlainText(self.files)

    def Uploadcompleted(self):
        self.form.stackedWidgetbimfile.setCurrentIndex(2)
        self.form.deletelistView.setModel(self.dest_model)
        for i in range(len(self.file)):
            self.dest_model.insertRows(self.dest_model.rowCount(), 1)
            self.dest_model.setData(self.dest_model.index(self.dest_model.rowCount() - 1), self.file[i])

    def removeSelectedText(self):
        self.selected_indexes = self.form.deletelistView.selectedIndexes()
        self.form.DeleteconfirmButton.clicked.connect(self.removelist)

    def removelist(self):
        rows_to_remove = [index.row() for index in self.selected_indexes]
        self.dest_model = self.form.deletelistView.model()
        for row in sorted(rows_to_remove, reverse=True):
            self.dest_model.removeRow(row)
        self.form.stackedWidgetbimfile.setCurrentIndex(4)

    def localize(self):
        localise = localisewin.localisationInterpretor(
            self.accountinfo, self.widget, self.userlabel, self.file
        )
        self.widget.addWidget(localise)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
