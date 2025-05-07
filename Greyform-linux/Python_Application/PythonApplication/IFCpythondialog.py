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
import PythonApplication.ifcextractmaterials as ifcmaterials
import ifcopenshell.util.element as Element
import re


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
                self.Cellingstorey = []
                marking_points = {}
                self.floor_offset = {}
                self.floor_height = 0
                self.wall_offset = {}
                self.wall_finishes_offset = {}
                floor_finishes_offset = {}
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
                            width, wall_height, depth, self.offsets, wallcoordi = (
                                self.get_wall_dimensions(wall)
                            )
                            dimensions = self.get_wall_dimensions(wall)
                            if width and wall_height:
                                self.wall_dimensions[wall.Name] = {
                                    "width": int(round(width)),
                                    "height": int(round(wall_height)),
                                    "depth": int(round(depth)),
                                    "offset": int(round(self.offsets)),
                                }
                                self.wall_offset[wall.Name] = {
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
                            self.save_wall_mesh_as_stl(wall.Name, mesh)
                        if "Wall Finishes" in wall.Name:
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
                            if verts.size == 0 or faces.size == 0:
                                print(f"[SKIP] {floor.Name}: Empty verts or faces")
                                continue
                            all_floor_points.append(verts)
                            # Update face indices based on the current point offset
                            adjusted_faces = faces + point_offset
                            all_floor_faces.append(adjusted_faces)
                            point_offset += verts.shape[0]
                        if "Floor" in floor.Name:
                            (
                                width,
                                self.floor_height,
                                depth,
                                self.floor_offset,
                                floorcoordi,
                            ) = self.get_wall_dimensions(wall)
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
                    all_floor_points = np.vstack(all_floor_points)
                    all_floor_faces = np.vstack(all_floor_faces)
                    floor_mesh = meshio.Mesh(
                        points=all_floor_points, cells=[("triangle", all_floor_faces)]
                    )
                    meshio.write("floor.stl", floor_mesh)
                    storeys = self.ifc_file.by_type("IfcBuildingStorey")
                    for storey in storeys:
                        object_type = storey.ObjectType
                        if (
                            object_type
                            and "level:bss.level head" in object_type.lower().strip()
                        ):
                            placement = storey.ObjectPlacement
                            if placement and hasattr(placement, "RelativePlacement"):
                                axis_placement = placement.RelativePlacement
                                if axis_placement and hasattr(
                                    axis_placement, "Location"
                                ):
                                    location_point = axis_placement.Location
                                    self.Cellingstorey = list(
                                        location_point.Coordinates
                                    )
                except Exception as e:
                    ifcmaterials.log_error(f"Error while processing IFC shapes: {e}")
                self.label_map = ifcmaterials.shapesformat(wallsformat)
                self.directions = ifcmaterials.calculate_wall_directions(self.label_map)
                self.top_two = ifcmaterials.get_x_y(
                    self.label_map, self.wall_dimensions, wall_height
                )
                self.wall_dimensions = dict(
                    sorted(
                        self.wall_dimensions.items(),
                        key=lambda item: item[1].get("label", "Z"),
                    )
                )
                self.convertStl(stl_data)
                self.wall_finishes_dimensions = self.validate_and_fix_wall_finishes(
                    self.wall_finishes_dimensions
                )
                self.listenerdialog = process.ListenerNodeRunner(
                    self.rosnode, self.stl_file, self.labelstatus, self.stackedWidget
                )
                self.buttonlocalize.clicked.connect(lambda: self.start_scan())
        except Exception as e:
            ifcmaterials.log_error(
                f"Failed to initialize IFC geometry settings or iterator: {str(e)}"
            )
        self.close()

    def validate_and_fix_wall_finishes(self, wall_finishes_dimensions):
        fixed_walls = {}
        expected_heights = self.get_expected_heights(wall_finishes_dimensions)
        for wall_name, dimensions in wall_finishes_dimensions.items():
            for wall_type, expected_height in expected_heights.items():
                if wall_type in wall_name:
                    if (
                        dimensions["height"] != expected_height
                        and dimensions["width"] == expected_height
                    ):
                        dimensions["width"], dimensions["height"] = (
                            dimensions["height"],
                            dimensions["width"],
                        )
                    fixed_walls[wall_name] = dimensions
                    break  # Stop checking further once a match is found
        return fixed_walls

    def get_expected_heights(self, wall_finishes_dimensions):
        expected_heights = {}
        for wall_name in wall_finishes_dimensions.keys():
            match = re.search(r"BSS\.(\d{2})mm Wall Finishes", wall_name)
            if match:
                height_value = int(match.group(1))
                wall_type = f"BSS.{height_value}mm Wall Finishes"
                if wall_type not in expected_heights:
                    expected_heights[wall_type] = height_value
        return expected_heights

    def save_wall_mesh_as_stl(self, wall_name, mesh, scale=1000.0):
        safe_wall_name = wall_name.replace(":", "_").replace(" ", "_")
        self.stlwalls = []
        filename = f"{safe_wall_name}.stl"
        scaled_points = (mesh.points * scale).tolist()
        tri_faces = np.array(mesh.faces).reshape(-1, 4)[:, 1:]
        meshio_mesh = meshio.Mesh(points=scaled_points, cells=[("triangle", tri_faces)])
        self.stlwalls.append(filename)
        meshio.write(f"{safe_wall_name}.stl", meshio_mesh)

    def calculate_wall_directions(self, label_map):
        directions = []
        num_walls = len(label_map)
        for i in range(num_walls):
            curr_label, curr_wall, curr_elevation, curr_axis, name = label_map[i]
            next_label, next_wall, next_elevation, next_axis, name = label_map[
                (i + 1) % num_walls
            ]
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
        if len(self.wall_dimensions) == 6:
            self.loadexcel()
        else:
            self.loadexcel4sides()
        self.stlloader()

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

    # Convert to meshio format and write to STL
    def convertStl(self, data):
        points = np.array(data["points"])
        cells = [("triangle", np.array(data["cells"]))]
        self.stl_file = "output.stl"
        mesh = meshio.Mesh(points=points, cells=cells)
        mesh.cell_data["triangle"] = [np.array(data["material_ids"])]
        meshio.write(self.stl_file, mesh)
        self.meshsplot = pv.read(self.stlwalls[0])
        loadingstl.StLloaderpyvista(self.meshsplot, self.loader)

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
            self.label_map,
            self.directions,
            self.Cellingstorey,
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
            self.wall_offset,
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
            self.wall_dimensions,
            self.top_two,
            self.wall_finishes_dimensions,
            self.label_map,
            self.directions,
        )
