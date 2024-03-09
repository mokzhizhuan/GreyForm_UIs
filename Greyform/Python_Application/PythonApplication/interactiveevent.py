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

class myInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self,xlabel, ylabel, ren,  renderwindowinteractor,actorviewbathpos , actorviewshowerpos,parent=None):
        self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)
        self.AddObserver("RightButtonPressEvent", self.RightButtonPressEvent)
        self.AddObserver("UpButtonPressEvent", self.UpButtonPressEvent)
        self.AddObserver("DownButtonPressEvent", self.UpButtonPressEvent)
        self.AddObserver("KeyPressEvent", self.KeyPressed)
        self.xlabels = xlabel
        self.ylabels = ylabel
        self.render = ren
        self.renderwindowinteractors = renderwindowinteractor
        self.actorviewsbathpos = actorviewbathpos
        self.actorviewsshowerpos = actorviewshowerpos


    def leftButtonPressEvent(self, obj, event):

        clickPos = self.GetInteractor().GetEventPosition()       # <<<-----<
        _translate = QtCore.QCoreApplication.translate
        self.xlabels.setText(_translate("MainWindow", str("{0:.2f}".format(clickPos[0]))))
        self.ylabels.setText(_translate("MainWindow", str("{0:.2f}".format(clickPos[1]))))
        self.OnLeftButtonDown()

    def RightButtonPressEvent(self, obj, event):

        clickPos = self.GetInteractor().GetEventPosition()       # <<<-----<
        _translate = QtCore.QCoreApplication.translate
        self.xlabels.setText(_translate("MainWindow", str("{0:.2f}".format(clickPos[0]))))
        self.ylabels.setText(_translate("MainWindow", str("{0:.2f}".format(clickPos[1]))))

        self.OnRightButtonDown()

    def UpButtonPressEvent(self, obj, event):

        clickPos = self.GetInteractor().GetEventPosition()       # <<<-----<
        _translate = QtCore.QCoreApplication.translate
        self.xlabels.setText(_translate("MainWindow", str("{0:.2f}".format(clickPos[0]))))
        self.ylabels.setText(_translate("MainWindow", str("{0:.2f}".format(clickPos[1]))))

        self.OnKeyUp()

    def DownButtonPressEvent(self, obj, event):

        clickPos = self.GetInteractor().GetEventPosition()       # <<<-----<
        _translate = QtCore.QCoreApplication.translate
        self.xlabels.setText(_translate("MainWindow", str("{0:.2f}".format(clickPos[0]))))
        self.ylabels.setText(_translate("MainWindow", str("{0:.2f}".format(clickPos[1]))))

        self.OnKeyDown()

    def KeyPressed(self, obj, event):
        key = self.renderwindowinteractors.GetKeySym()
        camera = vtk.vtkCamera()
        print(key)
        if key in "j":
            print(self.actorviewsbathpos)
            camera.SetFocalPoint(self.actorviewsbathpos[0],self.actorviewsbathpos[1], self.actorviewsbathpos[2])
            self.render.SetActiveCamera(camera)
        elif key in "n":
            print(self.actorviewsshowerpos)
            camera.SetFocalPoint(self.actorviewsshowerpos[0],self.actorviewsshowerpos[1], self.actorviewsshowerpos[2])
            self.render.SetActiveCamera(camera)
