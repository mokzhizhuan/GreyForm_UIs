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
import re


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
                wall_finishes_dimensions = {}
                floor_dimensions = {}
                self.scale_factor = 1000.0
                marking_points = {}
                wall_offset, wall_finishes_offset, floor_finishes_offset = {}, {}, {}
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
                    plotter = pv.Plotter()
                    wallsformat = []
                    for wall in walls:
                        if "Basic Wall:BSS.50" in wall.Name:
                            shape = ifcopenshell.geom.create_shape(settings, wall)
                            verts = np.array(shape.geometry.verts).reshape(-1, 3)
                            faces = shape.geometry.faces
                            mesh = pv.PolyData()
                            mesh.points = verts
                            mesh.faces = np.hstack(
                                [
                                    [3, *faces[i : i + 3]]
                                    for i in range(0, len(faces), 3)
                                ]
                            )
                            plotter.add_mesh(mesh, color="lightgray", opacity=0.6)
                            width, wall_height, depth, offsets, wallcoordi = (
                                self.get_wall_dimensions(wall)
                            )
                            dimensions = self.get_wall_dimensions(wall)
                            if width and wall_height:
                                wall_dimensions[wall.Name] = {
                                    "width": int(round(width)),
                                    "height": int(round(wall_height)),
                                    "depth": int(round(depth)),
                                    "offset": int(round(offsets)),
                                }
                                wall_offset[wall.Name] = {
                                    "x": int(round(wallcoordi[0])),
                                    "y": int(round(wallcoordi[1])),
                                    "z": int(round(wallcoordi[2])),
                                }
                            wallsformat.append(
                                {
                                    "name": wall.Name,
                                    "global_id": wall.GlobalId,
                                    "center": mesh.center,
                                    "mesh": mesh,
                                }
                            )
                            if dimensions[0]:
                                widths.append(int(round(dimensions[0])))
                        if "BSS.20mm Wall Finishes" in wall.Name or "BSS.12mm Wall Finishes" in wall.Name:
                            width, height, depth, offset, wallfinishescoordi = (
                                self.get_wall_dimensions(wall)
                            )
                            wall_finishes_dimensions[wall.Name] = {
                                "width": int(round(width)),
                                "height": int(round(height)),
                                "depth": int(round(depth)),
                                "offset": offset,
                            }
                            wall_finishes_offset[wall.Name] = {
                                "width": int(round(wallfinishescoordi[0])),
                                "height": int(round(wallfinishescoordi[1])),
                                "depth": int(round(wallfinishescoordi[2])),
                            }
                    for floor in floors:
                        if "Floor" in floor.Name:
                            width, floor_height, depth, floor_offset, floorcoordi = (
                                self.get_wall_dimensions(wall)
                            )
                            floor_dimensions[floor.Name] = {
                                "width": int(round(width)),
                                "height": int(round(floor_height)),
                                "depth": int(round(depth)),
                                "offset": floor_offset,
                            }
                            floor_finishes_offset[floor.Name] = {
                                "width": int(round(floorcoordi[0])),
                                "height": int(round(floorcoordi[1])),
                                "depth": int(round(floorcoordi[2])),
                            }
                except Exception as e:
                    self.log_error(f"Error while processing IFC shapes: {e}")
                centers = np.array([w["center"] for w in wallsformat])
                x_min, x_max = centers[:, 0].min(), centers[:, 0].max()
                y_min, y_max = centers[:, 1].min(), centers[:, 1].max()
                x_range = x_max - x_min
                y_range = y_max - y_min
                south = [
                    w for w in wallsformat if w["center"][1] < y_min + y_range * 0.3
                ]
                north = [
                    w for w in wallsformat if w["center"][1] > y_min + y_range * 0.7
                ]
                remaining = [w for w in wallsformat if w not in south + north]
                west = [w for w in remaining if w["center"][0] < x_min + x_range * 0.3]
                east = [w for w in remaining if w["center"][0] > x_min + x_range * 0.7]
                south.sort(key=lambda w: w["center"][0])  # A
                west.sort(key=lambda w: -w["center"][0])  # B
                north.sort(key=lambda w: w["center"][0])  # C, E
                east.sort(key=lambda w: -w["center"][1])  # D (top), F (bottom)
                label_map = []
                label_letters = iter("ABCDEF")
                def detect_axis(mesh):
                    bounds = mesh.bounds
                    x_range = abs(bounds[1] - bounds[0])
                    y_range = abs(bounds[3] - bounds[2])
                    return "X" if x_range >= y_range else "Y"
                # South (front, left → right)
                if south:
                    south.sort(key=lambda w: w["center"][0])
                    for wall in south:
                        axis = detect_axis(wall["mesh"])
                        label_map.append((next(label_letters), wall, "South", axis))
                # West (left, bottom → top)
                if west:
                    west.sort(key=lambda w: w["center"][1])
                    for wall in west:
                        axis = detect_axis(wall["mesh"])
                        label_map.append((next(label_letters), wall, "West", axis))
                # North (back, left → right)
                if north:
                    north.sort(key=lambda w: w["center"][0])
                    for wall in north:
                        axis = detect_axis(wall["mesh"])
                        label_map.append((next(label_letters), wall, "North", axis))
                # East (right, top → bottom)
                if east:
                    east.sort(key=lambda w: -w["center"][1])
                    for wall in east:
                        axis = detect_axis(wall["mesh"])
                        label_map.append((next(label_letters), wall, "East", axis))
                label_map.sort(key=lambda x: x[0])  # sort by label A–F
                num_walls = len(label_map)
                x_widths = []  # for labels A, C, E (even index)
                y_heights = []  # for labels B, D, F (odd index)
                top_two = []
                for i, (label, wall, direction, axiss) in enumerate(label_map):
                    wall_name = wall["name"]
                    if wall_name in wall_dimensions:
                        wall_dimensions[wall_name]["label"] = label
                        width = wall_dimensions[wall_name].get("width", 0)
                        if i % 2 == 0:
                            x_widths.append(width)
                        else:  # Odd labels: B, D, F → Y axis
                            y_heights.append(width)
                directions = self.calculate_wall_directions(label_map)
                top_two = [
                    max(x_widths) + (wall_height * 2) if x_widths else 0,
                    max(y_heights) if y_heights else 0,
                ]
                wall_dimensions = dict(
                    sorted(
                        wall_dimensions.items(),
                        key=lambda item: item[1].get("label", "Z"),
                    )
                )
                self.convertStl(stl_data)
                wall_finishes_dimensions = self.validate_and_fix_wall_finishes(wall_finishes_dimensions)
                if len(wall_dimensions) == 6:
                    biminfo.Exportexcelinfo(
                        self.ifc_file,
                        "IfcElement",
                        wall_dimensions,
                        top_two,
                        offsets,
                        wall_finishes_dimensions,
                        floor_offset,
                        floor_height,
                        wall_finishes_offset,
                        wall_offset,
                        label_map,
                        directions
                    )
                else:
                    bim4sideinfo.Exportexcelinfo(
                        self.ifc_file,
                        "IfcElement",
                        wall_dimensions,
                        top_two,
                        offsets,
                        wall_finishes_dimensions,
                        floor_offset,
                        floor_height,
                        wall_finishes_offset,
                        wall_offset,
                        label_map,
                    )
                try:
                    self.stlloader()
                except Exception as e:
                    self.log_error(f"Failed to load stlfile in the frame: {e}")
        except Exception as e:
            self.log_error(
                f"Failed to initialize IFC geometry settings or iterator: {str(e)}"
            )
        self.close()

    def validate_and_fix_wall_finishes(self, wall_finishes_dimensions):
        invalid_walls = {}
        fixed_walls = {}
        expected_heights = self.get_expected_heights(wall_finishes_dimensions)
        for wall_name, dimensions in wall_finishes_dimensions.items():
            for wall_type, expected_height in expected_heights.items():
                if wall_type in wall_name:
                    if dimensions['height'] != expected_height and dimensions['width'] == expected_height:
                        dimensions['width'], dimensions['height'] = dimensions['height'], dimensions['width']
                    # Store the (fixed or correct) dimensions
                    fixed_walls[wall_name] = dimensions
                    break  # 
        return fixed_walls

    def get_expected_heights(self, wall_finishes_dimensions):
        expected_heights = {}
        for wall_name in wall_finishes_dimensions.keys():
            match = re.search(r'BSS\.(\d{2})mm Wall Finishes', wall_name)
            if match:
                height_value = int(match.group(1))
                wall_type = f"BSS.{height_value}mm Wall Finishes"
                if wall_type not in expected_heights:
                    expected_heights[wall_type] = height_value
        return expected_heights

    def calculate_wall_directions(self, label_map):
        directions = []
        num_walls = len(label_map)
        for i in range(num_walls):
            curr_label, curr_wall, curr_elevation, curr_axis = label_map[i]
            next_label, next_wall, next_elevation, next_axis = label_map[(i + 1) % num_walls]
            curr_center = curr_wall["center"]
            next_center = next_wall["center"]
            dx = next_center[0] - curr_center[0]
            dy = next_center[1] - curr_center[1]
            if curr_axis == "X":
                direction = "+X" if dx > 0 else "-X"
            elif curr_axis == "Y":
                direction = "+Y" if dy > 0 else "-Y"
            else:
                if abs(dx) > abs(dy):
                    direction = "+X" if dx > 0 else "-X"
                else:
                    direction = "+Y" if dy > 0 else "-Y"
            directions.append((curr_label, next_label, direction))
        return directions


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
        return None, None, None, None, None

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
        """Createmesh.createMesh(
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
        )"""
        self.close()
