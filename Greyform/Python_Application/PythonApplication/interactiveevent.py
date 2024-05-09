from PyQt5.QtCore import *
from vtk import *
import PythonApplication.middlebuttoninteractor as middlebuttoninteractor
import PythonApplication.leftbuttoninteractor as leftbuttoninteraction
import PythonApplication.rightclickroominteraction as roominteraction
import PythonApplication.storedisplay as displaystoring


# insert interactive event for the stl mesh , left click is for moving the stl ,
# right click is to insert the actor in the room view , right click for room interact shower and toilet
# middle click is to insert an object tht was marked
# l key is to remove the actor in the room view and set the mesh to the original position
# m Key is to restore moving position <br>
class myInteractorStyle(vtkInteractorStyleTrackballCamera):
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
        collisionFilter,
        spaceseperation,
        parent=None,
    ):
        # starting initialize
        self.append_filterpolydata = append_filterpolydata
        self.addactor = self.AddObserver(
            "RightButtonPressEvent", self.RightButtonPressEvent
        )
        self.spaceseperation = spaceseperation
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
            spaceseperation,
        )
        self.old_actor_position = [80, self.center[1], self.center[2]]
        self.default_pos = [80, self.center[1], self.center[2]]
        self.collisionFilter = collisionFilter
        self.collisionFilter.Update()
        self.old_actor_position = oldcamerapos
        self.collisionFilter.SetCollisionModeToAllContacts()
        self.collisionFilter.GenerateScalarsOn()
        self.renderwindowinteractor.GetRenderWindow().Render()
        self._translate = QCoreApplication.translate
        self.xlabelbefore = xlabelbefore
        self.ylabelbefore = ylabelbefore
        self.zlabelbefore = zlabelbefore
        self.rightclickinteract = roominteraction.rightclickRoomInteract(
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
            self.collisionFilter,
            spaceseperation,
            self.default_pos,
        )
        self.displaystore = displaystoring.storage(
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
            self.collisionFilter,
            spaceseperation,
            self.default_pos,
        )
        self.displaytext(camera)

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
        camera.SetPosition(self.old_actor_position)
        self.cubeactor.SetPosition(self.old_actor_position)
        self.camsetvieworientation(camera)
        self.render.SetActiveCamera(camera)  # insert and replace a new camera
        # camera coordinates
        self.displaytext(camera)
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
        self.interactionsroom = self.AddObserver(
            "RightButtonPressEvent", self.rightclickinteract.click_event
        )
        self.refresh()
        self.OnRightButtonDown()

    # movement controls
    def KeyPressed(self, obj, event):
        key = self.GetInteractor().GetKeySym()
        actor_position = []
        camera = self.render.GetActiveCamera()
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
            self.RemoveObserver(self.interactionsroom)
            self.addactor = self.AddObserver(
                "RightButtonPressEvent", self.RightButtonPressEvent
            )
            self.refresh()
            return  # return to its original position
        if key == "n":
            self.leftbuttoninteraction.release()
        if key == "Up":
            if actor_position[0] < (
                self.meshbound[1] - self.actor_speed
            ):  # prevent shape max number
                actor_position[0] += self.actor_speed
        elif key == "Down":
            if actor_position[0] > (
                self.meshbound[0] + self.actor_speed
            ):  # prevent shape min number
                actor_position[0] -= self.actor_speed
        elif key == "Left":
            if actor_position[1] < (
                self.meshbound[3] - self.actor_speed
            ):  # prevent shape max number
                actor_position[1] += self.actor_speed
        elif key == "Right":
            if actor_position[1] > (
                self.meshbound[2] + self.actor_speed
            ):  # prevent shape min number
                actor_position[1] -= self.actor_speed
        self.cubeactor.SetPosition(actor_position)
        self.setcameraactor()
        camera.SetPosition(actor_position)
        self.camsetvieworientation(camera)
        self.collisionFilter.Update()
        num_contacts = self.collisionFilter.GetNumberOfContacts()
        if num_contacts == 0:
            self.refresh()
            self.old_actor_position = actor_position
            self.setcameraactor()
        else:
            self.old_actor_position = [
                self.cubeactor.GetPosition()[0],
                self.cubeactor.GetPosition()[1],
                self.cubeactor.GetPosition()[2],
            ]
            if key == "Up":
                self.old_actor_position[0] -= self.actor_speed * 2
            elif key == "Down":
                self.old_actor_position[0] += self.actor_speed * 2
            elif key == "Left":
                self.old_actor_position[1] -= self.actor_speed * 2
            elif key == "Right":
                self.old_actor_position[1] += self.actor_speed * 2
            self.cubeactor.SetPosition(self.old_actor_position)
            self.setcameraactor()
            camera.SetPosition(self.old_actor_position)
            actor_position = self.old_actor_position
            self.refresh()
            self.collisionFilter.Update()
        # camera coordinates
        self.displaystore.storedisplay()
        self.displaytext(camera)

    def displaytext(self, camera):
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

    def camsetvieworientation(self, camera):
        camera.SetViewUp(
            self.defaultposition[0],
            self.defaultposition[1],
            self.defaultposition[2],
        )

    def refresh(self):
        self.render.ResetCameraClippingRange()
        self.renderwindowinteractor.GetRenderWindow().Render()

    def setcameraactor(self):
        self.cameraactor.SetPosition(
            self.old_actor_position[0],
            self.old_actor_position[1] - self.spaceseperation,
            self.old_actor_position[2] - self.spaceseperation,
        )
