from PyQt5 import QtCore
from PyQt5.QtCore import *
import PythonApplication.interactiveevent as mainInteraction


# storing variable for refreshing and storing variable that are saved
class storage(object):
    def __init__(self, setcamerainteraction):
        # starting initialize
        self.setcamerainteraction = setcamerainteraction
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

    def storedisplay(self):
        self.oldcamerapos = [
            self.cubeactor.GetPosition()[0],
            self.cubeactor.GetPosition()[1],
            self.cubeactor.GetPosition()[2],
        ]
        self.maininteractor = mainInteraction.myInteractorStyle(
            self.setcamerainteraction
        )
