from PyQt5 import QtCore
from PyQt5.QtCore import *
import vtk
from vtk import *


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
    ):
        self.movement = None
        self.interactor_style = interactor_style
        self.cameraactor = cameraactor
        self.xlabels = xlabel
        self.ylabels = ylabel
        self.render = ren
        self.renderwindowinteractor = renderwindowinteractor
        self.meshbound = meshbounds
        self.mesh = polydata
        self.polys = polys
        self.reader = reader
        self.cubeactor = cubeactor
        self.defaultposition = [0, 0, 1]
        self.center = [
            (self.meshbound[0] + self.meshbound[1]) / 2,
            (self.meshbound[2] + self.meshbound[3]) / 2,
            (self.meshbound[4] + self.meshbound[5]) / 2,
        ]
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
        self._translate = QtCore.QCoreApplication.translate
        self.xlabelbefore = xlabelbefore
        self.ylabelbefore = ylabelbefore
        self.zlabelbefore = zlabelbefore
        self.max_zoom_in_factor = 2.0  # Adjust based on trial or calculation
        self.min_zoom_out_factor = 0.9  # Adjust based on trial or calculation
        self.current_zoom_factor = 1.0
        self.last_update_time = 0
        self.update_interval = 0.1  # Update every 0.1 seconds
        self.displayoldpos = camdisplay

    def leftButtonPressEvent(self, obj, event):
        self.leftbuttoninteraction = True
        clickPos = self.renderwindowinteractor.GetEventPosition()  # <<<-----<
        self.xlabels.setText(
            self._translate("MainWindow", str("{0:.2f}".format(clickPos[0])))
        )
        self.ylabels.setText(
            self._translate("MainWindow", str("{0:.2f}".format(clickPos[1])))
        )
        self.current_zoom_factor = 1.0
        self.interactor_style.OnLeftButtonDown()

    def mouse_move(self, obj, event):
        if self.leftbuttoninteraction is True:
            camera = self.render.GetActiveCamera()
            camera_pos = camera.GetPosition()
            self.cameraactor.SetPosition(camera_pos)
            self.collisionFilter.Update()
            num_contacts = self.collisionFilter.GetNumberOfContacts()
            self.renderwindowinteractor.GetRenderWindow().Render()
            if (
                num_contacts > 0
                or self.meshbound[0] + 70 >= camera_pos[0] <= self.meshbound[1] - 70
                or self.meshbound[2] + 70 >= camera_pos[1] <= self.meshbound[3] - 70
                or 0 >= camera_pos[2] <= self.meshbound[5] - 70
            ):
                camera.SetPosition(self.cubeactor.GetPosition())
                self.cameraactor.SetPosition(self.cubeactor.GetPosition())
                camera.SetViewUp(
                    self.defaultposition[0],
                    self.defaultposition[1],
                    self.defaultposition[2],
                )
                self.render.ResetCameraClippingRange()
                self.renderwindowinteractor.GetRenderWindow().Render()
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
            self.interactor_style.OnMouseMove()

    def left_button_release(self, obj, event):
        self.leftbuttoninteraction = False

    def release(self):
        self.leftbuttoninteraction = False
        camera = self.render.GetActiveCamera()
        camera.SetPosition(self.displayoldpos)
        camera.SetViewUp(
            self.defaultposition[0],
            self.defaultposition[1],
            self.defaultposition[2],
        )
        self.render.ResetCameraClippingRange()
        self.renderwindowinteractor.GetRenderWindow().Render()

    def mouse_wheel_forward(self, obj, event):
        if self.current_zoom_factor * 1.02 <= self.max_zoom_in_factor:
            self.current_zoom_factor *= 1.02
            camera = self.render.GetActiveCamera()
            camera.Zoom(1.02)  # Zoom in
            camera_pos = camera.GetPosition()
            self.xlabelbefore.setText(
                self._translate("MainWindow", str("{0:.2f}".format(camera_pos[0])))
            )
            self.ylabelbefore.setText(
                self._translate("MainWindow", str("{0:.2f}".format(camera_pos[1])))
            )
            self.zlabelbefore.setText(
                self._translate("MainWindow", str("{0:.2f}".format(camera_pos[2])))
            )
        self.interactor_style.OnMouseWheelForward()

    def mouse_wheel_backward(self, obj, event):
        if self.current_zoom_factor * 0.98 >= self.min_zoom_out_factor:
            camera = self.render.GetActiveCamera()
            camera.Zoom(0.98)  # Zoom out
            self.current_zoom_factor *= 0.98
            camera_pos = camera.GetPosition()
            self.renderwindowinteractor.GetRenderWindow().Render()
            if (
                self.meshbound[0] >= camera_pos[0]
                or self.meshbound[2] >= camera_pos[1]
                or self.meshbound[4] >= camera_pos[2]
            ):
                camera.SetPosition(self.cubeactor.GetPosition())
                camera.SetViewUp(
                    self.defaultposition[0],
                    self.defaultposition[1],
                    self.defaultposition[2],
                )
                self.current_zoom_factor = 1.0
                camera_pos = camera.GetPosition()
                self.collisionFilter.Update()
                self.render.ResetCameraClippingRange()
                self.renderwindowinteractor.GetRenderWindow().Render()
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
        self.interactor_style.OnMouseWheelBackward()
