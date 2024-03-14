import sys
from PyQt5 import  QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog, QProgressBar, QLabel
from PyQt5.QtCore import QTimer
from decimal import Decimal
import vtk
from vtk import *
from vtkmodules.qt import QVTKRenderWindowInteractor
import math
import PythonApplication.interactiveevent as events
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element as Element
from ifcopenshell.util.placement import get_local_placement
import multiprocessing
import vtkmodules.vtkInteractionStyle
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOGeometry import vtkSTLReader

class pythonProgressBar(QDialog):
    def __init__(self, value , polydata, ren, renderwindowinteractor, xlabelbefore, ylabelbefore, xlabel , ylabel):
        super().__init__()
        progress_layout = QVBoxLayout()
        self.setWindowTitle("Progress Window")
        self.setGeometry(100, 100, 400, 200)
        self.setLayout(progress_layout)
        print(polydata)
        label = QLabel("Graphics is loading , please wait.")
        label.setGeometry(QtCore.QRect(50, 30, 170, 30))
        label.setWordWrap(True)
        label.setObjectName("label")
        self.reader = vtk.vtkSTLReader()
        self.meshbounds = None
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(30, 130, 340, 30)
        self.value = value
        self.polydata = polydata
        self.ren = ren
        self.ren.SetBackground(255, 255, 255)
        polydataextracted = self.start_progress()
        self.ren.AddActor(self.polyDataToActor(polydataextracted))
        camera = events.myInteractorStyle(xlabel,ylabel,ren , renderwindowinteractor, self.meshbounds, xlabelbefore, ylabelbefore)
        renderwindowinteractor.SetInteractorStyle(camera)

        # Set the layout for the dialog
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100) 
        progress_layout.addWidget(label)
        progress_layout.addWidget(self.progress_bar)
        self.stop_progress()

    def start_progress(self):
        poly_data = QTimer.singleShot(self.value, self.loadStl)
        return poly_data
    
    def update_progress(self):
        value = self.progress_bar.value()
        if value < 100:
            self.progress_bar.setValue(value + 1)
            QTimer.singleShot(100, self.update_progress)  # Update progress again after 100 milliseconds
        else:
            self.timer.stop()  # Stop the timer when progress reaches 100%
            self.progress_bar.setValue(0)  # Reset progress to 0
            self.timer.start(100)

    def loadStl(self):
        self.update_progress()
        """Load the given STL file, and return a vtkPolyData object for it."""
        self.reader.SetFileName(self.polydata)
        self.reader.Update()
        polydata = self.reader.GetOutput()
        center = [0.0, 0.0, 0.0]
        for i in range(polydata.GetNumberOfPoints()):
            point = polydata.GetPoint(i)
            center[0] += point[0]
            center[1] += point[1]
            center[2] += point[2]

        num_points = polydata.GetNumberOfPoints()
        center[0] /= num_points
        center[1] /= num_points
        center[2] /= num_points
        return polydata
    
    def polyDataToActor(self, polydata):
        """Wrap the provided vtkPolyData object in a mapper and an actor, returning
    the actor."""
        mapper = vtk.vtkPolyDataMapper()
        if vtk.VTK_MAJOR_VERSION <= 5:
            mapper.SetInput(self.reader.GetOutput())
            mapper.SetInput(polydata)
        else:
            mapper.SetInputConnection(self.reader.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToSurface()
        print(actor.GetBounds())
        self.meshbounds = []
        for i in range(6):
            self.meshbounds.append(actor.GetBounds()[i])
        #color RGB must be /255 for Red, green , blue color code
        actor.GetProperty().SetColor((230/255),(230/255), (250/255))
        actor.GetProperty().SetDiffuse(0.8)
        colorsd = vtkNamedColors()
        actor.GetProperty().SetDiffuseColor(colorsd.GetColor3d('LightSteelBlue'))
        actor.GetProperty().SetSpecular(0.3)
        actor.GetProperty().SetSpecularPower(60.0)
        return actor
    
    def stop_progress(self):
        self.timer.stop()
        self.close()
