from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import vtk
from vtk import *
from vtkmodules.vtkCommonColor import vtkNamedColors
import PythonApplication.progressBarvtk as progressvtk


# create the imported stl mesh in vtk frame
class createMesh(QMainWindow):
    def __init__(self):
        self.reader = None
        self.meshbounds = None

    # vtkrenderwindow
    def createmesh(
        self,
        ren,
        CurrentMesh,
        renderwindowinteractor,
        ylabel,
        xlabel,
        xlabelbefore,
        ylabelbefore,
        zlabelbefore,
        append_filterpolydata,
    ):
        renderwindowinteractor.GetRenderWindow().SetMultiSamples(0)
        renderwindowinteractor.GetRenderWindow().AddRenderer(ren)
        ren.UseHiddenLineRemovalOn()
        # Check if the render window has been rendered
        rendered = renderwindowinteractor.GetRenderWindow().GetNeverRendered()
        if rendered:
            progressbarprogram = progressvtk.pythonProgressBar(
                60000,
                CurrentMesh,
                ren,
                renderwindowinteractor,
                xlabelbefore,
                ylabelbefore,
                zlabelbefore,
                xlabel,
                ylabel,
                append_filterpolydata,
            )
            progressbarprogram.exec_()
        else:
            return
