from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import vtk
from vtk import *


class myInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(
        self,
        xlabel,
        ylabel,
        ren,
        renderwindowinteractor,
        meshbounds,
        xlabelbefore,
        ylabelbefore,
        zlabelbefore,
        polydata,
        polys,
        reader,
        parent=None,
    ):
        self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)
        self.AddObserver("RightButtonPressEvent", self.RightButtonPressEvent)
        self.AddObserver("MiddleButtonPressEvent", self.MiddleButtonPressEvent)
        self.selected_cells = []
        self.defaultposition = [0, 0, 1]
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
        self.pointx = []
        self.pointz = []
        self.pointy = []
        self.renderwindowinteractors.GetRenderWindow().Render()
        _translate = QtCore.QCoreApplication.translate
        self.xlabelbefore = xlabelbefore
        self.ylabelbefore = ylabelbefore
        self.zlabelbefore = zlabelbefore
        self.points = []
        xlabelbefore.setText(
            _translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0])))
        )
        ylabelbefore.setText(
            _translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1])))
        )
        zlabelbefore.setText(
            _translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[2])))
        )

    def leftButtonPressEvent(self, obj, event):
        clickPos = self.GetInteractor().GetEventPosition()  # <<<-----<
        _translate = QtCore.QCoreApplication.translate
        self.xlabels.setText(
            _translate("MainWindow", str("{0:.2f}".format(clickPos[0])))
        )
        self.ylabels.setText(
            _translate("MainWindow", str("{0:.2f}".format(clickPos[1])))
        )
        camera = self.render.GetActiveCamera()
        self.xlabelbefore.setText(
            _translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0])))
        )
        self.ylabelbefore.setText(
            _translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1])))
        )
        self.zlabelbefore.setText(
            _translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[2])))
        )
        if self.actor != None:
            camera.SetPosition(
                camera.GetPosition()[0],
                camera.GetPosition()[1],
                camera.GetPosition()[2],
            )
            self.actor.SetPosition(
                camera.GetPosition()[0],
                camera.GetPosition()[1],
                camera.GetPosition()[2],
            )
            self.render.ResetCameraClippingRange()
            self.renderwindowinteractors.GetRenderWindow().Render()
        self.OnLeftButtonDown()

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

    def RightButtonPressEvent(self, obj, event):
        clickPos = self.GetInteractor().GetEventPosition()  # <<<-----<
        _translate = QtCore.QCoreApplication.translate
        self.xlabels.setText(
            _translate("MainWindow", str("{0:.2f}".format(clickPos[0])))
        )
        self.ylabels.setText(
            _translate("MainWindow", str("{0:.2f}".format(clickPos[1])))
        )
        center = [
            (self.meshbound[0] + self.meshbound[1]) / 2,
            (self.meshbound[2] + self.meshbound[3]) / 2,
            (self.meshbound[4] + self.meshbound[5]) / 2,
        ]
        picker = vtk.vtkPropPicker()
        # Click position is mostly 2d coordination x and y axis
        picker.Pick(80, center[1], center[2], self.render)
        world_pos = picker.GetPickPosition()
        self.actor = self.create_cube_actor()
        self.actor.SetPosition(80, center[1], center[2])
        self.actor.SetOrientation(
            self.defaultposition[0], self.defaultposition[1], self.defaultposition[2]
        )
        self.render.AddActor(self.actor)
        camera = self.render.GetActiveCamera()
        camera.SetPosition(80, center[1], center[2])
        camera.SetViewUp(
            self.defaultposition[0], self.defaultposition[1], self.defaultposition[2]
        )
        self.render.SetActiveCamera(camera)  # insert and replace a new camera
        self.renderwindowinteractors.GetRenderWindow().Render()
        # camera coordinates
        self.xlabelbefore.setText(
            _translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0])))
        )
        self.ylabelbefore.setText(
            _translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1])))
        )
        self.zlabelbefore.setText(
            _translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[2])))
        )
        self.AddObserver("KeyPressEvent", self.KeyPressed)
        self.OnRightButtonDown()

    def MiddleButtonPressEvent(self, obj, event):
        clickPos = self.GetInteractor().GetEventPosition()
        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.render)
        pickedPos = picker.GetPickPosition()
        if len(self.points) < 2:
            self.points.append(pickedPos)
            print("Point", len(self.points), "picked at:", pickedPos)

            if len(self.points) == 2:
                print("Two points picked:", self.points)
                self.createCube()
                # Do whatever you want with the points here
        else:
            self.points = []  # Reset points if more than two are picked

        self.OnMiddleButtonDown()

    def createCube(self):
        if len(self.points) == 2:
            cubeSource = vtk.vtkCubeSource()
            cubeSource.SetCenter(
                (self.points[0][0] + self.points[1][0]) / 2,
                (self.points[0][1] + self.points[1][1]) / 2,
                (self.points[0][2] + self.points[1][2]) / 2,
            )
            if self.points[1][2] > self.points[0][2]:
                cubeSource.SetXLength(40)
                cubeSource.SetYLength(abs(self.points[1][1] - self.points[0][1]))
                cubeSource.SetZLength(abs(self.points[1][2] - self.points[0][2]))
            else:
                cubeSource.SetXLength(40)
                cubeSource.SetYLength(abs(self.points[0][1] - self.points[1][1]))
                cubeSource.SetZLength(abs(self.points[0][2] - self.points[1][2]))

            cubeMapper = vtk.vtkPolyDataMapper()
            cubeMapper.SetInputConnection(cubeSource.GetOutputPort())

            cubeActor = vtk.vtkActor()
            cubeActor.SetMapper(cubeMapper)
            cubeActor.GetProperty().SetColor(1, 0, 0)  # Red color
            self.render.AddActor(cubeActor)
            self.renderwindowinteractors.GetRenderWindow().Render()

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
            self.render.RemoveActor(self.actor)
            self.renderwindowinteractors.GetRenderWindow().Render()
            return  # return to its original position
        elif key in "Up":
            if camera_position[0] < (self.meshbound[1] - 100):
                actor_position[0] += actor_speed
                camera_position[0] += actor_speed
        elif key in "Down":
            if camera_position[0] > (self.meshbound[0] + 100):
                actor_position[0] -= actor_speed
                camera_position[0] -= actor_speed
        elif key in "Left":
            if camera_position[1] < (self.meshbound[3] - 100):
                actor_position[1] += actor_speed
                camera_position[1] += actor_speed
        elif key in "Right":
            if camera_position[1] > (self.meshbound[2] + 100):
                actor_position[1] -= actor_speed
                camera_position[1] -= actor_speed
        self.actor.SetPosition(actor_position)
        self.actor.SetOrientation(
            self.defaultposition[0], self.defaultposition[1], self.defaultposition[2]
        )
        camera.SetPosition(camera_position)
        camera.SetViewUp(
            self.defaultposition[0], self.defaultposition[1], self.defaultposition[2]
        )
        self.render.ResetCameraClippingRange()
        self.renderwindowinteractors.GetRenderWindow().Render()
        # camera coordinates
        _translate = QtCore.QCoreApplication.translate
        self.xlabelbefore.setText(
            _translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[0])))
        )
        self.ylabelbefore.setText(
            _translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[1])))
        )
        self.zlabelbefore.setText(
            _translate("MainWindow", str("{0:.2f}".format(camera.GetPosition()[2])))
        )
        self.render.RemoveActor(self.actor)
