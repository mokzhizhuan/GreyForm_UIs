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
        self.xlabelbefore = xlabelbefore
        self.ylabelbefore = ylabelbefore
        self.zlabelbefore = zlabelbefore
        self.xlabels = xlabel
        self.ylabels = ylabel
        self.append_filterpolydata = append_filterpolydata
        self.ren.SetBackground(255, 255, 255)
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
        actor, boundarypolydata = self.polyDataToActor(polydata)
        self.ren.AddActor(actor)
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
        )
        self.renderwindowinteractor.SetInteractorStyle(camera)
        self.ren.GetActiveCamera().SetPosition(0, -1, 0)
        self.ren.GetActiveCamera().SetFocalPoint(0, 0, 0)
        self.ren.GetActiveCamera().SetViewUp(0, 0, 1)
        self.ren.ResetCamera()
        self.renderwindowinteractor.GetRenderWindow().AddRenderer(self.ren)
        self.renderwindowinteractor.GetRenderWindow().Render()
        self.renderwindowinteractor.Initialize()
        self.renderwindowinteractor.Start()
        self.renderwindowinteractor.GetRenderWindow().Finalize()
        self.renderwindowinteractor.GetRenderWindow().SetSize(1600, 800)
        self.renderwindowinteractor.GetRenderWindow().Render()
        self.close()

    # set mesh as actor in vtk frame
    def polyDataToActor(self, polydata):
        """Wrap the provided vtkPolyData object in a mapper and an actor, returning
        the actor."""
        mapper = vtk.vtkPolyDataMapper()
        boundarymapper = vtk.vtkPolyDataMapper()
        if vtk.VTK_MAJOR_VERSION <= 5:
            mapper.SetInput(self.reader.GetOutput())
            mapper.SetInput(polydata)
        else:
            mapper.SetInputConnection(self.reader.GetOutputPort())
        actor = vtk.vtkActor()
        boundaryCells = self.polydataboundary(polydata)
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToSurface()
        boundaryPolyData = vtk.vtkPolyData()
        boundaryPolyData.SetPoints(boundaryCells.GetOutput().GetPoints())
        boundaryPolyData.SetStrips(boundaryCells.GetOutput().GetLines())
        boundarymapper.SetInputData(boundaryPolyData)
        boundaryactor = vtk.vtkActor()
        boundaryactor.SetMapper(boundarymapper)
        print(boundaryactor.GetBounds())
        self.meshbounds = []
        for i in range(6):
            self.meshbounds.append(actor.GetBounds()[i])
        # color RGB must be /255 for Red, Green , blue color code
        actor.GetProperty().SetColor((230 / 255), (230 / 255), (250 / 255))
        actor.GetProperty().SetDiffuse(0.8)
        colorsd = vtkNamedColors()
        actor.GetProperty().SetDiffuseColor(colorsd.GetColor3d("LightSteelBlue"))
        actor.GetProperty().SetSpecular(0.3)
        actor.GetProperty().SetSpecularPower(60.0)
        actor.SetOrientation(1, 0, 0)
        self.append_filterpolydata.AddInputData(actor.GetMapper().GetInput())
        self.append_filterpolydata.Update()
        return actor, boundaryPolyData

    def polydataboundary(self, polydata):
        # Extract edges
        edgeExtractor = vtk.vtkExtractEdges()
        edgeExtractor.SetInputData(self.reader.GetOutput())
        edgeExtractor.Update()

        # Get the boundary edges
        boundaryEdges = vtk.vtkFeatureEdges()
        boundaryEdges.SetInputData(edgeExtractor.GetOutput())
        boundaryEdges.BoundaryEdgesOn()
        boundaryEdges.NonManifoldEdgesOff()
        boundaryEdges.FeatureEdgesOff()
        boundaryEdges.ManifoldEdgesOff()
        boundaryEdges.Update()

        # Get the boundary cells
        boundaryCells = vtk.vtkStripper()
        boundaryCells.SetInputData(boundaryEdges.GetOutput())
        boundaryCells.Update()
        return boundaryCells
