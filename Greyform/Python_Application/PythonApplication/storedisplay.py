from PyQt5 import QtCore
from PyQt5.QtCore import *
import PythonApplication.interactiveevent as mainInteraction


# storing variable for refreshing and storing variable that are saved
class storage(object):
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
        cubeactor,
        cameraactor,
        oldcamerapos,
        collisionFilter,
        spaceseperation,
        default_pos,
        center,
    ):
        # starting initialize
        self.movement = None
        self.default_pos = default_pos
        self.spaceseperation = spaceseperation
        self.xlabels = xlabel
        self.ylabels = ylabel
        self.render = ren
        self.cameraactor = cameraactor
        self.renderwindowinteractor = renderwindowinteractor
        self.meshbound = meshbounds
        self.mesh = polydata
        self.polys = polys
        self.reader = reader
        self.actor_speed = 20
        self.cubeactor = cubeactor
        self.defaultposition = [0, 0, 1]
        self.oldcamerapos = oldcamerapos
        self.renderwindowinteractor.GetRenderWindow().Render()
        self._translate = QtCore.QCoreApplication.translate
        self.xlabelbefore = xlabelbefore
        self.ylabelbefore = ylabelbefore
        self.zlabelbefore = zlabelbefore
        self.collisionFilter = collisionFilter
        self.center = center

    def storedisplay(self):
        self.oldcamerapos = [
            self.cubeactor.GetPosition()[0],
            self.cubeactor.GetPosition()[1],
            self.cubeactor.GetPosition()[2],
        ]
        self.maininteractor = mainInteraction.myInteractorStyle(
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
            self.cubeactor,
            self.cameraactor,
            self.oldcamerapos,
            self.collisionFilter,
            self.spaceseperation,
            self.center,
        )
