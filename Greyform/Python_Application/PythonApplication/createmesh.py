import sys
from PyQt5 import QtCore, QtWidgets ,QtOpenGL, QtGui , uic
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *  
from PyQt5.QtGui import *
import OpenGL.GL as gl        
from OpenGL import GLU   
from pyqtgraph.opengl import  GLMeshItem 
import pyqtgraph.opengl as gl
import numpy as np
from stl import mesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pyvista as pv
import vtk
from ipywidgets import interact
from pyvistaqt import QtInteractor
import pandas as pd
import cv2
from vtk import *
from vtk import vtkUnstructuredGridReader
from vtkmodules.qt import QVTKRenderWindowInteractor
import math
import PythonApplication.interactiveevent as events

class createMesh(QMainWindow):
    def __init__(self):
        self.reader = None
        self.bathview = None
        self.showerview = None

    #vtkrenderwindow
    def createmesh(self, CurrentMesh, renderwindowinteractor , ylabel , xlabel, xlabelbefore, ylabelbefore):
        ren = vtk.vtkRenderer()
        renderwindowinteractor.GetRenderWindow().AddRenderer(ren)
        renderwindowinteractor.GetRenderWindow().SetSize(1600, 800)
        polydata = createMesh.loadStl(self, CurrentMesh)
        ren.AddActor(createMesh.polyDataToActor(self, polydata))
        ren.SetBackground(255, 255, 255)
        actorviewbath = vtkCylinderSource()
        actorviewbath.SetCenter(0.0,0.0,0.0)
        actorviewbath.SetRadius(5)
        actorviewbath.SetHeight(2)
        actorviewbath.SetResolution(10)
        actorviewshower = vtkCylinderSource()
        actorviewshower.SetCenter(0.0,0.0,0.0)
        actorviewshower.SetRadius(5)
        actorviewshower.SetHeight(2)
        actorviewshower.SetResolution(10)
        ren.AddActor(createMesh.loadactorviewbath(self, actorviewbath))
        ren.AddActor(createMesh.loadactorviewshower(self, actorviewshower))
        camera = events.myInteractorStyle(xlabel,ylabel,ren , renderwindowinteractor, self.bathview, self.showerview)
        renderwindowinteractor.SetInteractorStyle(camera)
        renderwindowinteractor.GetRenderWindow().Render()
        renderwindowinteractor.Initialize()
        renderwindowinteractor.Start()
        _translate = QtCore.QCoreApplication.translate
        xlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(ren.GetActiveCamera().GetPosition()[0]))))
        ylabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(ren.GetActiveCamera().GetPosition()[1]))))





    def loadStl(self, fname):
        """Load the given STL file, and return a vtkPolyData object for it."""
        self.reader = vtk.vtkSTLReader()
        self.reader.SetFileName(fname)
        self.reader.Update()
        polydata = self.reader.GetOutput()
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
        #color RGB must be /255 for Red, green , blue color code
        actor.GetProperty().SetColor((230/255),(230/255), (250/255))
        return actor
    
    def loadactorviewbath(self, polydata):
        """Wrap the provided vtkPolyData object in a mapper and an actor, returning
    the actor."""
        mapper = vtk.vtkPolyDataMapper()
        if vtk.VTK_MAJOR_VERSION <= 5:
            mapper.SetInput(polydata.GetOutput())
            mapper.SetInput(polydata)
        else:
            mapper.SetInputConnection(polydata.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToSurface()
        actor.SetPosition(300,500,20)
        actor.SetVisibility(False)
        self.bathview = []
        self.bathview.append(actor.GetPosition()[0])
        self.bathview.append(actor.GetPosition()[1])
        self.bathview.append(actor.GetPosition()[2])
        return actor
    
    def loadactorviewshower(self, polydata):
        """Wrap the provided vtkPolyData object in a mapper and an actor, returning
    the actor."""
        mapper = vtk.vtkPolyDataMapper()
        if vtk.VTK_MAJOR_VERSION <= 5:
            mapper.SetInput(polydata.GetOutput())
            mapper.SetInput(polydata)
        else:
            mapper.SetInputConnection(polydata.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToSurface()
        actor.SetPosition(2400,500,20)
        actor.SetVisibility(False)
        self.showerview = []
        self.showerview.append(actor.GetPosition()[0])
        self.showerview.append(actor.GetPosition()[1])
        self.showerview.append(actor.GetPosition()[2])
        return actor



    
