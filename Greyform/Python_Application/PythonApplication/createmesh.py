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

class createMesh(QMainWindow):
    def __init__(self):
        self.reader = None

    #vtkrenderwindow
    def createmesh(self, CurrentMesh, renderwindowinteractor):
        ren = vtk.vtkRenderer()
        renderwindowinteractor.GetRenderWindow().AddRenderer(ren)
        renderwindowinteractor.GetRenderWindow().SetSize(1600, 800)
        polydata = createMesh.loadStl(self, CurrentMesh)
        camera = vtk.vtkInteractorStyleTrackballCamera()
        axes = vtkAxesActor()
        #vtkOrientation
        widget = vtkOrientationMarkerWidget()
        widget.SetOrientationMarker(axes)
        widget.SetInteractor(renderwindowinteractor)
        widget.SetViewport(0.0, 0.0, 0.4, 0.4)
        widget.SetEnabled(1)
        widget.InteractiveOn()
        renderwindowinteractor.SetInteractorStyle(camera)
        ren.AddActor(createMesh.polyDataToActor(self, polydata))
        ren.SetBackground(255, 255, 255)
        renderwindowinteractor.Initialize()
        renderwindowinteractor.GetRenderWindow().Render()
        renderwindowinteractor.Start()


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
        actor.GetProperty().SetColor((230/255),(230/255), (250/255))
        return actor


    
