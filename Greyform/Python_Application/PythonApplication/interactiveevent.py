from PyQt5 import QtCore
from PyQt5.QtCore import *
import vtk
from vtk import *
import PythonApplication.middlebuttoninteractor as middlebuttoninteractor
import PythonApplication.leftbuttoninteractor as leftbuttoninteraction


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
        cubeactor,
        cameraactor,
        oldcamerapos,
        parent=None,
    ):
        # starting initialize
        self.movement = None
        self.append_filterpolydata = append_filterpolydata
        self.addactor = self.AddObserver(
            "RightButtonPressEvent", self.RightButtonPressEvent
        )
        self.xlabels = xlabel
        self.ylabels = ylabel
        self.render = ren
        self.cameraactor = cameraactor
        camera = self.render.GetActiveCamera()
        self.renderwindowinteractor = renderwindowinteractor
        """self.middlebuttonobserver = middlebuttoninteractor.MiddleButtonPressed(
            self,
            self.render,
            self.renderwindowinteractor,
            append_filterpolydata,
        )  # marking points interaction"""
        self.meshbound = meshbounds
        self.mesh = polydata
        self.polys = polys
        self.reader = reader
        self.actor_speed = 20
        self.cubeactor = cubeactor
        self.defaultposition = [0, 0, 1]
        self.center = [
            (self.meshbound[0] + self.meshbound[1]) / 2,
            (self.meshbound[2] + self.meshbound[3]) / 2,
            (self.meshbound[4] + self.meshbound[5]) / 2,
        ]
        self.oldcamerapos = oldcamerapos
        self.leftbuttoninteraction = leftbuttoninteraction.LeftInteractorStyle(
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
            cubeactor,
            cameraactor,
            self.oldcamerapos,
        )
        self.collisionFilter = vtk.vtkCollisionDetectionFilter()
        # Set up the collision filter
        self.collisionFilter.SetInputData(0, self.cubeactor.GetMapper().GetInput())
        self.collisionFilter.SetInputData(1, self.mesh.GetMapper().GetInput())
        self.collisionFilter.SetTransform(
            0, vtk.vtkTransform()
        )  # Moving object transform
        self.collisionFilter.SetTransform(
            1, vtk.vtkTransform()
        )  # Static object transform
        self.collisionFilter.SetMatrix(
            0, self.cubeactor.GetMatrix()
        )  # Static object transform
        self.collisionFilter.SetMatrix(
            1, self.mesh.GetMatrix()
        )  # Static object transform
        self.old_actor_position = None
        self.collisionFilter.SetCollisionModeToAllContacts()
        self.collisionFilter.GenerateScalarsOn()
        self.renderwindowinteractor.GetRenderWindow().Render()
        self._translate = QtCore.QCoreApplication.translate
        self.xlabelbefore = xlabelbefore
        self.ylabelbefore = ylabelbefore
        self.zlabelbefore = zlabelbefore
        xlabelbefore.setText(
            self._translate(
                "MainWindow", str("{0:.2f}".format(camera.GetPosition()[0]))
            )
        )
        ylabelbefore.setText(
            self._translate(
                "MainWindow", str("{0:.2f}".format(camera.GetPosition()[1]))
            )
        )
        zlabelbefore.setText(
            self._translate(
                "MainWindow", str("{0:.2f}".format(camera.GetPosition()[2]))
            )
        )

    # inside view
    def RightButtonPressEvent(self, obj, event):
        clickPos = self.GetInteractor().GetEventPosition()  # <<<-----<
        self.xlabels.setText(
            self._translate("MainWindow", str("{0:.2f}".format(clickPos[0])))
        )
        self.ylabels.setText(
            self._translate("MainWindow", str("{0:.2f}".format(clickPos[1])))
        )
        camera = self.render.GetActiveCamera()
        self.old_actor_position = [80, self.center[1], self.center[2]]
        camera.SetPosition(self.old_actor_position)
        self.cubeactor.SetPosition(self.old_actor_position)
        camera.SetViewUp(
            self.defaultposition[0], self.defaultposition[1], self.defaultposition[2]
        )
        self.render.SetActiveCamera(camera)  # insert and replace a new camera
        # camera coordinates
        self.xlabelbefore.setText(
            self._translate(
                "MainWindow", str("{0:.2f}".format(camera.GetPosition()[0]))
            )
        )
        self.ylabelbefore.setText(
            self._translate(
                "MainWindow", str("{0:.2f}".format(camera.GetPosition()[1]))
            )
        )
        self.zlabelbefore.setText(
            self._translate(
                "MainWindow", str("{0:.2f}".format(camera.GetPosition()[2]))
            )
        )
        """self.markingevent = self.AddObserver(
            "MiddleButtonPressEvent", self.middlebuttonobserver.MiddleButtonPressEvent
        )"""
        self.movement = self.AddObserver("KeyPressEvent", self.KeyPressed)
        self.mousemovement = self.AddObserver(
            "MouseMoveEvent", self.leftbuttoninteraction.mouse_move
        )
        self.revert_left_position = self.AddObserver(
            "LeftButtonPressEvent", self.leftbuttoninteraction.leftButtonPressEvent
        )
        self.releasemouseclick = self.AddObserver(
            "LeftButtonReleaseEvent", self.leftbuttoninteraction.left_button_release
        )
        self.mousezoomin = self.AddObserver(
            "MouseWheelForwardEvent", self.leftbuttoninteraction.mouse_wheel_forward
        )
        self.mousezoomout = self.AddObserver(
            "MouseWheelBackwardEvent", self.leftbuttoninteraction.mouse_wheel_backward
        )

        self.RemoveObserver(self.addactor)
        self.renderwindowinteractor.GetRenderWindow().Render()
        self.OnRightButtonDown()

    # movement controls
    def KeyPressed(self, obj, event):
        key = self.GetInteractor().GetKeySym()
        actor_position = []
        camera = self.render.GetActiveCamera()
        # Create a collision detection filter
        for i in range(3):
            actor_position.append(self.cubeactor.GetPosition()[i])
        if key == "l":  # reset movement and camera
            self.render.GetActiveCamera().SetPosition(0, -1, 0)
            self.render.GetActiveCamera().SetFocalPoint(0, 0, 0)
            self.render.GetActiveCamera().SetViewUp(0, 0, 1)
            self.render.ResetCamera()
            self.RemoveObserver(self.movement)
            # self.RemoveObserver(self.markingevent)
            self.RemoveObserver(self.mousemovement)
            self.RemoveObserver(self.revert_left_position)
            self.RemoveObserver(self.releasemouseclick)
            self.RemoveObserver(self.mousezoomin)
            self.RemoveObserver(self.mousezoomout)
            self.AddObserver("RightButtonPressEvent", self.RightButtonPressEvent)
            self.render.ResetCameraClippingRange()
            self.renderwindowinteractor.GetRenderWindow().Render()
            return  # return to its original position
        if key == "n":
            self.leftbuttoninteraction.release()
        if key == "Up":
            if actor_position[0] < (self.meshbound[1]):
                actor_position[0] += self.actor_speed
        elif key == "Down":
            if actor_position[0] > (self.meshbound[0]):
                actor_position[0] -= self.actor_speed
        elif key == "Left":
            if actor_position[1] < (self.meshbound[3]):
                actor_position[1] += self.actor_speed
        elif key == "Right":
            if actor_position[1] > (self.meshbound[2]):
                actor_position[1] -= self.actor_speed
        self.cubeactor.SetPosition(actor_position)
        self.cameraactor.SetPosition(self.old_actor_position)
        camera.SetPosition(actor_position)
        camera.SetViewUp(
            self.defaultposition[0],
            self.defaultposition[1],
            self.defaultposition[2],
        )
        self.collisionFilter.Update()
        num_contacts = self.collisionFilter.GetNumberOfContacts()
        if num_contacts == 0:
            self.renderwindowinteractor.GetRenderWindow().Render()
            self.old_actor_position = actor_position
        else:
            if key == "Up":
                self.old_actor_position[0] -= self.actor_speed
            elif key == "Down":
                self.old_actor_position[0] += self.actor_speed
            elif key == "Left":
                self.old_actor_position[1] -= self.actor_speed
            elif key == "Right":
                self.old_actor_position[1] += self.actor_speed
            self.cubeactor.SetPosition(self.old_actor_position)
            self.cameraactor.SetPosition(self.old_actor_position)
            camera.SetPosition(self.old_actor_position)
            actor_position = self.old_actor_position
            self.renderwindowinteractor.GetRenderWindow().Render()
            self.collisionFilter.Update()
        # camera coordinates
        self.storedisplay()
        self.xlabelbefore.setText(
            self._translate(
                "MainWindow", str("{0:.2f}".format(camera.GetPosition()[0]))
            )
        )
        self.ylabelbefore.setText(
            self._translate(
                "MainWindow", str("{0:.2f}".format(camera.GetPosition()[1]))
            )
        )
        self.zlabelbefore.setText(
            self._translate(
                "MainWindow", str("{0:.2f}".format(camera.GetPosition()[2]))
            )
        )

    def storedisplay(self):
        self.oldcamerapos = self.cubeactor.GetPosition()
        myInteractorStyle(
            self.xlabels,
            self.ylabels,
            self.render,
            self.renderwindowinteractor,
            self.meshbound,
            self.xlabelbefore,
            self.ylabelbefore,
            self.zlabelbefore,
            self.mesh,
            self.polys,
            self.reader,
            self.append_filterpolydata,
            self.cubeactor,
            self.cameraactor,
            self.oldcamerapos,
        )
