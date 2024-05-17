from PyQt5 import QtCore
from PyQt5.QtCore import *
import vtk
from vtk import *
import math


class LeftInteractorStyle(object):
    def __init__(
        self,
        interactor_style,
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
        camdisplay,
        spaceseperation,
        center,
    ):
        self.interactor_style = interactor_style
        self.cameraactor = cameraactor
        self.xlabels = xlabel
        self.ylabels = ylabel
        self.render = ren
        self.spaceseperation = spaceseperation
        self.renderwindowinteractor = renderwindowinteractor
        self.meshbound = meshbounds
        self.mesh = polydata
        self.polys = polys
        self.reader = reader
        self.cubeactor = cubeactor
        self.defaultposition = [0, 0, 1]
        self.center = center
        self.collisionFilter = vtk.vtkCollisionDetectionFilter()
        self.collisionFilter.SetInputData(0, self.cameraactor.GetMapper().GetInput())
        self.collisionFilter.SetInputData(1, self.mesh.GetMapper().GetInput())
        self.collisionFilter.SetTransform(
            0, vtk.vtkTransform()
        )  # Moving object transform
        self.collisionFilter.SetTransform(
            1, vtk.vtkTransform()
        )  # Static object transform
        self.collisionFilter.SetMatrix(
            0, self.cameraactor.GetMatrix()
        )  # Static object transform
        self.collisionFilter.SetMatrix(
            1, self.mesh.GetMatrix()
        )  # Static object transform
        # Set up the collision filter
        self.collisionFilter.SetCollisionModeToAllContacts()
        self.collisionFilter.GenerateScalarsOn()
        self.leftbuttoninteraction = False
        self.renderwindowinteractor.GetRenderWindow().Render()
        self._translate = QCoreApplication.translate
        self.xlabelbefore = xlabelbefore
        self.ylabelbefore = ylabelbefore
        self.zlabelbefore = zlabelbefore
        self.max_zoom_in_factor = 2.0
        self.min_zoom_out_factor = 0.1
        self.current_zoom_factor = 1.0
        self.last_update_time = 0
        self.update_interval = 0.1  # Update every 0.1 seconds
        self.displayoldpos = camdisplay

    def leftButtonPressEvent(self, obj, event):
        self.leftbuttoninteraction = True
        clickPos = self.renderwindowinteractor.GetEventPosition()  # <<<-----<
        self.displayclickpostext(clickPos)
        self.current_zoom_factor = 1.0
        self.interactor_style.OnLeftButtonDown()

    def mouse_move(self, obj, event):
        clickPos = self.renderwindowinteractor.GetEventPosition()
        if self.leftbuttoninteraction is True:
            self.interactor_style.SetMotionFactor(8)
            self.displayclickpostext(clickPos)
            camera = self.render.GetActiveCamera()
            camera_pos = camera.GetPosition()
            self.cameraactor.SetPosition(camera_pos)
            self.collisionFilter.Update()
            num_contacts = self.collisionFilter.GetNumberOfContacts()
            self.refresh()
            if (
                num_contacts > 0
                or self.meshbound[0] >= camera_pos[0] <= self.meshbound[1]
                or self.meshbound[2] >= camera_pos[1] <= self.meshbound[3]
                or 0 >= camera_pos[2] <= self.meshbound[5]
            ):
                camera.SetPosition(self.cubeactor.GetPosition())
                self.cameraactor.SetPosition(
                    self.cubeactor.GetPosition()[0],
                    self.cubeactor.GetPosition()[1] - self.spaceseperation,
                    self.cubeactor.GetPosition()[2] - self.spaceseperation,
                )
                self.camsetvieworientation(camera)
                self.refresh()
            self.displaytext(camera)
            self.interactor_style.OnMouseMove()

    def left_button_release(self, obj, event):
        self.leftbuttoninteraction = False

    def release(self):
        self.interactor_style.SetMotionFactor(8)
        self.leftbuttoninteraction = False
        camera = self.render.GetActiveCamera()
        camera.SetPosition(self.cubeactor.GetPosition())
        self.setcamposition(camera)
        self.current_zoom_factor = 1.0
        self.camsetvieworientation(camera)
        self.refresh()

    def mouse_wheel_forward(self, obj, event):
        self.interactor_style.SetMotionFactor(1)
        zoom_factor = 1.1
        if self.current_zoom_factor * zoom_factor <= self.max_zoom_in_factor:
            self.current_zoom_factor *= zoom_factor
            camera = self.render.GetActiveCamera()
            position = [
                camera.GetPosition()[0],
                camera.GetPosition()[1],
                camera.GetPosition()[2],
            ]
            focal_point = [
                camera.GetFocalPoint()[0],
                camera.GetFocalPoint()[1],
                camera.GetFocalPoint()[2],
            ]
            camera.Zoom(zoom_factor)  # Zoom out
            dx = position[0] - focal_point[0]
            dy = position[1] - focal_point[1]
            dz = position[2] - focal_point[2]
            current_distance = math.sqrt(dx**2 + dy**2 + dz**2)
            # Calculate the new distance by applying the zoom factor
            new_distance = (
                current_distance / zoom_factor
            )  # Zooming out increases distance
            # The difference in distance moved by the camera
            distance_moved = abs(current_distance - new_distance)
            camera.Zoom(zoom_factor)  # Zoom in
            self.setcamposition(camera)
            self.collisionFilter.Update()
            num_contacts = self.collisionFilter.GetNumberOfContacts()
            self.refresh()
            self.setcollisiondetection(num_contacts, distance_moved, camera)
            self.displaytext(camera)
            self.refresh()
        self.interactor_style.OnMouseWheelForward()

    def mouse_wheel_backward(self, obj, event):
        self.interactor_style.SetMotionFactor(1)
        zoom_factor = 0.99
        if self.current_zoom_factor * zoom_factor >= self.min_zoom_out_factor:
            camera = self.render.GetActiveCamera()
            position = [
                camera.GetPosition()[0],
                camera.GetPosition()[1],
                camera.GetPosition()[2],
            ]
            focal_point = [
                camera.GetFocalPoint()[0],
                camera.GetFocalPoint()[1],
                camera.GetFocalPoint()[2],
            ]
            camera.Zoom(zoom_factor)  # Zoom out
            dx = position[0] - focal_point[0]
            dy = position[1] - focal_point[1]
            dz = position[2] - focal_point[2]
            current_distance = math.sqrt(dx**2 + dy**2 + dz**2)
            # Calculate the new distance by applying the zoom factor
            new_distance = (
                current_distance / zoom_factor
            )  # Zooming out increases distance
            # The difference in distance moved by the camera
            distance_moved = abs(current_distance - new_distance)
            self.current_zoom_factor *= zoom_factor
            self.setcamposition(camera)
            self.collisionFilter.Update()
            num_contacts = self.collisionFilter.GetNumberOfContacts()
            self.refresh()
            self.setcollisiondetection(num_contacts, distance_moved, camera)
            self.displaytext(camera)
            self.refresh()
        self.interactor_style.OnMouseWheelBackward()

    def displayclickpostext(self, clickPos):
        self.xlabels.setText(
            self._translate("MainWindow", str("{0:.2f}".format(clickPos[0])))
        )
        self.ylabels.setText(
            self._translate("MainWindow", str("{0:.2f}".format(clickPos[1])))
        )

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
        self.interactor_style.GetInteractor().GetRenderWindow().Render()

    def setcamposition(self, camera):
        self.cameraactor.SetPosition(
            camera.GetPosition()[0],
            camera.GetPosition()[1] - self.spaceseperation,
            camera.GetPosition()[2] - self.spaceseperation,
        )

    def setcollisiondetection(self, num_contacts, distance_moved, camera):
        camera_pos = [
            camera.GetPosition()[0],
            camera.GetPosition()[1],
            camera.GetPosition()[2],
        ]
        if (
            num_contacts > 0
            or self.meshbound[0] + distance_moved
            <= camera_pos[0]
            >= self.meshbound[1] - distance_moved
            or self.meshbound[2] + distance_moved
            <= camera_pos[1]
            >= self.meshbound[3] - distance_moved
            or self.meshbound[4] + distance_moved
            <= camera_pos[2]
            >= self.meshbound[5] - distance_moved
        ):
            camera.SetPosition(self.cubeactor.GetPosition())
            self.setcamposition(camera)
            self.camsetvieworientation(camera)
            self.current_zoom_factor = 1.0
            camera_pos = camera.GetPosition()
            self.collisionFilter.Update()
            self.refresh()
            self.displaytext(camera)
            return
