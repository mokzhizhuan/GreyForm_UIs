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
        setcamerainteraction,
        default_pos,
        wall_identifiers,
        localizebutton,
        ros_node,
    ):
        # starting initialize
        self.interactor_style = interactor_style
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
        self.default_pos = default_pos
        camera = self.render.GetActiveCamera()
        self.defaultposition = [0, 0, 1]
        self.renderwindowinteractor.GetRenderWindow().Render()
        self._translate = QtCore.QCoreApplication.translate
        self.displaystore = displaystoring.storage(
            setcamerainteraction, wall_identifiers, localizebutton, ros_node
        )
        self.displaytext(camera)

    #teleporter interaction(needed or not needed depending on robot scan)
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

    #text display 
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
