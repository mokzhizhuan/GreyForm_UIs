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
        label.setWordWrap(True)
        label.setObjectName("label")

        # variable for loading bar ui
        self.defaultposition = [0, 0, 1]
        self.reader = vtk.vtkSTLReader()
        self.meshbounds = None
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(30, 130, 340, 30)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.value = value
        self.polydata = polydata
        self.ren = ren
        self.renderwindowinteractor = renderwindowinteractor
        self.renderwindowinteractor.GetRenderWindow().AddRenderer(self.ren)
        self.xlabelbefore = xlabelbefore
        self.ylabelbefore = ylabelbefore
        self.zlabelbefore = zlabelbefore
        self.xlabels = xlabel
        self.ylabels = ylabel
        self.append_filterpolydata = append_filterpolydata
        self.ren.SetBackground(1, 1, 1)
        self.start_progress()
        # timer layout for the dialog
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgress)
        self.timer.start(100)
        progress_layout.addWidget(label)
        progress_layout.addWidget(self.progress_bar)

    def start_progress(self):
        QTimer.singleShot(self.value, self.loadStl)

    def updateProgress(self):
        # Update loading progress
        current_value = self.progress_bar.value()
        new_value = (current_value + 1) % 101  # Increment progress by 1
        self.progress_bar.setValue(new_value)
        if new_value == 100:
            self.timer.stop()  # Stop the timer when progress reaches 100%
            self.progress_bar.setValue(0)  # Reset progress to 0
            self.timer.start(100)

    # load STL in vtk frame
    def loadStl(self):
        self.updateProgress()
        """Load the given STL file, and return a vtkPolyData object for it."""
        self.reader.SetFileName(self.polydata)
        self.reader.Update()
        polydata = self.reader.GetOutput()
        actor = self.polyDataToActor(polydata)
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
        self.cameraactor.SetPosition(80, center[1], center[2])
        self.cameraactor.SetOrientation(
            self.defaultposition[0], self.defaultposition[1], self.defaultposition[2]
        )
        self.ren.AddActor(self.cameraactor)
        self.ren.AddActor(self.cubeactor)
        self.ren.AddActor(actor)
        self.oldcamerapos = self.cubeactor.GetPosition()
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
            polydata,
            self.reader,
            self.append_filterpolydata,
            self.cubeactor,
            self.cameraactor,
            self.oldcamerapos,
        )
        self.renderwindowinteractor.SetInteractorStyle(camera)
        self.ren.GetActiveCamera().SetPosition(0, -1, 0)
        self.ren.GetActiveCamera().SetFocalPoint(0, 0, 0)
        self.ren.GetActiveCamera().SetViewUp(0, 0, 1)
        self.ren.ResetCameraClippingRange()
        self.ren.ResetCamera()
        self.renderwindowinteractor.GetRenderWindow().Render()
        self.renderwindowinteractor.GetRenderWindow().Finalize()
        self.renderwindowinteractor.GetRenderWindow().SetSize(1600, 800)
        self.renderwindowinteractor.GetRenderWindow().Render()
        self.renderwindowinteractor.Initialize()
        self.renderwindowinteractor.Start()
        self.close()

    def create_cube_actor(self):
        self.cube_source = vtk.vtkCubeSource()
        self.cube_mapper = vtk.vtkPolyDataMapper()
        self.cube_mapper.SetInputConnection(self.cube_source.GetOutputPort())
        self.cube_mapper.ScalarVisibilityOff()
        self.cube_actor = vtk.vtkActor()
        self.cube_actor.SetMapper(self.cube_mapper)
        self.cube_actor.GetProperty().BackfaceCullingOn()
        self.cube_actor.GetProperty().FrontfaceCullingOn()
        self.cube_actor.GetProperty().SetOpacity(0.0)
        return self.cube_actor

    # set mesh as actor in vtk frame
    def polyDataToActor(self, polydata):
        """Wrap the provided vtkPolyData object in a mapper and an actor, returning
        the actor."""
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.reader.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToSurface()
        self.meshbounds = []
        for i in range(6):
            self.meshbounds.append(actor.GetBounds()[i])
        # color RGB must be /255 for Red, Green , blue color code
        actor.GetProperty().SetColor((230 / 255), (230 / 255), (250 / 255))
        actor.GetProperty().SetDiffuse(0.8)
        actor.SetPosition(0, 0, 0)
        colorsd = vtkNamedColors()
        actor.GetProperty().SetDiffuseColor(colorsd.GetColor3d("LightSteelBlue"))
        actor.GetProperty().SetSpecular(0.3)
        actor.GetProperty().SetSpecularPower(60.0)
        actor.GetProperty().BackfaceCullingOn()
        actor.GetProperty().FrontfaceCullingOn()
        actor.SetOrientation(1, 0, 0)
        self.append_filterpolydata.AddInputData(actor.GetMapper().GetInput())
        self.append_filterpolydata.Update()
        return actor
