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
                all_points = []
                all_cells = []
                all_guids = []
                all_element = []
                all_materials = []
                all_material_ids = []
                scale_factor = 100.0
                try:
                    while True:
                        shape = iterator.get()
                        guid = shape.guid
                        element = self.ifc_file.by_guid(shape.guid)
                        element_type = element.is_a() if element else "Unknown"
                        # Skip IfcOpeningElement
                        if element_type == "IfcOpeningElement":
                            if not iterator.next():
                                break
                            continue
                        element_name = (
                            element.Name
                            if element and hasattr(element, "Name")
                            else "Unnamed"
                        )
                        # Indices of vertices per triangle face
                        faces = shape.geometry.faces
                        # X Y Z of vertices in flattened list
                        verts = shape.geometry.verts
                        # Material names and colour style information that are relevant to this shape
                        materials = shape.geometry.materials
                        # Indices of material applied per triangle face e.g. [f1m, f2m, ...]
                        material_ids = shape.geometry.material_ids
                        if len(faces) == 0 or len(verts) == 0:
                            print(f"No geometry for shape {guid}")
                            continue
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
                        scaled_grouped_verts = self.scale_vertices(
                            grouped_verts, scale_factor
                        )
                        # Flatten the grouped_verts and add indices to all_points
                        vert_index_offset = len(all_points)
                        all_points.extend(scaled_grouped_verts)
                        all_cells.extend(
                            [
                                [
                                    face[0] + vert_index_offset,
                                    face[1] + vert_index_offset,
                                    face[2] + vert_index_offset,
                                ]
                                for face in grouped_faces
                            ]
                        )
                        all_element.extend(
                            [(element_type, element_name)] * len(grouped_faces)
                        )
                        all_guids.extend([guid] * len(grouped_faces))
                        if material_ids:
                            all_material_ids.extend(material_ids)
                        if materials:
                            all_materials.extend(materials)
                        if not iterator.next():
                            break
                except Exception as e:
                    self.log_error(f"Error while processing IFC shapes: {e}")
                self.convertStl(all_points, all_cells, all_material_ids)
                self.convertExcel(
                    all_points, all_cells, all_element, all_guids, all_materials
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

    def log_error(self, message):
        with open("error_log.txt", "a") as log_file:
            log_file.write(message + "\n")

    # Convert to meshio format and write to STL
    def convertStl(self, all_points, all_cells, all_material_ids):
        try:
            points = all_points
            cells = [("triangle", all_cells)]
            # Create material ID array for each face
            cell_data = {"triangle": [all_material_ids]}
            self.stl_file = "output.stl"
            meshio.write_points_cells(
                self.stl_file,
                points=points,
                cells=cells,
                cell_data=cell_data,
            )
        except Exception as e:
            self.log_error(f"Failed to write STL file: {e}")

    def convertExcel(
        self, all_points, all_cells, all_element, all_guids, all_materials
    ):
        try:
            points_df = pd.DataFrame(all_points, columns=["X", "Y", "Z"])
            cells_df = pd.DataFrame(
                all_cells, columns=["Vertex1", "Vertex2", "Vertex3"]
            )
            guids_df = pd.DataFrame(all_guids, columns=["GUID"])
            elements_df = pd.DataFrame(
                all_element, columns=["Element Type", "Element Name"]
            )
            materials_df = pd.DataFrame(all_materials, columns=["Material"])
            # Save to Excel
            with pd.ExcelWriter("output.xlsx") as writer:
                points_df.to_excel(writer, sheet_name="Vertices", index=False)
                cells_df.to_excel(writer, sheet_name="Faces", index=False)
                guids_df.to_excel(writer, sheet_name="GUIDs", index=False)
                elements_df.to_excel(writer, sheet_name="Elements", index=False)
                materials_df.to_excel(writer, sheet_name="Materials", index=False)
        except Exception as e:
            self.log_error(f"Failed to write Excel file: {e}")

    def scale_vertices(self, vertices, scale_factor):
        return np.array(vertices) * scale_factor

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
        )
        self.close()
