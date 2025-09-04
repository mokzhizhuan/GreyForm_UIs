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
import PythonApplication.actors as createactorvtk
import PythonApplication.robotplacementrobot as robotplacemats


# create the imported stl mesh in vtk frame
class createMesh(QMainWindow):
    def __init__(
        self,
        ren,
        polydata,
        renderwindowinteractor,
        file_path,
        mainwindow,
        Stagelabel,
        walllabel,
        stacked_widget,
        count_plus_y,
        count_minus_y,
        excel_file,
        wallformat,
        axis_widths,
        listenerdialog 
    ):
        # starting initialize
        super().__init__()
        self.defaultposition = [0, 0, 1]
        self.reader = vtk.vtkPolyData()
        self.ren = ren
        self.excel_file = excel_file
        self.meshbounds = None
        self.polydata = polydata
        self.dialog = None
        self.renderwindowinteractor = renderwindowinteractor
        self.renderwindowinteractor.GetRenderWindow().AddRenderer(self.ren)
        self.filepath = file_path
        self.walllabel = walllabel
        self.count_plus_y = count_plus_y
        self.count_minus_y = count_minus_y
        self.stacked_widget = stacked_widget
        self.wallformat = wallformat
        self.axis_widths = {"x": [], "y": []}
        self.ren.SetBackground(1, 1, 1)
        self.renderwindowinteractor.GetRenderWindow().SetMultiSamples(0)
        self.ren.UseHiddenLineRemovalOn()
        self.mainwindow = mainwindow
        self.axis_widths = axis_widths
        self.currentindexstage = 0
        self.listenerdialog = listenerdialog
        self.Stagelabel = Stagelabel
        (
            self.wall_identifiers,
            self.wall,
            self.stagewallnum,
            self.stagestorage,
        ) = vtk_data_excel.exceldataextractor(self.excel_file)

        self.stagetext = self.stagestorage[self.currentindexstage]
        Stagelabel.setText(f"Stage : {self.stagetext}")
        self.loadStl()

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
        self.robotplacement = robotplacemats.robotplacement(self.meshbounds)
        self.objectrobot = [500,500,500]
        self.wall7 = [self.meshbounds[1], self.meshbounds[3]]
        self.walls = {}
        self.walls, self.cameraactors = createactorvtk.initialize_walls(
            self.wallformat, self.axis_widths, self.walls
        )
        self.wall_actors, self.identifier, self.wallname = (
            createactorvtk.setupactors(
                self.walls,
                self.stagetext,
                self.wall_identifiers,
                self.ren,
                self.walllabel,
                self.robotplacement,
                self.objectrobot,
            )
        )
        self.setupvtkframe()

    # setup vtk frame ui
    def setupvtkframe(self):
        setcamerainteraction = [
            self.ren,
            self.renderwindowinteractor,
            self.meshbounds,
            self.filepath,
            self.excel_file,
            self.dialog,
            self.stagetext,
            self.wall7,
            self.wall_identifiers,
            self.stagestorage,
            self.currentindexstage,
            self.Stagelabel,
            self.walls,
            self.wall_actors,
            self.wallname,
            self.identifier,
            self.stacked_widget,
            self.walllabel,
            self.listenerdialog,
            self.robotplacement,
            self.objectrobot,
        ]
        camera = events.myInteractorStyle(setcamerainteraction)
        self.renderwindowinteractor.SetInteractorStyle(camera)
        cameramain = vtk.vtkCamera()
        x_center = (self.meshbounds[0] + self.meshbounds[1]) / 2
        y_center = (self.meshbounds[2] + self.meshbounds[3]) / 2
        z_center = (self.meshbounds[4] + self.meshbounds[5]) / 2
        cameramain.SetPosition(x_center, y_center, z_center + 50)  # top-down view
        cameramain.SetFocalPoint(x_center, y_center, z_center)
        cameramain.SetViewUp(0, 1, 0)
        cameramain.ParallelProjectionOn()
        cameramain.SetParallelScale((self.meshbounds[3] - self.meshbounds[2]))
        self.ren.SetActiveCamera(cameramain)
        self.ren.ResetCameraClippingRange()
        self.renderwindowinteractor.GetRenderWindow().Render()
        self.renderwindowinteractor.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
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
