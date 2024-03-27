import sys
from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import OpenGL.GL as gl
import pyqtgraph.opengl as gl
import ifcopenshell
import ifcopenshell.geom
from ifcopenshell.util.placement import get_local_placement
from pyvistaqt import QtInteractor
import multiprocessing
import PythonApplication.progressBar as Progress


#load pyvista in the frame
class FileSelectionMesh(QMainWindow):
    def __init__(
        self,
        horizontalLayout,
        horizontalLayout_page2,
        file_path,
        plotterloader,
        plotterloader_2,
        pyvistaframe,
        pyvistaframe_2,
        layoutWidget,
        layoutWidget_page2,
    ):
        self.horizontalLayout = horizontalLayout
        self.horizontalLayout_page2 = horizontalLayout_page2
        self.plotterloader = plotterloader
        self.plotterloader_2 = plotterloader_2
        self.pyvistaframe = pyvistaframe
        self.pyvistaframe_2 = pyvistaframe_2
        self.layoutwidget = layoutWidget
        self.layoutwidget_page2 = layoutWidget_page2
        self.file_path = file_path
        self.meshdata()

    # load meshdata from file
    def meshdata(self):
        # load glviewer in ifc
        if "ifc" in self.file_path:
            self.viewer = gl.GLViewWidget()
            self.viewer_page2 = gl.GLViewWidget()
            self.clearLayout()
            self.horizontalLayout.addWidget(self.viewer, 1)
            self.horizontalLayout_page2.addWidget(self.viewer_page2, 1)
            # clear all item
            self.viewer.clear()
            self.viewer_page2.clear()
            FileSelectionMesh.loadmeshinGLView(self, self.file_path)
        else:  # load mesh in pyvista from STL
            # clear mesh
            self.clearLayout()
            self.horizontalLayout.addWidget(self.plotterloader.interactor)
            self.horizontalLayout_page2.addWidget(self.plotterloader_2.interactor)
            progressbarprogram = Progress.pythonProgressBar(
                100000, self.plotterloader, self.plotterloader_2, self.file_path
            )
            progressbarprogram.exec_()

    # clear layout
    def clearLayout(self):
        while self.horizontalLayout.count():
            child = self.horizontalLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        while self.horizontalLayout_page2.count():
            child = self.horizontalLayout_page2.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # load mesh in GLViewWidget
    def loadmeshinGLView(self, file_path):
        try:
            ifc_file = ifcopenshell.open(file_path)
        except:
            print(ifcopenshell.get_log())
        else:
            settings = ifcopenshell.geom.settings()
            iterator = ifcopenshell.geom.iterator(
                settings, ifc_file, multiprocessing.cpu_count()
            )
            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    element = ifc_file.by_guid(shape.guid)
                    faces = (
                        shape.geometry.faces
                    )  # Indices of vertices per triangle face e.g. [f1v1, f1v2, f1v3, f2v1, f2v2, f2v3, ...]
                    verts = (
                        shape.geometry.verts
                    )  # X Y Z of vertices in flattened list e.g. [v1x, v1y, v1z, v2x, v2y, v2z, ...]
                    materials = (
                        shape.geometry.materials
                    )  # Material names and colour style information that are relevant to this shape
                    material_ids = (
                        shape.geometry.material_ids
                    )  # Indices of material applied per triangle face e.g. [f1m, f2m, ...]

                    # Since the lists are flattened, you may prefer to group them per face like so depending on your geometry kernel
                    grouped_verts = [
                        [verts[i], verts[i + 1], verts[i + 2]]
                        for i in range(0, len(verts), 3)
                    ]
                    grouped_faces = [
                        [faces[i], faces[i + 1], faces[i + 2]]
                        for i in range(0, len(faces), 3)
                    ]
                    if not iterator.next():
                        break
                    FileSelectionMesh.showmesh(self, grouped_verts, grouped_faces)

    # showmesh in GLView for ifc file
    def showmesh(self, grouped_verts, grouped_faces):
        meshdata = gl.MeshData(vertexes=grouped_verts, faces=grouped_faces)
        mesh = gl.GLMeshItem(
            meshdata=meshdata,
            smooth=True,
            drawFaces=False,
            drawEdges=True,
            edgeColor=(0, 1, 0, 1),
        )
        self.viewer.addItem(mesh)
        self.viewer_page2.addItem(mesh)

    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        self.horizontalLayout.close()
        self.horizontalLayout_page2.close()
        self.pyvistaframe.close()
        self.plotterloader.close()
        self.plotterloader_2.close()
        self.pyvistaframe_2.close()
        self.plotterloader.GetRenderWindow().Finalize()
        self.plotterloader_2.GetRenderWindow().Finalize()
