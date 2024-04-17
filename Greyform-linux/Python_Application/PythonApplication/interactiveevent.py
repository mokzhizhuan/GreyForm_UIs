from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import vtk
from vtk import *
import PythonApplication.middlebuttoninteractor as middlebuttoninteractor


# insert interactive event for the stl mesh , left click is for moving the stl ,
# right click is to insert the actor in the room view , room view only include up down left and right and left click to move the object
# middle click is to insert an object tht was marked
# l key is to remove the actor in the room view and set the mesh to the original position
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
        polys,
        reader,
        append_filterpolydata,
        parent=None,
    ):
        self.movement = None
        self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)
        self.addactor = self.AddObserver(
            "RightButtonPressEvent", self.RightButtonPressEvent
        )
        self.defaultposition = [0, 0, 1]
        ren.ResetCamera()
        camera = ren.GetActiveCamera()
        self.xlabels = xlabel
        self.ylabels = ylabel
        self.render = ren
        self.renderwindowinteractors = renderwindowinteractor
        self.middlebuttonobserver = middlebuttoninteractor.MiddleButtonPressed(
            self,
            self.render,
            self.renderwindowinteractors,
            append_filterpolydata,
        )
        self.meshbound = meshbounds
        self.polys = polys
        self.actor = None
        self.renderwindowinteractors.GetRenderWindow().Render()
        _translate = QtCore.QCoreApplication.translate
        self.xlabelbefore = xlabelbefore
        self.ylabelbefore = ylabelbefore
        self.zlabelbefore = zlabelbefore
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
        self.insertshapeevent = self.AddObserver(
            "MiddleButtonPressEvent", self.middlebuttonobserver.MiddleButtonPressEvent
        )
        self.movement = self.AddObserver("KeyPressEvent", self.KeyPressed)
        self.RemoveObserver(self.addactor)
        self.OnRightButtonDown()

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
            self.RemoveObserver(self.movement)
            self.RemoveObserver(self.insertshapeevent)
            self.AddObserver("RightButtonPressEvent", self.RightButtonPressEvent)
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
