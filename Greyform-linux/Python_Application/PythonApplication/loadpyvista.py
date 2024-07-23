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
        self.loader.remove_actor("roombuilding")
        self.loader_2.remove_actor("roombuilding")
        self.loader.remove_actor("edges")
        self.loader_2.remove_actor("edges")
        self.loader.update()
        self.loader_2.update()
        edges = self.meshsplot.extract_feature_edges(
            boundary_edges=False,
            non_manifold_edges=True,
            feature_edges=False,
            manifold_edges=True,
        )
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
        self.loader.add_mesh(edges, color="black", line_width=2 ,name="edges")
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
        self.loader_2.add_mesh(edges, color="black", line_width=2 ,name="edges")
        # show Frame
        self.loader.show()
        self.loader_2.show()
