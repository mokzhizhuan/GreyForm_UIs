from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class loadseqdata(object):
    # when selected how many sequence
    def on_selection_sequence(buttonseq, buttonnextpage, label):
        dataseqtext = buttonseq.text()
        dataseqtext = dataseqtext.replace("Sequence ", "")
        buttonnextpage.show()
        _translate = QtCore.QCoreApplication.translate
        label.setText(_translate("MainWindow", "Sequence: " + str(dataseqtext)))
