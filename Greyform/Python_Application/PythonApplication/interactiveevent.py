from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import vtk
from vtk import *
import PythonApplication.middlebuttoninteractor as middlebuttoninteractor
import math


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
        polydata,
        polys,
        reader,
        append_filterpolydata,
        parent=None,
    ):
        # variable initialize
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
        """self.middlebuttonobserver = middlebuttoninteractor.MiddleButtonPressed(
            self,
            self.render,
            self.renderwindowinteractors,
            append_filterpolydata,
        )"""  # marking points interaction
        self.meshbound = meshbounds
        self.mesh = polydata
        self.polys = polys
        self.reader = reader
        self.actor_speed = 0
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
        camera = (
            self.GetInteractor()
            .GetRenderWindow()
            .GetRenderers()
            .GetFirstRenderer()
            .GetActiveCamera()
        )
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

    # create a cube actor for inside room view
    def create_cube_actor(self):
        cube_source = vtk.vtkCubeSource()
        cube_mapper = vtk.vtkPolyDataMapper()
        cube_mapper.SetInputConnection(cube_source.GetOutputPort())
        cube_actor = vtk.vtkActor()
        cube_actor.SetMapper(cube_mapper)
        cube_actor.GetProperty().SetColor(1, 0, 0)  # Red color
        cube_actor.SetVisibility(False)
        return cube_actor

    # inside view
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
        bounds = self.actor.GetBounds()
        secondactorcenter = [
            (bounds[0] + bounds[1]) / 2,
            (bounds[2] + bounds[3]) / 2,
            (bounds[4] + bounds[5]) / 2,
        ]
        self.render.AddActor(self.actor)
        camera = self.render.GetActiveCamera()
        camera.SetPosition(80, center[1], center[2])
        camera.SetViewUp(
            self.defaultposition[0], self.defaultposition[1], self.defaultposition[2]
        )
        self.render.SetActiveCamera(camera)  # insert and replace a new camera
        self.renderwindowinteractors.GetRenderWindow().Render()
        self.collision_detection = vtk.vtkCollisionDetectionFilter()
        self.collision_detection.SetCollisionModeToAllContacts()
        self.collision_detection.SetInputData(1, self.actor.GetMapper().GetInput())
        # Create a transform for the mesh
        self.mesh_transform = vtk.vtkTransform()
        self.mesh_transform.Identity()

        # Create a transform for the camera
        self.camera_transform = vtk.vtkTransform()
        self.camera_transform.Identity()
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
        """self.markingevent = self.AddObserver(
            "MiddleButtonPressEvent", self.middlebuttonobserver.MiddleButtonPressEvent
        )"""
        self.movement = self.AddObserver("KeyPressEvent", self.KeyPressed)
        self.RemoveObserver(self.addactor)
        self.OnRightButtonDown()

    def check_collision(self):
        # Set the input for collision detection as the camera mesh
        self.collision_detection.SetInputData(0, self.mesh.GetMapper().GetInput())
        self.collision_detection.SetTransform(0, self.mesh_transform)
        self.mesh.SetUserTransform(self.mesh_transform)
        self.collision_detection.SetTransform(1, self.camera_transform)
        self.actor.SetUserTransform(self.camera_transform)
        self.collision_detection.Update()
        num_contacts = self.collision_detection.GetNumberOfContacts()
        print(num_contacts)
        return num_contacts > 0

    # movement controls
    def KeyPressed(self, obj, event):
        key = self.renderwindowinteractors.GetKeySym()
        actor_position = []
        camera_position = []
        self.actor_speed = 10
        camera = self.render.GetActiveCamera()
        # Create a collision detection filter

        for i in range(3):
            actor_position.append(self.actor.GetPosition()[i])
            camera_position.append(self.actor.GetPosition()[i])
        if key == "l":  # reset movement and camera
            self.render.GetActiveCamera().SetPosition(0, -1, 0)
            self.render.GetActiveCamera().SetFocalPoint(0, 0, 0)
            self.render.GetActiveCamera().SetViewUp(0, 0, 1)
            self.render.ResetCamera()
            self.render.RemoveActor(self.actor)
            # Actor speed is reset to 0, indicating no movement.
            self.actor_speed = 0
            self.RemoveObserver(self.movement)
            # self.RemoveObserver(self.markingevent)
            self.AddObserver("RightButtonPressEvent", self.RightButtonPressEvent)
            self.renderwindowinteractors.GetRenderWindow().Render()
            return  # return to its original position
        # default up down left and right control movement only in toilet/no access shower room
        if key == "Up":
            if camera_position[0] < (self.meshbound[1]):
                actor_position[0] += self.actor_speed
                camera_position[0] += self.actor_speed
        elif key == "Down":
            if camera_position[0] > (self.meshbound[0]):
                actor_position[0] -= self.actor_speed
                camera_position[0] -= self.actor_speed
        elif key == "Left":
            if camera_position[1] < (self.meshbound[3]):
                actor_position[1] += self.actor_speed
                camera_position[1] += self.actor_speed
        elif key == "Right":
            if camera_position[1] > (self.meshbound[2]):
                actor_position[1] -= self.actor_speed
                camera_position[1] -= self.actor_speed
        self.actor.SetPosition(actor_position)
        camera.SetPosition(camera_position)
        self.collision_detection.SetInputData(1, self.actor.GetMapper().GetInput())

        if self.check_collision():
            # Move the camera back to its previous position if there's a collision
            if key == "Up":
                actor_position[0] -= self.actor_speed
                camera_position[0] -= self.actor_speed
            elif key == "Down":
                actor_position[0] += self.actor_speed
                camera_position[0] += self.actor_speed
            elif key == "Left":
                actor_position[1] -= self.actor_speed
                camera_position[1] -= self.actor_speed
            elif key == "Left":
                actor_position[1] += self.actor_speed
                camera_position[1] += self.actor_speed
        self.actor.SetPosition(actor_position)

        self.actor.SetOrientation(
            self.defaultposition[0],
            self.defaultposition[1],
            self.defaultposition[2],
        )
        camera.SetPosition(camera_position)
        camera.SetViewUp(
            self.defaultposition[0],
            self.defaultposition[1],
            self.defaultposition[2],
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
