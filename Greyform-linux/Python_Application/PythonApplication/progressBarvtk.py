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
import vtk
from vtk import *
import PythonApplication.interactiveevent as events
from vtkmodules.vtkCommonColor import vtkNamedColors
import numpy as np
from stl import mesh
import gc

gc.collect()


# progress bar to load the vtk frame from the stl
class pythonProgressBar(QDialog):
    def __init__(
        self,
        value,
        polydata,
        ren,
        renderwindowinteractor,
        xlabelbefore,
        ylabelbefore,
        zlabelbefore,
        xlabel,
        ylabel,
        append_filterpolydata,
    ):
        super().__init__()
        progress_layout = QVBoxLayout()
        self.setWindowTitle("Progress Window")
        self.setGeometry(100, 100, 400, 200)
        self.setLayout(progress_layout)
        label = QLabel("Graphics is loading , please wait.")
        label.setGeometry(QtCore.QRect(50, 30, 170, 30))
        self.defaultposition = [0, 0, 1]
        label.setWordWrap(True)
        label.setObjectName("label")
        self.reader = vtk.vtkPolyData()
        self.meshbounds = None
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(30, 130, 340, 30)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.value = value
        self.polydata = polydata
        self.ren = ren
        self.renderwindowinteractor = renderwindowinteractor
        self.xlabelbefore = xlabelbefore
        self.ylabelbefore = ylabelbefore
        self.zlabelbefore = zlabelbefore
        self.xlabels = xlabel
        self.ylabels = ylabel
        self.append_filterpolydata = append_filterpolydata
        self.ren.SetBackground(255, 255, 255)
        QTimer.singleShot(self.value, self.loadStl)

        # Set the layout for the dialog
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgress)
        self.timer.start(100)
        progress_layout.addWidget(label)
        progress_layout.addWidget(self.progress_bar)

    def updateProgress(self):
        # Update loading progress
        current_value = self.progress_bar.value()
        new_value = (current_value + 1) % 101  # Increment progress by 1
        self.progress_bar.setValue(new_value)
        if new_value == 100:
            self.timer.stop()  # Stop the timer when progress reaches 100%
            self.progress_bar.setValue(0)  # Reset progress to 0
            self.timer.start(100)

    def loadStl(self):
        self.updateProgress()
        """Load the given STL file, and return a vtkPolyData object for it."""
        meshs = mesh.Mesh.from_file(self.polydata)
        shape = meshs.points.shape
        points = meshs.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)
        # Create VTK Points
        vtk_points = vtk.vtkPoints()
        for vertex in points:
            vtk_points.InsertNextPoint(vertex)
        # Create VTK CellArray
        vtk_faces = vtk.vtkCellArray()
        for face in faces:
            # Create VTK Polygon (assuming all faces are polygons)
            polygon = vtk.vtkPolygon()
            for vertex_index in face:
                polygon.GetPointIds().InsertNextId(vertex_index)
            vtk_faces.InsertNextCell(polygon)
        self.reader.SetPoints(vtk_points)
        self.reader.SetPolys(vtk_faces)
        actor = self.polyDataToActor()
        center = [
            (self.meshbounds[0] + self.meshbounds[1]) / 2,
            (self.meshbounds[2] + self.meshbounds[3]) / 2,
            (self.meshbounds[4] + self.meshbounds[5]) / 2,
        ]
        self.cubeactor = self.create_cube_actor()
        self.cameraactor = self.create_cube_actor()
        self.cubeactor.SetPosition(80, center[1], center[2])
        self.cubeactor.SetOrientation(
            self.defaultposition[0], self.defaultposition[1], self.defaultposition[2]
        )
        spaceseperation = 50
        self.cameraactor.SetPosition(
            80, center[1] - spaceseperation, center[2] - spaceseperation
        )
        self.cameraactor.SetOrientation(
            self.defaultposition[0], self.defaultposition[1], self.defaultposition[2]
        )
        self.ren.AddActor(actor)
        self.ren.AddActor(self.cameraactor)
        self.ren.AddActor(self.cubeactor)
        self.oldcamerapos = self.cubeactor.GetPosition()
        self.collisionFilter = vtk.vtkCollisionDetectionFilter()
        # Set up the collision filter
        self.collisionFilter.SetInputData(0, self.cubeactor.GetMapper().GetInput())
        self.collisionFilter.SetInputData(1, actor.GetMapper().GetInput())
        self.collisionFilter.SetTransform(
            0, vtk.vtkTransform()
        )  # Moving object transform
        self.collisionFilter.SetTransform(
            1, vtk.vtkTransform()
        )  # Static object transform
        self.collisionFilter.SetMatrix(
            0, self.cubeactor.GetMatrix()
        )  # Static object transform
        self.collisionFilter.SetMatrix(1, actor.GetMatrix())  # Static object transform
        self.collisionFilter.SetCollisionModeToAllContacts()
        self.collisionFilter.GenerateScalarsOn()
        camera = events.myInteractorStyle(
            self.xlabels,
            self.ylabels,
            self.ren,
            self.renderwindowinteractor,
            self.meshbounds,
            self.xlabelbefore,
            self.ylabelbefore,
            self.zlabelbefore,
            actor,
            self.polydata,
            self.reader,
            self.append_filterpolydata,
            self.cubeactor,
            self.cameraactor,
            self.oldcamerapos,
            self.collisionFilter,
            spaceseperation,
            center,
        )
        self.renderwindowinteractor.SetInteractorStyle(camera)
        self.ren.GetActiveCamera().SetPosition(0, -1, 0)
        self.ren.GetActiveCamera().SetFocalPoint(0, 0, 0)
        self.ren.GetActiveCamera().SetViewUp(0, 0, 1)
        self.ren.ResetCameraClippingRange()
        self.ren.ResetCamera()
        self.renderwindowinteractor.GetRenderWindow().Render()
        self.renderwindowinteractor.Initialize()
        self.renderwindowinteractor.Start()
        self.close()

    def create_cube_actor(self):
        self.cube_source = vtk.vtkCubeSource()
        self.cube_source.SetXLength(10)
        self.cube_source.SetYLength(10)
        self.cube_source.SetZLength(10)
        self.cube_mapper = vtk.vtkPolyDataMapper()
        self.cube_mapper.SetInputConnection(self.cube_source.GetOutputPort())
        self.cube_mapper.ScalarVisibilityOff()
        self.cube_actor = vtk.vtkActor()
        self.cube_actor.SetMapper(self.cube_mapper)
        self.cube_actor.GetProperty().BackfaceCullingOn()
        self.cube_actor.GetProperty().FrontfaceCullingOn()
        self.cube_actor.GetProperty().SetOpacity(0.0)
        return self.cube_actor

    def polyDataToActor(self):
        """Wrap the provided vtkPolyData object in a mapper and an actor, returning
        the actor."""
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.reader)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToSurface()
        self.meshbounds = []
        for i in range(6):
            self.meshbounds.append(actor.GetBounds()[i])
        # color RGB must be /255 for Red, green , blue color code
        actor.GetProperty().SetColor((230 / 255), (230 / 255), (250 / 255))
        actor.GetProperty().SetDiffuse(0.8)
        colorsd = vtkNamedColors()
        actor.GetProperty().SetDiffuseColor(colorsd.GetColor3d("LightSteelBlue"))
        actor.GetProperty().SetSpecular(0.3)
        actor.GetProperty().SetSpecularPower(60.0)
        return actor
