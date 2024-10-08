from PyQt5.QtCore import *
from vtk import *
import PythonApplication.leftbuttoninteractor as leftbuttoninteraction
import PythonApplication.rightclickroominteraction as roominteraction
import PythonApplication.storedisplay as displaystoring
import PythonApplication.wall_identifiers as wallinteraction
import tkinter as tk
from tkinter import messagebox
import time


# insert interactive event for the stl mesh , left click is for moving the stl ,
# right click is to insert the actor in the room view , right click for room interact shower and toilet
# l key is to remove the actor in the room view and set the mesh to the original position
class myInteractorStyle(vtkInteractorStyleTrackballCamera):
    def __init__(
        self, setcamerainteraction, wall_identifiers, localizebutton, ros_node
    ):
        # starting initialize
        super().__init__()
        self.addactor = self.AddObserver(
            "RightButtonPressEvent", self.RightButtonPressEvent
        )
        self.xlabels = setcamerainteraction[0]
        self.ylabels = setcamerainteraction[1]
        self.render = setcamerainteraction[2]
        self.renderwindowinteractor = setcamerainteraction[3]
        self.meshbound = setcamerainteraction[4]
        self.xlabelbefore = setcamerainteraction[5]
        self.ylabelbefore = setcamerainteraction[6]
        self.zlabelbefore = setcamerainteraction[7]
        self.mesh = setcamerainteraction[8]
        self.polys = setcamerainteraction[9]
        self.reader = setcamerainteraction[10]
        self.cubeactor = setcamerainteraction[11]
        self.cameraactor = setcamerainteraction[12]
        self.oldcamerapos = setcamerainteraction[13]
        self.old_actor_position = setcamerainteraction[13]
        self.collisionFilter = setcamerainteraction[14]
        self.spaceseperation = setcamerainteraction[15]
        self.center = setcamerainteraction[16]
        camera = self.render.GetActiveCamera()
        self.actor_speed = 20
        self.threshold = 20
        self.defaultposition = [0, 0, 1]
        self.leftbuttoninteraction = leftbuttoninteraction.LeftInteractorStyle(
            self, setcamerainteraction
        )
        self.old_actor_position = [160, self.center[1], self.center[2]]
        self.default_pos = [160, self.center[1], self.center[2]]
        self.refresh()
        self._translate = QCoreApplication.translate
        self.rightclickinteract = roominteraction.rightclickRoomInteract(
            self,
            setcamerainteraction,
            self.default_pos,
            wall_identifiers,
            localizebutton,
            ros_node,
        )
        self.locator = vtkStaticPointLocator()
        self.locator.SetDataSet(self.reader)
        self.locator.BuildLocator()
        self.wallinteractor = wallinteraction.wall_Interaction(
            self, setcamerainteraction, wall_identifiers, localizebutton, ros_node
        )
        self.displaystore = displaystoring.storage(
            setcamerainteraction, wall_identifiers, localizebutton, ros_node
        )
        self.setkeypreventcontrols()
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
        self.walldatainteraction = self.AddObserver(
            "MiddleButtonPressEvent", self.wallinteractor.setwallinteractiondata
        )
        self.refresh()
        self.OnRightButtonDown()

    # default prevent controls
    def setkeypreventcontrols(self):
        self.disable_up = False
        self.disable_down = False
        self.disable_left = False
        self.disable_right = False

    # movement controls
    def KeyPressed(self, obj, event):
        self.SetMotionFactor(8)
        key = self.GetInteractor().GetKeySym()
        actor_position = []
        delay = 1
        camera = self.render.GetActiveCamera()
        for i in range(3):
            actor_position.append(self.cubeactor.GetPosition()[i])
        if key == "l":  # reset movement and camera
            camera = self.render.GetActiveCamera()
            camera.SetPosition(0, -1, 0)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 0, 1)
            self.render.ResetCameraClippingRange()
            self.render.ResetCamera()
            self.RemoveObserver(self.movement)
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
        if key == "Up" and self.disable_up is False:
            # actor will not go beyond the inside are of the mesh
            if actor_position[0] < (self.meshbound[1]):
                # prevent shape max number
                actor_position[0] += self.actor_speed
                self.setkeypreventcontrols()
                self.setcollision(actor_position, key, camera)
            time.sleep(delay)
        elif key == "Down" and self.disable_down is False:
            if actor_position[0] > (self.meshbound[0]):
                # prevent shape min number
                actor_position[0] -= self.actor_speed
                self.setkeypreventcontrols()
                self.setcollision(actor_position, key, camera)
            time.sleep(delay)
        elif key == "Left" and self.disable_left is False:
            if actor_position[1] < (self.meshbound[3]):
                # prevent shape max number
                actor_position[1] += self.actor_speed
                self.setkeypreventcontrols()
                self.setcollision(actor_position, key, camera)
            time.sleep(delay)
        elif key == "Right" and self.disable_right is False:
            if actor_position[1] > (self.meshbound[2]):
                # prevent shape min number
                actor_position[1] -= self.actor_speed
                self.setkeypreventcontrols()
                self.setcollision(actor_position, key, camera)
            time.sleep(delay)
        self.displaystore.storedisplay()
        self.leftbuttoninteraction.displaytext(camera)

    # set camera orientation
    def camsetvieworientation(self, camera):
        camera.SetViewUp(0, 0, 1)

    def calculate_distance_to_mesh(self, actor_position):
        min_distance = float("inf")
        for i in range(self.reader.GetNumberOfPoints()):
            point = [self.meshbound[1], self.meshbound[3], self.meshbound[5]]
            self.reader.GetPoint(i, point)
            distance = vtkMath.Distance2BetweenPoints(actor_position, point) ** 0.5
            if distance < min_distance:
                min_distance = distance
        return min_distance

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
        distance_to_mesh = self.calculate_distance_to_mesh(actor_position)
        if distance_to_mesh < 100:
            message = f"Warning: Cube actor is within {distance_to_mesh:.2f}mm of a wall. Movement restricted."
            self.show_error_message(message)
            actor_position = self.old_actor_position
        else:
            self.cubeactor.SetPosition(actor_position)
            self.setcameraactor()
            camera.SetPosition(actor_position)
            self.camsetvieworientation(camera)
            self.collisionFilter.Update()
            num_contacts = self.collisionFilter.GetNumberOfContacts()
            if num_contacts == 0:
                self.refresh()
                self.old_actor_position = actor_position
            else:
                message = f"Collision detected. Moving back to previous position. Contact detected: {num_contacts}"
                self.show_error_message(message)
                if key == "Up":
                    self.old_actor_position[0] -= self.actor_speed
                    self.disable_up = True
                elif key == "Down":
                    self.old_actor_position[0] += self.actor_speed
                    self.disable_down = True
                elif key == "Left":
                    self.old_actor_position[1] -= self.actor_speed
                    self.disable_left = True
                elif key == "Right":
                    self.old_actor_position[1] += self.actor_speed
                    self.disable_right = True
                actor_position = self.old_actor_position
        self.cubeactor.SetPosition(actor_position)
        self.setcameraactor()
        camera.SetPosition(actor_position)
        self.refresh()

    # show an error message 
    def show_error_message(self, message):
        root = tk.Tk()
        root.withdraw()  
        messagebox.showerror("Error", message)
        root.destroy()
