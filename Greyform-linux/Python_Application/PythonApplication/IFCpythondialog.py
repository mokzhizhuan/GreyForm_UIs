from PyQt5 import QtCore
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
import PythonApplication.excel_export_4sidesinfo as bim4sideinfo
import PythonApplication.processloader as Thread
import PythonApplication.processlistenerrunner as process
import numpy as np
import os


# ifc loader
class ProgressBarDialogIFC(QDialog):
    def __init__(self, total_steps, ifc_file, mainwindowforfileselection, mainwindow ,stackedWidget):
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
        self.listenerdialog = process.ListenerNodeRunner(
            self.rosnode, self.ifc_file, self.labelstatus, self.stackedWidget
        )
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
            # Update progress again after 100 milliseconds
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
                self.wall_dimensions = {}
                self.wall_finishes_dimensions = {}
                self.floor_dimensions = {}
                self.scale_factor = 1000.0
                marking_points = {}
                self.wall_offset, self.wall_finishes_offset, floor_finishes_offset = {}, {}, {}
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
                            # data array for STL
                        if not iterator.next():
                            break
                    walls = self.ifc_file.by_type("IfcWallStandardCase")
                    widths = []
                    floors = self.ifc_file.by_type("IfcSlab")
                    for wall in walls:
                        if "Basic Wall:BSS.50" in wall.Name:
                            width, height, depth, self.offsets, wallcoordi = (
                                self.get_wall_dimensions(wall)
                            )
                            dimensions = self.get_wall_dimensions(wall)
                            if width and height:
                                self.wall_dimensions[wall.Name] = {
                                    "width": int(round(width)),
                                    "height": int(round(height)),
                                    "depth": int(round(depth)),
                                    "offset": int(round(self.offsets)),
                                }
                                self.wall_offset[wall.Name] = {
                                    "x": int(round(wallcoordi[0])),
                                    "y": int(round(wallcoordi[1])),
                                    "z": int(round(wallcoordi[2])),
                                }
                            if dimensions[0]:
                                widths.append(int(round(dimensions[0])))
                        if "BSS.20mm Wall Finishes" in wall.Name:
                            width, height, depth, offset, wallfinishescoordi = (
                                self.get_wall_dimensions(wall)
                            )
                            self.wall_finishes_dimensions[wall.Name] = {
                                "width": int(round(width)),
                                "height": int(round(height)),
                                "depth": int(round(depth)),
                                "offset": offset,
                            }
                            self.wall_finishes_offset[wall.Name] = {
                                "width": int(round(wallfinishescoordi[0])),
                                "height": int(round(wallfinishescoordi[1])),
                                "depth": int(round(wallfinishescoordi[2])),
                            }
                    for floor in floors:
                        if "Floor" in floor.Name:
                            width, self.floor_height, depth, self.floor_offset, floorcoordi = (
                                self.get_wall_dimensions(wall)
                            )
                            self.floor_dimensions[floor.Name] = {
                                "width": int(round(width)),
                                "height": int(round(self.floor_height)),
                                "depth": int(round(depth)),
                                "offset": self.floor_offset,
                            }
                            floor_finishes_offset[floor.Name] = {
                                "width": int(round(floorcoordi[0])),
                                "height": int(round(floorcoordi[1])),
                                "depth": int(round(floorcoordi[2])),
                            }
                    if len(widths) > 1 and len(widths) == 6:
                        self.top_two = sorted(widths, reverse=True)[:2]
                        self.top_two[0] = self.top_two[0] + 100
                    elif len(widths) > 1 and len(widths) == 4:
                        self.top_two = sorted(widths, reverse=True)[:3]
                        self.top_two[0] = self.top_two[0] + 50
                    else:
                        top_two = widths
                except Exception as e:
                    self.log_error(f"Error while processing IFC shapes: {e}")
                self.convertStl(stl_data)
                self.buttonlocalize.clicked.connect(lambda: self.start_scan())
        except Exception as e:
            self.log_error(
                f"Failed to initialize IFC geometry settings or iterator: {str(e)}"
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
        """Update the progress bar with the current value."""
        self.scanprogressBar.setValue(value)  # Ensure progressBar is properly defined in your UI

    def update_status_label(self, text):
        """Update the status label with progress text."""
        self.labelstatus.setText(text)
    
    def create_mesh(self):
        # Call the createMesh function in the main thread
        try:
            if len(self.wall_dimensions) == 6:
                self.loadexcel()
            else:
                self.loadexcel4sides()
            self.stlloader()
        except Exception as e:
            self.log_error(f"Failed to load stlfile in the frame: {e}")


    def get_wall_dimensions(self, wall):
        placement = wall.ObjectPlacement
        if placement:
            if hasattr(placement, "RelativePlacement"):
                rel_placement = placement.RelativePlacement
                if hasattr(rel_placement, "Location"):
                    location = rel_placement.Location
                    coordinates = location.Coordinates
                    offset = abs(coordinates[2])
        for representation in wall.Representation.Representations:
            if representation.RepresentationType == "SweptSolid":
                solid = representation.Items[0]
                extruded_area = solid.SweptArea
                extrusion_depth = solid.Depth if hasattr(solid, "Depth") else None
                if hasattr(extruded_area, "XDim") and hasattr(extruded_area, "YDim"):
                    width = extruded_area.XDim
                    height = extruded_area.YDim
                    return width, height, extrusion_depth, offset, coordinates
            elif (
                representation.RepresentationIdentifier == "Body"
                and representation.RepresentationType == "Clipping"
            ):
                for item in representation.Items:
                    if item.is_a("IfcBooleanClippingResult"):
                        if item.FirstOperand.is_a("IfcExtrudedAreaSolid"):
                            extruded_area_solid = item.FirstOperand
                            depth = extruded_area_solid.Depth
                            profile = extruded_area_solid.SweptArea
                            width = profile.XDim
                            height = profile.YDim
                            return width, height, depth, offset, coordinates
        return None, None, None

    # include error in text file
    def log_error(self, message):
        with open("error_log.txt", "a") as log_file:
            log_file.write(message + "\n")

    def log(self, message):
        with open("log.txt", "a") as log_file:
            log_file.write(message + "\n")

    # Convert to meshio format and write to STL
    def convertStl(self, data):
        try:
            points = np.array(data["points"])
            message = f"Points: {self.spacing}"
            cells = [("triangle", np.array(data["cells"]))]
            self.stl_file = "output.stl"
            mesh = meshio.Mesh(points=points, cells=cells)
            mesh.cell_data["triangle"] = [np.array(data["material_ids"])]
            meshio.write(self.stl_file, mesh)
            self.meshsplot = pv.read(self.stl_file)
            loadingstl.StLloaderpyvista(self.meshsplot, self.loader)
        except Exception as e:
            self.log_error(f"Failed to write STL file: {e}")

    def loadexcel(self):
        biminfo.Exportexcelinfo(
            self.ifc_file,
            "IfcElement",
            self.wall_dimensions,
            self.top_two,
            self.offsets,
            self.wall_finishes_dimensions,
            self.floor_offset,
            self.floor_height,
            self.wall_finishes_offset,
            self.wall_offset,
        )
    
    def loadexcel4sides(self):
        bim4sideinfo.Exportexcelinfo(
            self.ifc_file,
            "IfcElement",
            self.wall_dimensions,
            self.top_two,
            self.offsets,
            self.wall_finishes_dimensions,
            self.floor_offset,
            self.floor_height,
            self.wall_finishes_offset,
            self.wall_offset
        )

    # add mesh in pyvista frame
    def stlloader(self):
        Createmesh.createMesh(
            self.renderer,
            self.stl_file,
            self.renderWindowInteractor,
            self.rosnode,
            self.stl_file,
            self.mainwindow,
            self.Stagelabel,
            self.walllabel,
            self.stackedWidget,
            self.listenerdialog,
        )