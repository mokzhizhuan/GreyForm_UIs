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
import numpy as np


# ifc loader
class ProgressBarDialogIFC(QDialog):
    def __init__(self, total_steps, ifc_file, mainwindowforfileselection):
        # starting initialize
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
        self.Seqlabel = mainwindowforfileselection[13]
        self.localizebutton = mainwindowforfileselection[14]
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
                wall_dimensions = {}
                self.scale_factor = 1500.0
                try:
                    while True:
                        shape = iterator.get()
                        guid = shape.guid
                        element = self.ifc_file.by_guid(guid)
                        element_type = element.is_a() if element else "Unknown"
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
                            scaled_grouped_verts = np.array(grouped_verts) * self.scale_factor
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
                            # data array for STL
                        if not iterator.next():
                            break
                    walls = self.ifc_file.by_type('IfcWallStandardCase')
                    widths = []
                    for wall in walls:
                        if "Basic Wall:BSS.50" in wall.Name:
                            width, height , depth= self.get_wall_dimensions(wall)
                            dimensions = self.get_wall_dimensions(wall)
                            if width and height :
                                wall_dimensions[wall.Name] = {
                                    "width" : int(round(width)),
                                    "height" : int(round(height)),
                                    "depth" : int(round(depth)),
                                }
                            if dimensions[0]:  
                                widths.append(int(round(dimensions[0])))
                    if len(widths) > 1 and len(widths) == 6:
                        top_two = sorted(widths, reverse=True)[:2] 
                    elif len(widths) > 1 and len(widths) == 4:
                        top_two = sorted(widths, reverse=True)[:3] 
                        top_two[0] = top_two[0] + 50
                    else:
                        top_two = widths  
                except Exception as e:
                    self.log_error(f"Error while processing IFC shapes: {e}")
                self.convertStl(stl_data)
                if len(wall_dimensions) == 6 :
                    biminfo.Exportexcelinfo(self.ifc_file, "IfcElement", wall_dimensions, top_two)
                else:
                    bim4sideinfo.Exportexcelinfo(self.ifc_file, "IfcElement", wall_dimensions, top_two)
                try:
                    self.stlloader()
                except Exception as e:
                    self.log_error(f"Failed to load stlfile in the frame: {e}")
        except Exception as e:
            self.log_error(
                f"Failed to initialize IFC geometry settings or iterator: {str(e)}"
            )
        self.close()

    def get_wall_dimensions(self, wall):
        for representation in wall.Representation.Representations:
            if representation.RepresentationType == 'SweptSolid':
                solid = representation.Items[0]
                extruded_area = solid.SweptArea
                extrusion_depth = solid.Depth if hasattr(solid, 'Depth') else None
                if hasattr(extruded_area, 'XDim') and hasattr(extruded_area, 'YDim'):
                    width = extruded_area.XDim
                    height = extruded_area.YDim
                    return width, height , extrusion_depth
            elif representation.RepresentationIdentifier == 'Body' and representation.RepresentationType == 'Clipping':
                for item in representation.Items:
                    if item.is_a('IfcBooleanClippingResult'):
                        if item.FirstOperand.is_a('IfcExtrudedAreaSolid'):
                            extruded_area_solid = item.FirstOperand
                            depth = extruded_area_solid.Depth
                            profile = extruded_area_solid.SweptArea
                            width = profile.XDim
                            height = profile.YDim
                            return width, height, depth
        return None, None , None

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
        except Exception as e:
            self.log_error(f"Failed to write STL file: {e}")

    # add mesh in pyvista frame
    def stlloader(self):
        self.meshsplot = pv.read(self.stl_file)
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
            self.Seqlabel,
            self.stl_file,
        )
        self.close()
