from PyQt5 import QtCore
from PyQt5.QtCore import *
import PythonApplication.interactiveevent as mainInteraction


# storing variable for refreshing and storing variable that are saved
class storage(object):
    def __init__(
        self, setcamerainteraction, wall_identifiers, localizebutton
    ):
        # starting initialize
        super().__init__()
        self.setcamerainteraction = setcamerainteraction
        self.wall_identifiers = wall_identifiers
        self.localizebutton = localizebutton
        self.cubeactor = setcamerainteraction[11]

    def storedisplay(self):
        self.oldcamerapos = [
            self.cubeactor.GetPosition()[0],
            self.cubeactor.GetPosition()[1],
            self.cubeactor.GetPosition()[2],
        ]
        self.maininteractor = mainInteraction.myInteractorStyle(
            self.setcamerainteraction,
            self.wall_identifiers,
            self.localizebutton,
        )
