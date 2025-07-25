from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QProgressBar, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
import ifcopenshell
import ifcopenshell.geom
import meshio
import multiprocessing
import pyvista as pv
import PythonApplication.createmesh as Createmesh
import PythonApplication.loadpyvista as loadingstl
import PythonApplication.processloader as Thread
import PythonApplication.processlistenerrunner as process
import PythonApplication.ifcextractmaterials as ifcmaterials
import PythonApplication.robotplacementrobot as robotplacemats
import numpy as np
import ifcopenshell.util.element as Element
import re
from collections import OrderedDict
import PythonApplication.dataanalysis as datadraft


# ifc loader
class ProgressBarDialogIFC(QDialog):
    def __init__(
        self,
        total_steps,
        ifc_file,
        mainwindowforfileselection,
        mainwindow,
        stackedWidget,
    ):
        # starting initialize
        super().__init__()
        progress_layout = QVBoxLayout()
        self.setLayout(progress_layout)
        self.setWindowTitle("IFC Conversion Progress")
        self.setGeometry(100, 100, 600, 200)
        self.ifc_file = ifc_file
        self.totalsteps = total_steps
        self.mainwindow = mainwindow
        self.stackedWidget = stackedWidget
        self.loader = mainwindowforfileselection[0]
        self.renderer = mainwindowforfileselection[1]
        self.renderWindowInteractor = mainwindowforfileselection[2]
        self.rosnode = mainwindowforfileselection[3]
        self.Stagelabel = mainwindowforfileselection[6]
        self.buttonlocalize = mainwindowforfileselection[5]
        self.stagestoring = mainwindowforfileselection[7]
        self.labelstatus = mainwindowforfileselection[8]
        self.scanprogressBar = mainwindowforfileselection[9]
        self.walllabel = mainwindowforfileselection[10]
        self.args = mainwindowforfileselection[11]
        self.spacing = "\n"
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
            QTimer.singleShot(100, self.update_progress)
        else:
            self.timer.stop()  # Stop the timer when progress reaches 100%
            self.progress_bar.setValue(0)  # Reset progress to 0
            self.timer.start(100)

    # execute loading ifc program
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
                self.scale_factor = 1000.0
                marking_points = {}
                try:
                    while True:
                        shape = iterator.get()
                        guid = shape.guid
                        element = self.ifc_file.by_guid(guid)
                        element_type = element.is_a() if element else "Unknown"
                        element_name = (
                            element.Name
                            if element and hasattr(element, "Name")
                            else "Unnamed"
                        )
                        if element_type.lower() != "ifcopeningelement":
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
                            scaled_grouped_verts = (
                                np.array(grouped_verts) * self.scale_factor
                            )
                            stl_vert_index_offset = len(stl_data["points"])
                            marking_points[element_name] = {
                                "Marking": scaled_grouped_verts
                            }
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
                        floors = self.ifc_file.by_type("IfcSlab")
                        all_floor_points = []
                        all_floor_faces = []
                        point_offset = 0
                        for floor in floors:
                            container = Element.get_container(floor)
                            if floor.Representation is None:
                                continue  # Skip floors without geometry
                            if "bedroom" in container.Name.lower():
                                shape = ifcopenshell.geom.create_shape(settings, floor)
                                verts = np.array(shape.geometry.verts).reshape(-1, 3)
                                faces = np.array(shape.geometry.faces).reshape(-1, 3)
                                scaled_grouped_verts = (
                                    np.array(verts) * self.scale_factor
                                )
                                scaled_grouped_verts[:, 2] -= scaled_grouped_verts[
                                    :, 2
                                ].min()
                                all_floor_points.append(scaled_grouped_verts)
                                adjusted_faces = faces + point_offset
                                all_floor_faces.append(adjusted_faces)
                                point_offset += verts.shape[0]
                        all_floor_points = np.vstack(all_floor_points)
                        all_floor_faces = np.vstack(all_floor_faces)
                        floor_mesh = meshio.Mesh(
                            points=all_floor_points,
                            cells=[("triangle", all_floor_faces)],
                        )
                        meshio.write(self.args.floor_stl, floor_mesh)
                except Exception as e:
                    ifcmaterials.log_error(f"Error while processing IFC shapes: {e}")
                datadrafter = datadraft.data_draft(self.ifc_file, self.args)
                (
                    self.count_plus_y,
                    self.count_minus_y,
                    self.excelfile,
                    self.wallformat,
                    self.axis_widths,
                ) = datadrafter.analysis()
                self.convertStl(stl_data)
                self.listenerdialog = process.ListenerNodeRunner(
                    self.rosnode, self.stl_file, self.labelstatus, self.stackedWidget
                )
                self.buttonlocalize.clicked.connect(lambda: self.start_scan())
        except Exception as e: 
            import traceback
            import inspect
            frame = inspect.currentframe()
            filename = inspect.getfile(frame)
            lineno = frame.f_lineno
            ifcmaterials.log_error(
                f"Failed to initialize IFC geometry settings or iterator: {str(e)} "
                f"(File \"{filename}\", Line {lineno})"
            )
        self.close()

    def start_scan(self):
        self.stackedWidget.setCurrentIndex(3)
        self.worker = Thread.WorkerThread(self.listenerdialog, self.stackedWidget)
        self.worker.update_progress.connect(self.update_progress_bar)
        self.worker.update_status.connect(self.update_status_label)
        self.worker.render_mesh.connect(self.create_mesh)  # Connect new signal
        self.worker.start()  # Start the worker thread

    def update_progress_bar(self, value):
        self.scanprogressBar.setValue(value)

    def update_status_label(self, text):
        self.labelstatus.setText(text)

    def create_mesh(self):
        self.stlloader()

    # Convert to meshio format and write to STL
    def convertStl(self, data):
        points = np.array(data["points"])
        cells = [("triangle", np.array(data["cells"]))]
        self.stl_file = self.args.output_stl
        mesh = meshio.Mesh(points=points, cells=cells)
        mesh.cell_data["triangle"] = [np.array(data["material_ids"])]
        meshio.write(self.stl_file, mesh)
        self.meshsplot = pv.read(self.stl_file)
        self.meshbounds = self.meshsplot.bounds
        robotplacement = robotplacemats.robotplacement(
            self.count_plus_y, self.count_minus_y, self.meshbounds
        )
        objectrobot = [500, 500, 500]
        wall1_position = robotplacement[0]["Wall 1"]
        cube_center = [
            wall1_position[0],
            wall1_position[1],
            wall1_position[2] + objectrobot[2] / 2,
        ]
        robot_cube = pv.Cube(
            center=cube_center,
            x_length=objectrobot[0],
            y_length=objectrobot[1],
            z_length=objectrobot[2],
        )
        self.meshsplots = pv.read(self.args.floor_stl)
        loadingstl.StLloaderpyvista(
            self.meshsplots, self.loader, robot_cube, wall1_position
        )

    # add mesh in pyvista frame
    def stlloader(self):
        Createmesh.createMesh(
            self.renderer,
            self.stl_file,
            self.renderWindowInteractor,
            self.stl_file,
            self.mainwindow,
            self.Stagelabel,
            self.walllabel,
            self.stackedWidget,
            self.count_plus_y,
            self.count_minus_y,
            self.excelfile,
            self.wallformat,
            self.axis_widths,
            self.listenerdialog 
        )
