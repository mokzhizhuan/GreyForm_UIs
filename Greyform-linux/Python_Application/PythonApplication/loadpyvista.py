from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QDialog,
    QProgressBar,
    QLabel,
)
import pyvista as pv


class StLloaderpyvista(object):
    def __init__(self, meshsplot, loader, loader_2):
        self.meshsplot = meshsplot
        self.loader = loader
        self.loader_2 = loader_2
        self.loadstl()

    def loadstl(self):
        self.loader.add_mesh(
            self.meshsplot,
            color=(230, 230, 250),
            show_edges=True,
            edge_color=(128, 128, 128),
            cmap="terrain",
            clim=[1, 3],
            name="roombuilding",
            opacity="linear",
        )
        self.loader_2.add_mesh(
            self.meshsplot,
            color=(230, 230, 250),
            show_edges=True,
            edge_color=(128, 128, 128),
            cmap="terrain",
            clim=[1, 3],
            name="roombuilding",
            opacity="linear",
        )
        # show Frame
        self.loader.show()
        self.loader_2.show()
