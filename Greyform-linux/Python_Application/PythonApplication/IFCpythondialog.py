from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QDialog,
    QProgressBar,
    QLabel,
)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
import ifcopenshell
import ifcopenshell.geom
import meshio
import multiprocessing
import pyvista as pv
import PythonApplication.createmesh as Createmesh
import PythonApplication.loadpyvista as loadingstl
import PythonApplication.excel_export_info as biminfo
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)


class ProgressBarDialogIFC(QDialog):
    def __init__(self, total_steps, ifc_file, mainwindowforfileselection):
        super().__init__()
        progress_layout = QVBoxLayout()
        self.setLayout(progress_layout)
        self.setWindowTitle("IFC Conversion Progress")
        self.setGeometry(100, 100, 600, 200)
        self.ifc_file = ifc_file
        self.totalsteps = total_steps
        self.loader = mainwindowforfileselection[0]
        self.loader_2 = mainwindowforfileselection[1]
        self.renderer = mainwindowforfileselection[2]
        self.renderWindowInteractor = mainwindowforfileselection[3]
        self.Ylabel = mainwindowforfileselection[4]
        self.Xlabel = mainwindowforfileselection[5]
        self.Xlabel_before = mainwindowforfileselection[6]
        self.Ylabel_before = mainwindowforfileselection[7]
        self.Zlabel_before = mainwindowforfileselection[8]
        self.seq1Button = mainwindowforfileselection[9]
        self.seq2Button = mainwindowforfileselection[10]
        self.seq3Button = mainwindowforfileselection[11]
        self.NextButton_Page_3 = mainwindowforfileselection[12]
        self.Stagelabel = mainwindowforfileselection[13]
        self.localizebutton = mainwindowforfileselection[14]
        self.rosnode = mainwindowforfileselection[15]
        self.excelfiletext = mainwindowforfileselection[16]
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFont(QFont("Arial", 30))
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar.setGeometry(30, 130, 340, 200)
        label = QLabel("Graphics is converting , please wait.")
        label.setGeometry(QtCore.QRect(50, 30, 200, 100))
        label.setFont(QFont("Arial", 30))
        label.setWordWrap(True)
        label.setObjectName("label")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)
        progress_layout.addWidget(label)
        progress_layout.addWidget(self.progress_bar)
        self.start_progress()

    def start_progress(self):
        QTimer.singleShot(self.totalsteps, self.ifcprogramexecute)

    def update_progress(self):
        value = self.progress_bar.value()
        if value < 100:
            self.progress_bar.setValue(value + 1)
            # Update progress again after 100%
            QTimer.singleShot(100, self.update_progress)
        else:
            self.timer.stop()  # Stop the timer when progress reaches 100%
            self.progress_bar.setValue(0)  # Reset progress to 0
            self.timer.start(100)

    def ifcprogramexecute(self):
        self.update_progress()
        try:
            settings = ifcopenshell.geom.settings()
            settings.set(settings.USE_WORLD_COORDS, True)
            iterator = ifcopenshell.geom.iterator(
                settings, self.ifc_file, multiprocessing.cpu_count()
            )
            if iterator.initialize():
                stl_data = {"points": [], "cells": [], "material_ids": []}
                scale_factor = 1500.0
                # Collect all unique element types
                biminfo.Exportexcelinfo(self.ifc_file, "IfcElement")
                try:
                    while True:
                        shape = iterator.get()
                        guid = shape.guid
                        element = self.ifc_file.by_guid(guid)
                        element_type = element.is_a() if element else "Unknown"
                        faces = shape.geometry.faces
                        verts = shape.geometry.verts
                        material_ids = shape.geometry.material_ids
                        grouped_verts = [
                            [verts[i], verts[i + 1], verts[i + 2]]
                            for i in range(0, len(verts), 3)
                        ]
                        grouped_faces = [
                            [faces[i], faces[i + 1], faces[i + 2]]
                            for i in range(0, len(faces), 3)
                        ]
                        scaled_grouped_verts = np.array(grouped_verts) * scale_factor
                        if element_type != "IfcOpeningElement":
                            stl_vert_index_offset = len(stl_data["points"])
                            stl_data["points"].extend(scaled_grouped_verts)
                            stl_data["cells"].extend(
                                [
                                    [
                                        face[0] + stl_vert_index_offset,
                                        face[1] + stl_vert_index_offset,
                                        face[2] + stl_vert_index_offset,
                                    ]
                                    for face in grouped_faces
                                ]
                            )
                            stl_data["material_ids"].extend(material_ids)
                        if not iterator.next():
                            break
                except Exception as e:
                    self.log_error(f"Error while processing IFC shapes: {e}")
                self.convertStl(stl_data)
                try:
                    self.stlloader()
                except Exception as e:
                    self.log_error(f"Failed to load stlfile in the frame: {e}")
        except Exception as e:
            self.log_error(
                f"Failed to initialize IFC geometry settings or iterator: {str(e)}"
            )
        self.close()

    def log_error(self, message):
        with open("error_log.txt", "a") as log_file:
            log_file.write(message + "\n")

    # Convert to meshio format and write to STL
    def convertStl(self, data):
        try:
            points = np.array(data["points"])
            cells = [("triangle", np.array(data["cells"]))]
            # Create material ID array for each face
            self.stl_file = "output.stl"
            mesh = meshio.Mesh(points=points, cells=cells)
            mesh.cell_data["triangle"] = [np.array(data["material_ids"])]
            meshio.write(self.stl_file, mesh)
            self.meshsplot = pv.read(self.stl_file)
        except Exception as e:
            self.log_error(f"Failed to write STL file: {e}")

    # add mesh in pyvista frame
    def stlloader(self):
        meshs = meshio.read(self.stl_file)
        offset = []
        cells = []
        cell_types = []
        for cell_block in meshs.cells:
            cell_type = cell_block.type
            cell_data = cell_block.data
            num_points_per_cell = cell_data.shape[1]
            offsets = np.arange(
                start=num_points_per_cell,
                stop=num_points_per_cell * (len(cell_data) + 1),
                step=num_points_per_cell,
            )
            offset.append(offsets)
            cells.append(
                np.hstack(
                    (np.full((len(cell_data), 1), num_points_per_cell), cell_data)
                ).flatten()
            )
            cell_types.append(cell_type)
        if len(cells) > 1:
            vtk_cells = np.concatenate(cells)
        else:
            vtk_cells = cells[0]
        self.meshsplot = pv.PolyData(meshs.points, vtk_cells)
        loadingstl.StLloaderpyvista(self.meshsplot, self.loader, self.loader_2)
        Createmesh.createMesh(
            self.renderer,
            self.stl_file,
            self.renderWindowInteractor,
            self.Ylabel,
            self.Xlabel,
            self.Xlabel_before,
            self.Ylabel_before,
            self.Zlabel_before,
            self.seq1Button,
            self.seq2Button,
            self.seq3Button,
            self.NextButton_Page_3,
            self.Stagelabel,
            self.localizebutton,
            self.rosnode,
            self.stl_file,
            self.excelfiletext,
        )
        self.close()
