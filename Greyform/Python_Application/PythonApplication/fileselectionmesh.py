from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal
from pyvistaqt import QtInteractor
import PythonApplication.progressBar as Progress
import ifcopenshell
import ifcopenshell.geom
import PythonApplication.IFCpythondialog as ProgressIFCFile
import PythonApplication.loadpyvista as loadingstl
import xml.etree.ElementTree as ET
import numpy as np
import meshio
import pyvista as pv


# load pyvista in the frame
class FileSelectionMesh(QMainWindow):
    def __init__(
        self,
        file_path,
        plotterloader,
        plotterloader_2,
        pyvistaframe,
        pyvistaframe_2,
        layoutWidget,
        layoutWidget_page2,
        renderer,
        renderWindowInteractor,
        Ylabel,
        Xlabel,
        Xlabel_before,
        Ylabel_before,
        Zlabel_before,
        seq1Button,
        seq2Button,
        seq3Button,
        NextButton_Page_3,
        Seqlabel,
    ):
        self.plotterloader = plotterloader
        self.plotterloader_2 = plotterloader_2
        self.pyvistaframe = pyvistaframe
        self.pyvistaframe_2 = pyvistaframe_2
        self.layoutwidget = layoutWidget
        self.layoutwidget_page2 = layoutWidget_page2
        self.file_path = file_path
        self.renderer = renderer
        self.renderWindowInteractor = renderWindowInteractor
        self.Ylabel = Ylabel
        self.Xlabel = Xlabel
        self.Xlabel_before = Xlabel_before
        self.Ylabel_before = Ylabel_before
        self.Zlabel_before = Zlabel_before
        self.seq1Button = seq1Button
        self.seq2Button = seq2Button
        self.seq3Button = seq3Button
        self.NextButton_Page_3 = NextButton_Page_3
        self.Seqlabel = Seqlabel
        self.meshdata()

    # load meshdata from file
    def meshdata(self):
        if ".stl" in self.file_path:
            progressbarprogram = Progress.pythonProgressBar(
                100000,
                self.plotterloader,
                self.plotterloader_2,
                self.file_path,
                self.renderer,
                self.renderWindowInteractor,
                self.Xlabel,
                self.Ylabel,
                self.Xlabel_before,
                self.Ylabel_before,
                self.Zlabel_before,
                self.seq1Button,
                self.seq2Button,
                self.seq3Button,
                self.NextButton_Page_3,
                self.Seqlabel,
            )
            progressbarprogram.exec_()
        elif ".ifc" in self.file_path:
            try:
                ifc_file = ifcopenshell.open(self.file_path)
            except Exception as e:
                self.log_error(f"Failed to open IFC file: {e}")
            else:
                progressbarprogram = ProgressIFCFile.ProgressBarDialogIFC(
                    80000,
                    ifc_file,
                    self.plotterloader,
                    self.plotterloader_2,
                    self.renderer,
                    self.renderWindowInteractor,
                    self.Xlabel,
                    self.Ylabel,
                    self.Xlabel_before,
                    self.Ylabel_before,
                    self.Zlabel_before,
                    self.seq1Button,
                    self.seq2Button,
                    self.seq3Button,
                    self.NextButton_Page_3,
                    self.Seqlabel,
                )
                progressbarprogram.exec_()
        elif ".xml" in self.file_path:
            tree = ET.parse(self.file_path)
            root = tree.getroot()
            # Extract the point and face data
            points = []
            faces = []

            # Namespace dictionary for XML parsing
            ns = {"gbXML": "http://www.gbxml.org/schema"}

            for shell in root.findall(".//gbXML:ClosedShell", ns):
                for polyloop in shell.findall("gbXML:PolyLoop", ns):
                    poly_points = []
                    for point in polyloop.findall("gbXML:CartesianPoint", ns):
                        coords = [
                            float(coord.text)
                            for coord in point.findall("gbXML:Coordinate", ns)
                        ]
                        if coords not in points:
                            points.append(coords)
                        poly_points.append(points.index(coords))
                    # Create triangular faces from the polyloop points
                    for i in range(1, len(poly_points) - 1):
                        faces.append(
                            [poly_points[0], poly_points[i], poly_points[i + 1]]
                        )
            points = np.array(points)
            faces = np.array(faces)
            mesh = meshio.Mesh(points, [("triangle", faces)])
            meshio.write("output.stl", mesh)
            self.meshsplot = pv.read("output.stl")
            loadingstl.StLloaderpyvista(
                self.meshsplot, self.plotterloader, self.plotterloader_2
            )

    def log_error(self, message):
        with open("error_log.txt", "a") as log_file:
            log_file.write(message + "\n")
