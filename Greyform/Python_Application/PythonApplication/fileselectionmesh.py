from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import PythonApplication.progressBar as Progress
import ifcopenshell
import ifcopenshell.geom
import PythonApplication.IFCpythondialog as ProgressIFCFile
import PythonApplication.loadpyvista as loadingstl
import numpy as np
import pyvista as pv
import geopandas as gpd
from shapely.geometry import (
    LineString,
    Polygon,
    MultiPolygon,
    MultiLineString,
    Point,
    MultiPoint,
    LinearRing,
    GeometryCollection,
)
import PythonApplication.createmesh as Createmesh
from stl import mesh
import meshio


# load pyvista in the frame
class FileSelectionMesh(QMainWindow):
    def __init__(self, file_path, mainwindowforfileselection):
        self.file_path = file_path
        self.mainwindowforfileselection = mainwindowforfileselection
        self.mainwindowforfileselection = mainwindowforfileselection
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
        self.meshdata()

    # load meshdata from file
    def meshdata(self):
        if ".stl" in self.file_path:
            progressbarprogram = Progress.pythonProgressBar(
                80000, self.file_path, self.mainwindowforfileselection
            )
            progressbarprogram.exec_()
        elif ".ifc" in self.file_path:
            try:
                ifc_file = ifcopenshell.open(self.file_path)
            except Exception as e:
                self.log_error(f"Failed to open IFC file: {e}")
            else:
                progressbarprogram = ProgressIFCFile.ProgressBarDialogIFC(
                    30000, ifc_file, self.mainwindowforfileselection
                )
                progressbarprogram.exec_()
        elif ".dxf" in self.file_path:
            gdf = gpd.read_file(self.file_path, engine="fiona")
            self.all_vertices = []
            self.all_faces = []
            offset = 0
            for idx, row in gdf.iterrows():
                geometry = row["geometry"]
                offset = self.process_geometry(geometry, offset)
            if self.all_vertices:
                all_vertices = np.vstack(self.all_vertices)
                all_faces = np.hstack(self.all_faces)
                self.meshsplot = pv.PolyData(all_vertices, all_faces)
                output_stl_path = "output.stl"
                if not self.meshsplot.is_all_triangles:
                    self.meshsplot = self.meshsplot.triangulate()
                self.meshsplot.save(output_stl_path)
                scale_factor = 1.5
                self.resize_stl(output_stl_path, scale_factor, output_stl_path)
                meshs = meshio.read(output_stl_path)
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
                            (
                                np.full((len(cell_data), 1), num_points_per_cell),
                                cell_data,
                            )
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
                    output_stl_path,
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
                    self.localizebutton,
                    self.file_path,
                )

    #process geomtry for dxf meshdata
    def process_line_string(self, geometry, offset):
        points = np.array(geometry.coords)
        lines = np.hstack([[len(points)], np.arange(len(points)) + offset])
        return points, lines, offset + len(points)

    def process_polygon(self, geometry, offset):
        poly_points = np.array(geometry.exterior.coords)
        face = np.hstack([[len(poly_points)], np.arange(len(poly_points)) + offset])
        return poly_points, face, offset + len(poly_points)

    def process_geometry(self, geometry, offset):
        if isinstance(geometry, LineString):
            points, lines, offset = self.process_line_string(geometry, offset)
            self.all_vertices.append(points)
            self.all_faces.append(lines)
        elif isinstance(geometry, Polygon):
            poly_points, face, offset = self.process_polygon(geometry, offset)
            self.all_vertices.append(poly_points)
            self.all_faces.append(face)
        elif isinstance(geometry, MultiPolygon) or isinstance(
            geometry, MultiLineString
        ):
            for geom in geometry.geoms:
                offset = self.process_geometry(geom, offset)
        elif isinstance(geometry, GeometryCollection):
            for geom in geometry.geoms:
                offset = self.process_geometry(geom, offset)
        elif isinstance(geometry, Point):
            point_coords = np.array(geometry.coords)
            self.all_vertices.append(point_coords)
            offset += len(point_coords)
        elif isinstance(geometry, MultiPoint):
            for point in geometry.geoms:
                point_coords = np.array(point.coords)
                self.all_vertices.append(point_coords)
                offset += len(point_coords)
        elif isinstance(geometry, LinearRing):
            ring_points = np.array(geometry.coords)
            self.all_vertices.append(ring_points)
            offset += len(ring_points)
        else:
            print(f"Unknown geometry type: {type(geometry)}")
        return offset

    #resize stl
    def resize_stl(self, file_path, scale_factor, output_path):
        Mesh = mesh.Mesh.from_file(file_path)
        Mesh.vectors *= scale_factor
        Mesh.update_normals()
        Mesh.save(output_path)

    #error message implement for converting to text file
    def log_error(self, message):
        with open("error_log.txt", "a") as log_file:
            log_file.write(message + "\n")
