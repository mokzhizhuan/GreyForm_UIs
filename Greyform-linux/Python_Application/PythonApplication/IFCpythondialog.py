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
from PyQt5.QtCore import QTimer
import ifcopenshell
import ifcopenshell.geom
import meshio
import multiprocessing
import pandas as pd
import pyvista as pv
import PythonApplication.createmesh as Createmesh
import PythonApplication.loadpyvista as loadingstl
import PythonApplication.excel_export_info as biminfo
import numpy as np
import openpyxl


class ProgressBarDialogIFC(QDialog):
    def __init__(
        self,
        total_steps,
        ifc_file,
        plotterloader,
        plotterloader_2,
        renderer,
        renderWindowInteractor,
        Xlabel,
        Ylabel,
        Xlabel_before,
        Ylabel_before,
        Zlabel_before,
        append_filter,
        seq1Button,
        seq2Button,
        seq3Button,
        NextButton_Page_3,
        Seqlabel,
    ):
        super().__init__()
        progress_layout = QVBoxLayout()
        self.setLayout(progress_layout)
        self.setWindowTitle("IFC Conversion Progress")
        self.setGeometry(100, 100, 400, 100)
        self.ifc_file = ifc_file
        self.totalsteps = total_steps
        self.loader = plotterloader
        self.loader_2 = plotterloader_2
        self.renderer = renderer
        self.renderWindowInteractor = renderWindowInteractor
        self.Ylabel = Ylabel
        self.Xlabel = Xlabel
        self.Xlabel_before = Xlabel_before
        self.Ylabel_before = Ylabel_before
        self.Zlabel_before = Zlabel_before
        self.append_filter = append_filter
        self.meshsplot = None
        self.seq1Button = seq1Button
        self.seq2Button = seq2Button
        self.seq3Button = seq3Button
        self.NextButton_Page_3 = NextButton_Page_3
        self.Seqlabel = Seqlabel
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(30, 130, 340, 30)
        label = QLabel("Graphics is converting , please wait.")
        label.setGeometry(QtCore.QRect(50, 30, 170, 30))
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
            # Update progress again after 100 milliseconds
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
                        # Indices of vertices per triangle face
                        faces = shape.geometry.faces
                         # X Y Z of vertices in flattened list
                        verts = shape.geometry.verts
                        # Indices of material applied per triangle face
                        material_ids = shape.geometry.material_ids  
                        # Group vertices and faces appropriately
                        grouped_verts = [
                            [verts[i], verts[i + 1], verts[i + 2]]
                            for i in range(0, len(verts), 3)
                        ]
                        grouped_faces = [
                            [faces[i], faces[i + 1], faces[i + 2]]
                            for i in range(0, len(faces), 3)
                        ]
                        # Scale vertices
                        scaled_grouped_verts = np.array(grouped_verts) * scale_factor
                        # Collect data for STL
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
            vtk_offsets = np.concatenate(offset)
        else:
            vtk_cells = cells[0]
            vtk_offsets = offset[0]
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
            self.append_filter,
            self.seq1Button,
            self.seq2Button,
            self.seq3Button,
            self.NextButton_Page_3,
            self.Seqlabel,
        )
        self.close()
