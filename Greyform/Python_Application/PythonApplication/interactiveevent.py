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

class myInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self,xlabel, ylabel, ren,  renderwindowinteractor,meshbounds, xlabelbefore , ylabelbefore, parent=None):
        self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)
        self.AddObserver("RightButtonPressEvent", self.RightButtonPressEvent)
        self.AddObserver("KeyPressEvent", self.KeyPressed)
        self.AddObserver('InteractionEvent', CameraObserver(ren.GetActiveCamera()))
        camera = vtk.vtkCamera()
        ren.SetActiveCamera(camera)
        camera.ParallelProjectionOn()
        ren.ResetCamera()
        self.xlabels = xlabel
        self.ylabels = ylabel
        self.render = ren
        self.renderwindowinteractors = renderwindowinteractor
        self.meshbound = meshbounds
        self.render.ResetCamera()
        self.renderwindowinteractors.GetRenderWindow().Render()
        _translate = QtCore.QCoreApplication.translate
        self.xlabelbefore = xlabelbefore
        self.ylabelbefore = ylabelbefore
        xlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0]))))
        ylabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1]))))


    def leftButtonPressEvent(self, obj, event):
        clickPos = self.GetInteractor().GetEventPosition()       # <<<-----<
        _translate = QtCore.QCoreApplication.translate
        self.xlabels.setText(_translate("MainWindow", str("{0:.2f}".format(clickPos[0]))))
        self.ylabels.setText(_translate("MainWindow", str("{0:.2f}".format(clickPos[1]))))
        self.OnLeftButtonDown()

    def RightButtonPressEvent(self, obj , event):
        clickPos = self.GetInteractor().GetEventPosition()       # <<<-----<
        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.0005)
        picker.Pick(clickPos[0], clickPos[1], 0, self.render)
        world_pos = picker.GetPickPosition()
        camera = vtk.vtkCamera()
        camera.SetPosition(world_pos)
        self.render.SetActiveCamera(camera)
        self.renderwindowinteractors.GetRenderWindow().Render()
        self.OnRightButtonDoubleClick()

    def KeyPressed(self, obj, event):
        key = self.renderwindowinteractors.GetKeySym()
        camera = self.render.GetActiveCamera()
        if key in "l":
            camera.ParallelProjectionOn()
            self.render.ResetCamera()
            self.renderwindowinteractors.GetRenderWindow().Render()
            _translate = QtCore.QCoreApplication.translate
            self.xlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0]))))
            self.ylabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1]))))
        elif key in "Up":
            camera.Elevation(5)
            camera.OrthogonalizeViewUp()
            self.renderwindowinteractors.GetRenderWindow().Render()
            _translate = QtCore.QCoreApplication.translate
            self.xlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0]))))
            self.ylabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1]))))
        elif key in "Down":
            camera.Elevation(-5)
            camera.OrthogonalizeViewUp()
            self.renderwindowinteractors.GetRenderWindow().Render()
            _translate = QtCore.QCoreApplication.translate
            self.xlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0]))))
            self.ylabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1]))))
        elif key in "Left":
            camera.Azimuth(-5)
            camera.OrthogonalizeViewUp()
            self.renderwindowinteractors.GetRenderWindow().Render()
            _translate = QtCore.QCoreApplication.translate
            self.xlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0]))))
            self.ylabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1]))))
        elif key in "Right":
            camera.Azimuth(5)
            camera.OrthogonalizeViewUp() 
            self.renderwindowinteractors.GetRenderWindow().Render()
            _translate = QtCore.QCoreApplication.translate
            self.xlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0]))))
            self.ylabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1]))))      

class CameraObserver(object):
    def __init__(self, cam):
        self.cam = cam

    def __call__(self, caller, ev):
        self.cam.SetViewUp(0, 0, 1)



        

