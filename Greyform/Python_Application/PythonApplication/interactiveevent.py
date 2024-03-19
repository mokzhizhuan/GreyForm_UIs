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
    def __init__(self,xlabel, ylabel, ren,  renderwindowinteractor,meshbounds, xlabelbefore , ylabelbefore,zlabelbefore, polydata, polys, reader,  parent=None):
        self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)
        self.AddObserver("RightButtonPressEvent", self.RightButtonPressEvent)
        self.AddObserver("MiddleButtonPressEvent", self.MiddleButtonPressEvent)
        self.selected_cells = [] 
        ren.ResetCamera()
        camera = ren.GetActiveCamera()
        self.xlabels = xlabel
        self.ylabels = ylabel
        self.render = ren
        self.zstore = 0
        self.renderwindowinteractors = renderwindowinteractor
        self.meshbound = meshbounds
        self.mesh = polydata
        self.polys = polys
        self.reader = reader
        self.actor = None
        self.renderwindowinteractors.GetRenderWindow().Render()
        _translate = QtCore.QCoreApplication.translate
        self.xlabelbefore = xlabelbefore
        self.ylabelbefore = ylabelbefore
        self.zlabelbefore = zlabelbefore
        xlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0]))))
        ylabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1]))))
        zlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[2]))))

    def leftButtonPressEvent(self, obj, event):
        clickPos = self.GetInteractor().GetEventPosition()       # <<<-----<
        _translate = QtCore.QCoreApplication.translate
        self.xlabels.setText(_translate("MainWindow", str("{0:.2f}".format(clickPos[0]))))
        self.ylabels.setText(_translate("MainWindow", str("{0:.2f}".format(clickPos[1]))))
        camera = self.render.GetActiveCamera()
        self.xlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0]))))
        self.ylabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1]))))
        self.zlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[2]))))
        if self.actor != None:
            camera.SetPosition(camera.GetPosition()[0], camera.GetPosition()[1],camera.GetPosition()[2])
            self.actor.SetPosition(camera.GetPosition()[0], camera.GetPosition()[1],camera.GetPosition()[2])
            self.render.ResetCameraClippingRange() 
            self.renderwindowinteractors.GetRenderWindow().Render()

        self.OnLeftButtonDown()

    # Set up camera observer to keep it inside the mesh
    def camera_observer(self, obj, event):
        camera = self.render.GetActiveCamera()
        position = camera.GetPosition()
        focal_point = camera.GetFocalPoint()
        self.render.ResetCameraClippingRange()

        # Move the camera inside the mesh
        if not self.meshbound:
            return

        for i in range(3):
            if position[i] < self.meshbound[i * 2]:
                position[i] = self.meshbound[i * 2]
            elif position[i] > self.meshbound[i * 2 + 1]:
                position[i] = self.meshbound[i * 2 + 1]

        camera.SetPosition(position)
        self.render.ResetCameraClippingRange()

    # Define function to create a cube actor
    def create_cube_actor(self):
        cube_source = vtk.vtkCubeSource()
        cube_mapper = vtk.vtkPolyDataMapper()
        cube_mapper.SetInputConnection(cube_source.GetOutputPort())
        cube_actor = vtk.vtkActor()
        cube_actor.SetMapper(cube_mapper)
        cube_actor.GetProperty().SetColor(1, 0, 0)  # Red color
        cube_actor.SetVisibility(False)
        return cube_actor

    def RightButtonPressEvent(self, obj , event):
        clickPos = self.GetInteractor().GetEventPosition()       # <<<-----<
        _translate = QtCore.QCoreApplication.translate
        self.xlabels.setText(_translate("MainWindow", str("{0:.2f}".format(clickPos[0]))))
        self.ylabels.setText(_translate("MainWindow", str("{0:.2f}".format(clickPos[1]))))
        picker = vtk.vtkPropPicker()
        #Click position is mostly 2d coordination x and y axis
        picker.Pick(clickPos[0], clickPos[1],0, self.render)
        world_pos = picker.GetPickPosition()
        self.actor = self.create_cube_actor()
        self.actor.SetPosition(world_pos)
        self.actor.SetOrientation(0,1,0)
        self.render.AddActor(self.actor)
        camera = self.render.GetActiveCamera()
        camera.SetPosition(world_pos)
        camera.SetViewUp(0,1,0)
        self.render.SetActiveCamera(camera)#insert and replace a new camera
        self.renderwindowinteractors.GetRenderWindow().Render()
        #camera coordinates
        self.xlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0]))))
        self.ylabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1]))))
        self.zlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[2]))))
        self.AddObserver(vtk.vtkCommand.ModifiedEvent, self.camera_observer)
        self.AddObserver("KeyPressEvent", self.KeyPressed)
        self.OnRightButtonDown()

    def changeCameraView(self):
        camera = self.render.GetActiveCamera()
        camera.SetFocalPoint(self.actor.GetCenter())
        self.render.ResetCamera()

    def MiddleButtonPressEvent(self, obj, event):
        click_pos = self.GetInteractor().GetEventPosition() 
        _translate = QtCore.QCoreApplication.translate
        self.xlabels.setText(_translate("MainWindow", str("{0:.2f}".format(click_pos[0]))))
        self.ylabels.setText(_translate("MainWindow", str("{0:.2f}".format(click_pos[1]))))
        # Check if the click position intersects with the mesh
        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.001)  # Set tolerance to determine whether a pick occurs
        picker.PickFromListOn()  # Ensure that only the mesh is pickable
        picker.AddPickList(self.mesh)

        picker.Pick(click_pos[0], click_pos[1], 0, self.render)
        if picker.GetCellId() == -1:
            # If the click occurs outside the mesh, set the camera to show an outside view
            self.setOutsideView()
        camera = self.render.GetActiveCamera()
        self.render.RemoveActor(self.actor)
        self.OnMiddleButtonDown()

    def setOutsideView(self):
        # Calculate the bounding box of the mesh
        center = [(self.meshbound[0] + self.meshbound[1]) / 2, (self.meshbound[2] + self.meshbound[3]) / 2, (self.meshbound[4] + self.meshbound[5]) / 2]
        camera = self.render.GetActiveCamera()
        # Set camera position and focal point to show an outside view
        camera.SetPosition(center[0], center[1], self.meshbound[5] + 2 * (self.meshbound[5] - self.meshbound[4]))
        camera.SetFocalPoint(center)
        _translate = QtCore.QCoreApplication.translate
        self.xlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0]))))
        self.ylabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1]))))
        self.zlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[2]))))

    def KeyPressed(self, obj, event):
        key = self.renderwindowinteractors.GetKeySym()
        actor_position = []
        camera_position = []
        actor_speed = 20
        camera = self.render.GetActiveCamera()
        for i in range(3):
            actor_position.append(self.actor.GetPosition()[i])
            camera_position.append(self.actor.GetPosition()[i])
        if key in "l":
            self.render.ResetCamera()
            self.renderwindowinteractors.GetRenderWindow().Render()
            #camera coordinates
            _translate = QtCore.QCoreApplication.translate
            self.xlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0]))))
            self.ylabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1]))))
            self.zlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[2]))))
            self.render.RemoveActor(self.actor)
        elif key in "Up":
            if camera_position[0] < (self.meshbound[1]-80):
                actor_position[0] += actor_speed
                camera_position[0] += actor_speed
                self.actor.SetPosition(actor_position)
                self.actor.SetOrientation(1,1,0)
                camera.SetPosition(camera_position)
                camera.SetViewUp(1,1,0)
                self.render.ResetCameraClippingRange() 
                self.renderwindowinteractors.GetRenderWindow().Render()
                #camera coordinates
                _translate = QtCore.QCoreApplication.translate
                self.xlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0]))))
                self.ylabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1]))))
                self.zlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[2]))))
                self.AddObserver(vtk.vtkCommand.ModifiedEvent, self.camera_observer)
        elif key in "Down":
            if camera_position[0] > (self.meshbound[0]+80):
                actor_position[0] -= actor_speed
                camera_position[0] -= actor_speed
                self.actor.SetPosition(actor_position)
                self.actor.SetOrientation(1,1,0)
                camera.SetPosition(camera_position)
                camera.SetViewUp(1,1,0)
                self.render.ResetCameraClippingRange() 
                self.renderwindowinteractors.GetRenderWindow().Render()
            #camera coordinates
            _translate = QtCore.QCoreApplication.translate
            self.xlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0]))))
            self.ylabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1]))))
            self.zlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[2]))))
            self.AddObserver(vtk.vtkCommand.ModifiedEvent, self.camera_observer)
        elif key in "Left":
            if camera_position[1] < (self.meshbound[3]-100):
                actor_position[1] += actor_speed
                camera_position[1] += actor_speed
                self.actor.SetPosition(actor_position)
                self.actor.SetOrientation(1,1,0)
                camera.SetPosition(camera_position)
                camera.SetViewUp(1,1,0)
                self.render.ResetCameraClippingRange() 
                self.renderwindowinteractors.GetRenderWindow().Render()
            #camera coordinates
            _translate = QtCore.QCoreApplication.translate
            self.xlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0]))))
            self.ylabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1]))))
            self.zlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[2]))))
            self.AddObserver(vtk.vtkCommand.ModifiedEvent, self.camera_observer)
        elif key in "Right":
            if camera_position[1] > (self.meshbound[2]+80):
                actor_position[1] -= actor_speed
                camera_position[1] -= actor_speed
                self.actor.SetPosition(actor_position)
                self.actor.SetOrientation(1,1,0)
                camera.SetPosition(camera_position)
                camera.SetViewUp(1,1,0)
                self.render.ResetCameraClippingRange() 
                self.renderwindowinteractors.GetRenderWindow().Render()
            #camera coordinates
            _translate = QtCore.QCoreApplication.translate
            self.xlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0]))))
            self.ylabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1]))))    
            self.zlabelbefore.setText(_translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[2]))))
            self.AddObserver(vtk.vtkCommand.ModifiedEvent, self.camera_observer)


class CameraObserver(object):
    def __init__(self, cam):
        self.cam = cam

    def __call__(self, caller, ev):
        self.cam.SetViewUp(0, 0, 1)



        

