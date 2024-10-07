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

#load 2 pyvista frame in the ui
class StLloaderpyvista(object):
    def __init__(self, meshsplot, loader, loader_2):
        self.meshsplot = meshsplot
        self.loader = loader
        self.loader_2 = loader_2
        self.loadstlframe()

    def loadstlframe(self):
        self.loader.remove_actor("roombuilding")
        self.loader_2.remove_actor("roombuilding")
        self.loader.update()
        self.loader_2.update()
        self.loader.add_mesh(
            self.meshsplot,
            color=(230, 230, 250),
            show_edges=False,
            edge_color=(128, 128, 128),
            cmap="terrain",
            clim=[1, 3],
            name="roombuilding",
            opacity="linear",
        )
        self.loader_2.add_mesh(
            self.meshsplot,
            color=(230, 230, 250),
            show_edges=False,
            edge_color=(128, 128, 128),
            cmap="terrain",
            clim=[1, 3],
            name="roombuilding",
            opacity="linear",
        )
        self.loader.show()
        self.loader_2.show()

    def log_points(self, message):
        with open("dimension.txt", "a") as log_file:
            log_file.write(message + "\n")
