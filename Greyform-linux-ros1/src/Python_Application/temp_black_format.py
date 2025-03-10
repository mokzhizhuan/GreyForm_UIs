from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import vtk
from vtk import *
from vtkmodules.vtkCommonColor import vtkNamedColors
import numpy as np
from stl import mesh
import PythonApplication.interactiveevent as events
import PythonApplication.exceldatavtk as vtk_data_excel
import re
import PythonApplication.actors as createactorvtk


# create the imported stl mesh in vtk frame
class createMesh(QMainWindow):
    def __init__(
        self,
        ren,
        polydata,
        renderwindowinteractor,
        ros_node,
        file_path,
        mainwindow,
        Stagelabel,
        walllabel,
        stacked_widget
    ):
        # starting initialize
        super().__init__()
        self.defaultposition = [0, 0, 1]
        self.reader = vtk.vtkPolyData()
        self.meshbounds = None
        self.polydata = polydata
        self.ren = ren
        self.dialog = None
        self.renderwindowinteractor = renderwindowinteractor
        self.renderwindowinteractor.GetRenderWindow().AddRenderer(self.ren)
        self.ros_node = ros_node
        self.filepath = file_path
        self.walllabel = walllabel
        self.stacked_widget = stacked_widget
        self.ren.SetBackground(1, 1, 1)
        self.renderwindowinteractor.GetRenderWindow().SetMultiSamples(0)
        self.ren.UseHiddenLineRemovalOn()
        self.mainwindow = mainwindow
        self.currentindexstage = 0
        self.Stagelabel = Stagelabel
        self.wall_identifiers, self.wall, self.excelfiletext , self.stagewallnum , self.stagestorage = (
            vtk_data_excel.exceldataextractor()
        )
        self.stagetext = self.stagestorage[self.currentindexstage]
        Stagelabel.setText(f"Stage : {self.stagetext}")
        self.wallaxis = vtk_data_excel.wall_format(self.wall)
        self.loadStl()

    def show_cancelation_dialog(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Cancellation")
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    # load stl in vtk frame
    def loadStl(self):
        meshs = mesh.Mesh.from_file(self.polydata)
        points = meshs.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)
        vtk_points = vtk.vtkPoints()
        for vertex in points:
            vtk_points.InsertNextPoint(vertex)
        vtk_faces = vtk.vtkCellArray()
        for face in faces:
            polygon = vtk.vtkPolygon()
            for vertex_index in face:
                polygon.GetPointIds().InsertNextId(vertex_index)
            vtk_faces.InsertNextCell(polygon)
        self.reader.SetPoints(vtk_points)
        self.reader.SetPolys(vtk_faces)
        self.polyDataToActor()
        self.fixedposition()
        self.center = [
            (self.meshbounds[0] + self.meshbounds[1]) / 2,
            (self.meshbounds[2] + self.meshbounds[3]) / 2,
            (self.meshbounds[4] + self.meshbounds[5]) / 2,
        ]
        self.wall7 = [self.meshbounds[1], self.meshbounds[3]]
        self.addranges()
        self.walls = {
            "Wall 1": {
                "position": ((self.meshbounds[0] + self.meshbounds[1]), -100, 0),
                "size": (self.wallaxis[1]["height"], self.wallaxis[1]["width"]),
                "color": (0, 1, 1),
                "rotation": (90, 0, 90),
            },  # Cyan
            "Wall 2": {
                "position": (self.meshbounds[0] - 100, 0, 0),
                "size": (
                    (self.meshbounds[2] + self.meshbounds[3]),
                    self.wallaxis[1]["height"],
                ),
                "color": (1, 0, 0),
                "rotation": (0, 90, 90),
            },  # Red
            "Wall 3": {
                "position": (
                    self.wallaxis[3]["width"],
                    (self.meshbounds[2] + self.meshbounds[3]) + 100,
                    0,
                ),
                "size": (
                    self.wallaxis[1]["height"],
                    self.wallaxis[3]["width"],
                ),
                "color": (1, 0, 1),
                "rotation": (90, 0, 90),
            },  # Magenta
            "Wall 4": {
                "position": (
                    (self.meshbounds[0] + self.meshbounds[1]),
                    (self.meshbounds[2] + self.meshbounds[3]) - 300,
                    0,
                ),
                "size": (
                    self.wallaxis[1]["height"],
                    self.wallaxis[5]["width"],
                ),
                "color": (0.5, 0.5, 0),
                "rotation": (90, 0, 90),
            },  # Brown
            "Wall 5": {
                "position": (
                    self.wallaxis[3]["width"] + 100,
                    self.wallaxis[3]["width"] - 200,
                    0,
                ),
                "size": (self.wallaxis[4]["width"], self.wallaxis[1]["height"]),
                "color": (0, 0.5, 0.5),
                "rotation": (0, 90, 90),
            },  # Teal
            "Wall 6": {
                "position": (self.meshbounds[0] + self.meshbounds[1] + 100, 0, 0),
                "size": ((self.wallaxis[6]["width"], self.wallaxis[1]["height"])),
                "color": (0, 1, 0),
                "rotation": (0, 90, 90),
            },  # Green
            "Floor": {
                "position": (0, 0, -100),
                "points": (
                    (0, 0, -100),
                    (0, (self.meshbounds[2] + self.meshbounds[3]), -100),
                    (
                        (self.meshbounds[2] + self.meshbounds[3]),
                        (self.meshbounds[2] + self.meshbounds[3]),
                        -100,
                    ),
                    (
                        (self.meshbounds[2] + self.meshbounds[3]),
                        self.wallaxis[6]["width"],
                        -100,
                    ),
                    (
                        (self.meshbounds[0] + self.meshbounds[1]),
                        self.wallaxis[6]["width"],
                        -100,
                    ),
                    ((self.meshbounds[0] + self.meshbounds[1]), 0, -100),
                ),
                "color": (1, 1, 0),
                "rotation": (0, 0, 0),
            },  # Yellow
        }
        self.createactors, self.identifier, self.wall_actors, self.wallname = createactorvtk.setupactors(self.walls, self.stagetext, self.wall_identifiers, self.ren, self.walllabel)
        self.setupvtkframe()

    # setup vtk frame ui
    def setupvtkframe(self):
        setcamerainteraction = [
            self.ren,
            self.renderwindowinteractor,
            self.meshbounds,
            self.filepath,
            self.excelfiletext,
            self.dialog,
            self.stagetext,
            self.wall7,
            self.wallaxis,
            self.wall_identifiers,
            self.stagestorage,
            self.currentindexstage,
            self.Stagelabel,
            self.walls,
            self.wall_actors,
            self.wallname,
            self.identifier,
            self.stacked_widget
        ]
        camera = events.myInteractorStyle(
            setcamerainteraction,
            self.wall_identifiers,
        )
        self.renderwindowinteractor.SetInteractorStyle(camera)
        self.ren.GetActiveCamera().SetPosition(0, -1, 0)
        self.ren.GetActiveCamera().SetFocalPoint(0, 0, 0)
        self.ren.GetActiveCamera().SetViewUp(0, 0, 1)
        self.ren.ResetCameraClippingRange()
        self.ren.ResetCamera()
        self.renderwindowinteractor.GetRenderWindow().Render()
        self.renderwindowinteractor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        renderWindow = self.renderwindowinteractor.GetRenderWindow()
        renderWindow.AddRenderer(self.ren)
        self.renderwindowinteractor.Initialize()
        self.renderwindowinteractor.Start()

    # fixed x y and z pos
    def fixedposition(self):
        minBounds = [self.meshbounds[0], self.meshbounds[2], self.meshbounds[4]]
        transform = vtk.vtkTransform()
        transform.Translate(-minBounds[0], -minBounds[1], -minBounds[2])
        transformFilter = vtkTransformPolyDataFilter()
        transformFilter.SetInputData(self.reader)
        transformFilter.SetTransform(transform)
        transformFilter.Update()
        transformedPolyData = transformFilter.GetOutput()
        self.setnormals(transformedPolyData)

    # set the mesh to the 0,0,0 starting pos
    def setnormals(self, transformedPolyData):
        normals = vtkPolyDataNormals()
        normals.SetInputData(transformedPolyData)
        normals.ComputePointNormalsOn()
        normals.ComputeCellNormalsOff()
        normals.Update()
        mesh_with_normals = normals.GetOutput()
        mapper = vtkPolyDataMapper()
        mapper.SetInputData(mesh_with_normals)
        self.setactor(mapper)

    # setup main actor
    def setactor(self, mapper):
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)
        self.actor.GetProperty().SetRepresentationToSurface()
        colorsd = vtkNamedColors()
        self.actor.GetProperty().SetColor((230 / 255), (230 / 255), (250 / 255))
        self.actor.GetProperty().SetColor((230 / 255), (230 / 255), (250 / 255))
        self.actor.GetProperty().SetDiffuseColor(colorsd.GetColor3d("LightSteelBlue"))
        self.actor.GetProperty().SetDiffuse(0.8)
        self.actor.GetProperty().SetSpecular(0.3)
        self.actor.GetProperty().SetSpecularPower(60.0)
        self.actor.GetProperty().BackfaceCullingOn()
        self.actor.GetProperty().FrontfaceCullingOn()
        for i in range(6):
            self.meshbounds[i] = int(self.actor.GetBounds()[i])

    # clear actor
    def clearactor(self):
        actors = self.ren.GetActors()
        actors.InitTraversal()
        actor = actors.GetNextActor()
        while actor:
            self.ren.RemoveActor(actor)
            actor = actors.GetNextActor()

    # set actor in the vtk mapper
    def polyDataToActor(self):
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.reader)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToSurface()
        self.meshbounds = []
        for i in range(6):
            self.meshbounds.append(actor.GetBounds()[i])

    def addranges(self):
        current_y = 0
        current_x = 0
        max_y = self.wall7[1]  # Maximum Y position based on the image
        max_x = self.wall7[0]  # Maximum X position based on the image
        for wall_id, wall in self.wallaxis.items():
            if "pos_y_range" not in wall or wall["pos_y_range"] is None:
                wall["pos_y_range"] = (0, 0)
            if "pos_x_range" not in wall or wall["pos_x_range"] is None:
                wall["pos_x_range"] = (0, 0)
            if wall["axis"] == "y":  # Wall along the Y-axis
                # Y-axis walls increase current_y
                if wall_id == 2:  # Specific for Wall 1
                    wall["pos_x_range"] = (0, 50)
                    wall["pos_y_range"] = (0, self.wall7[0])
                elif wall_id == 4:  # Specific for wall 3
                    wall["pos_x_range"] = (self.wall7[1] - 50, self.wall7[1])
                    wall["pos_y_range"] = (
                        self.wall7[1] - self.wallaxis[4]["width"],
                        self.wall7[1],
                    )
                elif wall_id == 6:  # Specific for wall 5
                    wall["pos_x_range"] = (self.wall7[0] - 100, max_x)
                    wall["pos_y_range"] = (0, max_y)
                else:
                    wall["pos_x_range"] = (0, max_x)
                    wall["pos_y_range"] = (current_y, current_y + self.wall7[0])
            elif wall["axis"] == "x":  # Wall along the X-axis
                # X-axis walls increase current_x
                if wall_id == 3:  # Specific for Wall 2
                    wall["pos_x_range"] = (0, wall["width"])
                    wall["pos_y_range"] = (
                        max_y - self.wallaxis[4]["width"] + 50,
                        max_y,
                    )
                elif wall_id == 5:  # Specific for Wall 4
                    wall["pos_x_range"] = (self.wall7[1], max_x)
                    wall["pos_y_range"] = (max_y - 50, max_y)
                elif wall_id == 1:  # Wall 6
                    wall["pos_x_range"] = (0, max_x)  # Corrected range
                    wall["pos_y_range"] = (0, 50)
                else:
                    wall["pos_x_range"] = (current_x, current_x + max_x)
                    wall["pos_y_range"] = (0, max_y)
            wall["pos_x_range"] = (
                max(0, wall["pos_x_range"][0]),
                min(max_x, wall["pos_x_range"][1]),
            )
            wall["pos_y_range"] = (
                max(0, wall["pos_y_range"][0]),
                min(max_y, wall["pos_y_range"][1]),
            )
