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
from stl import mesh
import PythonApplication.loadpyvista as loadingstl
import meshio
import PythonApplication.createmesh as Createmesh
import PythonApplication.processlistenerrunner as process
import PythonApplication.processloader as Thread
from stl import mesh
import pyvista as pv
import numpy as np


class dxfloader(object):
    def __init__(
        self, file_path, mainwindowforfileselection, gdf, mainwindow, stackedWidget
    ):
        # starting initialize
        super().__init__()
        self.file_path = file_path
        self.mainwindowforfileselection = mainwindowforfileselection
        self.mainwindow = mainwindow
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
        self.markingitemsbasedonwallnumber = {}
        self.stackedWidget = stackedWidget
        self.gdf = gdf
        self.stagewallindex = 1
        self.Stagelabel.setText(f"Stage : {self.stagestoring[0]}")
        self.exceldata = "exporteddatassss(with TMP)(draft).xlsx"
        self.listenerdialog = process.ListenerNodeRunner(
            self.rosnode, self.file_path, self.labelstatus, self.stackedWidget
        )
        self.loaddxftoframe()

    def loaddxftoframe(self):
        self.all_vertices = []
        self.all_faces = []
        offset = 0
        for idx, row in self.gdf.iterrows():
            geometry = row["geometry"]
            offset = self.process_geometry(geometry, offset)
        if self.all_vertices:
            all_vertices = np.vstack(self.all_vertices)
            all_faces = np.hstack(self.all_faces)
            self.meshsplot = pv.PolyData(all_vertices, all_faces)
            self.output_stl_path = "output.stl"
            if not self.meshsplot.is_all_triangles:
                self.meshsplot = self.meshsplot.triangulate()
                self.meshsplot.save(self.output_stl_path)
                meshs = meshio.read(self.output_stl_path)
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
                loadingstl.StLloaderpyvista(self.meshsplot, self.loader)
                self.buttonlocalize.clicked.connect(lambda: self.start_scan())

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
        Createmesh.createMesh(
            self.renderer,
            self.output_stl_path,
            self.renderWindowInteractor,
            self.rosnode,
            self.file_path,
            self.mainwindow,
            self.Stagelabel,
            self.walllabel,
            self.stackedWidget,
            self.listenerdialog,
        )
        self.renderWindowInteractor.GetRenderWindow().Render()  # Force UI update

    # process geometry in geodata pandas
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

    # resize
    def resize_stl(self, file_path, scale_factor, output_path):
        Mesh = mesh.Mesh.from_file(file_path)
        Mesh.vectors *= scale_factor
        Mesh.update_normals()
        Mesh.save(output_path)
