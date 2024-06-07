from PyQt5.QtCore import *
from vtk import *
import PythonApplication.middlebuttoninteractor as middlebuttoninteractor
import PythonApplication.leftbuttoninteractor as leftbuttoninteraction
import PythonApplication.rightclickroominteraction as roominteraction
import PythonApplication.storedisplay as displaystoring
import tkinter as tk
from tkinter import messagebox


# insert interactive event for the stl mesh , left click is for moving the stl ,
# right click is to insert the actor in the room view , right click for room interact shower and toilet
# middle click is to insert an object tht was marked
# l key is to remove the actor in the room view and set the mesh to the original position
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
        center,
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
        self.center = center
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
            center,
        )
        self.old_actor_position = [80, self.center[1], self.center[2]]
        self.default_pos = [80, self.center[1], self.center[2]]
        self.collisionFilter = collisionFilter
        self.old_actor_position = oldcamerapos
        self.refresh()
        self._translate = QCoreApplication.translate
        self.xlabelbefore = xlabelbefore
        self.ylabelbefore = ylabelbefore
        self.zlabelbefore = zlabelbefore
        self.rightclickinteract = roominteraction.rightclickRoomInteract(
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
            self.collisionFilter,
            spaceseperation,
            self.default_pos,
            center,
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
            center,
        )
        self.leftbuttoninteraction.displaytext(camera)

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
        self.leftbuttoninteraction.displaytext(camera)
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
        self.SetMotionFactor(8)
        key = self.GetInteractor().GetKeySym()
        actor_position = []
        camera = self.render.GetActiveCamera()
        for i in range(3):
            actor_position.append(self.cubeactor.GetPosition()[i])
        if key == "l":  # reset movement and camera
            # Set up the camera
            camera = self.render.GetActiveCamera()
            camera.SetPosition(0, -(self.meshbound[2] * 3), 0)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 0, 1)
            self.render.ResetCamera()
            camera.SetPosition(0, -(self.meshbound[3] * 3), self.meshbound[5] * 2)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 0, 1)
            self.render.ResetCameraClippingRange()
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
            self.renderwindowinteractor.GetRenderWindow().Render()
            return  # return to its original position
        if key == "n":
            self.leftbuttoninteraction.release()
        elif key == "m":
            self.leftbuttoninteraction.reset(self.default_pos)
        if key == "Up":
            # actor will not go beyond the inside are of the mesh
            if actor_position[0] < (
                self.meshbound[1] - self.actor_speed * 2
            ):  # prevent shape max number
                actor_position[0] += self.actor_speed
                self.setcollision(actor_position, key, camera)
        elif key == "Down":
            if actor_position[0] > (
                self.meshbound[0] + self.actor_speed * 2
            ):  # prevent shape min number
                actor_position[0] -= self.actor_speed
                self.setcollision(actor_position, key, camera)
        elif key == "Left":
            if actor_position[1] < (
                self.meshbound[3] - self.actor_speed * 2
            ):  # prevent shape max number
                actor_position[1] += self.actor_speed
                self.setcollision(actor_position, key, camera)
        elif key == "Right":
            if actor_position[1] > (
                self.meshbound[2] + self.actor_speed * 2
            ):  # prevent shape min number
                actor_position[1] -= self.actor_speed
                self.setcollision(actor_position, key, camera)
        self.displaystore.storedisplay()
        self.leftbuttoninteraction.displaytext(camera)

    # set camera orientation
    def camsetvieworientation(self, camera):
        camera.SetViewUp(0, 0, 1)

    # refresher
    def refresh(self):
        self.render.ResetCameraClippingRange()
        self.renderwindowinteractor.GetRenderWindow().Render()

    # set cam for refresh
    def setcameraactor(self):
        self.cameraactor.SetPosition(
            self.old_actor_position[0],
            self.old_actor_position[1] - self.spaceseperation,
            self.old_actor_position[2] - self.spaceseperation,
        )

    # set collision for the actor to prevent moving the mesh to the outside area
    def setcollision(self, actor_position, key, camera):
        self.cubeactor.SetPosition(actor_position)
        self.setcameraactor()
        camera.SetPosition(actor_position)
        self.camsetvieworientation(camera)
        self.collisionFilter.Update()
        num_contacts = self.collisionFilter.GetNumberOfContacts()
        if num_contacts == 0:
            self.refresh()
            self.old_actor_position = actor_position
        elif num_contacts > 0 and num_contacts <= 8 :
            messege = f"collision detected , camera actor is stuck moving back to the original position"
            self.show_error_message(messege)
            self.leftbuttoninteraction.reset(self.default_pos)
        else:
            messege = f"collision detected. Moving back to previous position. Collision Contact detected {num_contacts}"
            self.show_error_message(messege)
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

    # Use Tkinter to show an error message
    def show_error_message(self, message):
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showerror("Error", message)
        root.destroy()
