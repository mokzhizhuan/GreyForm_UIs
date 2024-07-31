from PyQt5 import QtCore
from PyQt5.QtCore import *
import vtk
from vtk import *
import PythonApplication.storedisplay as displaystoring


# interaction with room based on the cell picker
class rightclickRoomInteract(object):
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
        append_filterpolydata,
        cubeactor,
        cameraactor,
        oldcamerapos,
        collisionFilter,
        spaceseperation,
        default_pos,
        center,
    ):
        # starting initialize
        self.interactor_style = interactor_style
        self.default_pos = default_pos
        self.spaceseperation = spaceseperation
        self.append_filterpolydata = append_filterpolydata
        self.xlabels = xlabel
        self.ylabels = ylabel
        self.render = ren
        self.cameraactor = cameraactor
        camera = self.render.GetActiveCamera()
        self.renderwindowinteractor = renderwindowinteractor
        self.meshbound = meshbounds
        self.mesh = polydata
        self.polys = polys
        self.reader = reader
        self.cubeactor = cubeactor
        self.center = center
        self.defaultposition = [0, 0, 1]
        self.center = [
            (self.meshbound[0] + self.meshbound[1]) / 2,
            (self.meshbound[2] + self.meshbound[3]) / 2,
            (self.meshbound[4] + self.meshbound[5]) / 2,
        ]
        self.oldcamerapos = oldcamerapos
        self.renderwindowinteractor.GetRenderWindow().Render()
        self._translate = QtCore.QCoreApplication.translate
        self.xlabelbefore = xlabelbefore
        self.ylabelbefore = ylabelbefore
        self.zlabelbefore = zlabelbefore
        self.collisionFilter = collisionFilter
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
            center
        )
        self.displaytext(camera)

    def click_event(self, obj, event):
        self.interactor_style.SetMotionFactor(8)
        click_pos = self.renderwindowinteractor.GetEventPosition()
        picker = vtk.vtkCellPicker()
        self.renderwindowinteractor.GetRenderWindow().GetInteractor().SetPicker(picker)
        picker.Pick(click_pos[0], click_pos[1], 0, self.render)
        picked_position = [
            picker.GetPickPosition()[0],
            picker.GetPickPosition()[1],
            picker.GetPickPosition()[2],
        ]
        if picked_position[0] <= self.default_pos[0]:
            picked_position[0] = self.default_pos[0]
        camera = self.render.GetActiveCamera()
        camera.SetPosition(picked_position[0], self.center[1], self.center[2])
        self.cubeactor.SetPosition(picked_position[0], self.center[1], self.center[2])
        self.cameraactor.SetPosition(
            picked_position[0],
            self.center[1] - self.spaceseperation,
            self.center[2] - self.spaceseperation,
        )
        camera.SetViewUp(
            self.defaultposition[0], self.defaultposition[1], self.defaultposition[2]
        )
        self.render.SetActiveCamera(camera)
        self.collisionFilter.Update()
        self.displaystore.storedisplay()
        self.render.ResetCameraClippingRange()
        self.renderwindowinteractor.GetRenderWindow().Render()
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
