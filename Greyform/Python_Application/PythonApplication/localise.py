import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PythonApplication.BIMFile as Bimfile
import os
import PythonApplication.login as loginuiadmins


# localise for bim file, still undergo research for the calibration and localisation.
# Right now I only include animation for the loader
class localisationInterpretor(QWidget):
    def __init__(self, accountinfo, widget, userlabel, filename):
        super(localisationInterpretor, self).__init__()
        self.filename = filename
        self.form = uic.loadUi("UI_Design/localize.ui", self)
        self.accountinfo = accountinfo
        self.widget = widget
        self.userlabel = userlabel
        self.localizationloading()

    # home ui
    def localizationloading(self):
        self.form.stackedWidget_localisation.setCurrentIndex(0)
        self.font = QFont()
        self.dest_model = QStringListModel()
        self.form.modellocaliselistview.setModel(self.dest_model)
        current_list = self.dest_model.stringList()
        for i in range(len(self.filename)):
            if self.filename[i] in current_list:
                current_list.remove(self.filename[i])
            self.dest_model.insertRows(self.dest_model.rowCount(), 1)
            self.dest_model.setData(
                self.dest_model.index(self.dest_model.rowCount() - 1), self.filename[i]
            )
        self.form.uploaduiButton.clicked.connect(self.uploadpages)
        self.form.backtologinbutton.clicked.connect(self.loginpages)
        self.form.modellocaliselistview.clicked.connect(self.modelselected)

    # upload BIM pages
    def uploadpages(self):
        Bimfiles = Bimfile.BimfileInterpretor(
            self.accountinfo, self.widget, self.userlabel, self.filename
        )
        self.widget.addWidget(Bimfiles)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)

    # back to admin login
    def loginpages(self):
        Loginuiadmin = loginuiadmins.Login(
            self.accountinfo, self.widget, self.userlabel, self.filename
        )
        self.widget.addWidget(Loginuiadmin)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)

    # file model selected
    def modelselected(self, index):
        model = self.form.modellocaliselistview.model()
        if index.isValid():
            self.selected_item = self.dest_model.data(index, Qt.DisplayRole)
            self.form.modelselectedlabel.setText(str(self.selected_item) + " selected.")
            self.form.selectbutton.clicked.connect(self.selectpages)

    def selectpages(self):
        self.form.stackedWidget_localisation.setCurrentIndex(1)
        self.localtexts = [
            "Localisation in progress ...",
            "Localisation completed",
            "Deriving reference point …",
            "Reference point derived",
            "Deriving marking points …",
            "Marking points derived",
        ]
        self.form.localisationlabel.setText("")
        self.form.derivingreferlabel.setText("")
        self.form.markingpointslabel.setText("")
        self.current_text_index_local = self.letter_index_local = (
            0  # Index to keep track of which text we're showing
        )

        # Timer for showing letters
        self.letter_timer_local = QTimer(self)
        self.letter_timer_local.timeout.connect(self.show_next_letter_local)

        # Start with the first text after an initial delay
        QTimer.singleShot(
            10000, self.start_text_animation_local
        )  # 10 seconds before starting
        self.form.markingstartbutton.hide()
        self.form.redoprocessbutton.hide()
        self.form.markinglabelselected.hide()
        self.form.markinglistWidget.hide()
        self.form.selectmarkingbutton.hide()
        self.form.cancelbutton_2.hide()

    # select marking
    def onItemClicked(self, item):
        item_text = item.model().data(item, Qt.DisplayRole)
        self.item = item_text
        self.form.selectmarkingbutton.clicked.connect(self.selectedmarking)

    # marking is selected
    def selectedmarking(self):
        self.form.markinglabelselected.setText(str(self.item) + " selected")
        self.form.markinglabelselected.show()
        self.form.markinglistWidget.hide()
        self.form.selectmarkingbutton.hide()
        self.form.cancelbutton_2.hide()
        self.form.markingstartbutton.show()
        self.form.redoprocessbutton.show()
        self.form.markingstartbutton.clicked.connect(self.markingprocess)
        self.form.redoprocessbutton.clicked.connect(self.selectpages)

    # makring process ui
    def markingprocess(self):
        self.form.stackedWidget_localisation.setCurrentIndex(2)
        self.form.localisationlabelselected.setText(
            str(self.selected_item) + " selected"
        )
        self.marktexts = [
            "Marking left wall ...",
            "Left wall marked",
            "Marking front wall ...",
            "Front wall marked",
            "Marking right wall ...",
            "Right wall marked",
            "Marking floor ...",
            "Floor marked",
        ]
        self.form.leftwalllabel.setText("")
        self.form.frontwalllabel.setText("")
        self.form.rightwalllabel.setText("")
        self.form.floorlabel.setText("")
        self.current_text_index_mark = self.letter_index_mark = (
            0  # Index to keep track of which text we're showing
        )

        # Timer for showing letters
        self.letter_timer_mark = QTimer(self)
        self.letter_timer_mark.timeout.connect(self.show_next_letter_mark)

        # Start with the first text after an initial delay
        QTimer.singleShot(
            10000, self.start_text_animation_mark
        )  # 10 seconds before starting
        self.form.cancelloadButton.clicked.connect(self.selectpages)

    # localise animation
    def start_text_animation_local(self):
        if self.current_text_index_local < len(self.localtexts):
            self.show_next_letter_local()
            self.letter_timer_local.start(200)  # Speed of letters appearing

    # localize page animation
    def show_next_letter_local(self):
        text = None
        if self.current_text_index_local <= 1:
            text = self.localtexts[self.current_text_index_local]
            displayed_text = text[: self.letter_index_local + 1]
            self.form.localisationlabel.setText(displayed_text)
            self.letter_index_local += 1
        elif self.current_text_index_local <= 3:
            text = self.localtexts[self.current_text_index_local]
            displayed_text = text[: self.letter_index_local + 1]
            self.form.derivingreferlabel.setText(displayed_text)
            self.letter_index_local += 1
        elif self.current_text_index_local < len(self.localtexts):
            text = self.localtexts[self.current_text_index_local]
            displayed_text = text[: self.letter_index_local + 1]
            self.form.markingpointslabel.setText(displayed_text)
            self.letter_index_local += 1

        # Check if the entire text has been displayed
        if self.letter_index_local >= len(text):
            self.letter_timer_local.stop()
            # If it's the first text, prepare to start the second after a delay , etc
            if self.current_text_index_local < len(self.localtexts):
                self.current_text_index_local += 1
                self.letter_index_local = 0
                if self.current_text_index_local == len(self.localtexts):
                    self.current_text_index_local = 0
                    self.form.markinglistWidget.selectionModel().clearSelection()
                    self.form.markinglistWidget.show()
                    self.form.selectmarkingbutton.show()
                    self.form.cancelbutton_2.show()
                    self.form.markinglistWidget.clicked.connect(self.onItemClicked)
                    self.form.cancelbutton_2.clicked.connect(self.localizationloading)
                    return
                QTimer.singleShot(
                    10000, self.start_text_animation_local
                )  # 10 seconds before the second text starts

    # animation
    def start_text_animation_mark(self):
        if self.current_text_index_mark < len(self.marktexts):
            self.show_next_letter_mark()
            self.letter_timer_mark.start(200)  # Speed of letters appearing

    # marking page animation
    def show_next_letter_mark(self):
        text = None
        if self.current_text_index_mark <= 1:
            text = self.marktexts[self.current_text_index_mark]
            displayed_text = text[: self.letter_index_mark + 1]
            self.form.leftwalllabel.setText(displayed_text)
            self.letter_index_mark += 1
        elif self.current_text_index_mark <= 3:
            text = self.marktexts[self.current_text_index_mark]
            displayed_text = text[: self.letter_index_mark + 1]
            self.form.frontwalllabel.setText(displayed_text)
            self.letter_index_mark += 1
        elif self.current_text_index_mark <= 5:
            text = self.marktexts[self.current_text_index_mark]
            displayed_text = text[: self.letter_index_mark + 1]
            self.form.rightwalllabel.setText(displayed_text)
            self.letter_index_mark += 1
        elif self.current_text_index_mark < len(self.marktexts):
            text = self.marktexts[self.current_text_index_mark]
            displayed_text = text[: self.letter_index_mark + 1]
            self.form.floorlabel.setText(displayed_text)
            self.letter_index_mark += 1

        # Check if the entire text has been displayed
        if self.letter_index_mark >= len(text):
            self.letter_timer_mark.stop()
            # If it's the first text, prepare to start the second after a delay
            if self.current_text_index_mark <= len(self.marktexts):
                self.current_text_index_mark += 1
                self.letter_index_mark = 0
                if self.current_text_index_mark == len(self.localtexts):
                    self.current_text_index_mark = 0
                    self.form.markingcompletedlabel.setText(
                        str(self.item) + " completed"
                    )
                    return
                QTimer.singleShot(
                    10000, self.start_text_animation_mark
                )  # 10 seconds before the second text starts
