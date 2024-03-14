import sys
from PyQt5 import QtCore, QtWidgets ,QtOpenGL, QtGui , uic
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *  
from PyQt5.QtGui import *
import OpenGL.GL as gl        
from OpenGL import GLU   
from pyqtgraph.opengl import GLViewWidget, MeshData, GLMeshItem 
import pyqtgraph.opengl as gl
import numpy as np
import PythonApplication.createmesh as meshs
from stl import mesh
import pyqtgraph as pg
import trimesh
import pyvista as pv



class loadseqdata(object):
    #when selected how many sequence
    def on_selection_sequence(buttonseq, buttonnextpage , label):     
        dataseqtext = buttonseq.text()
        dataseqtext = dataseqtext.replace("Sequence " , "")
        buttonnextpage.show()
        _translate = QtCore.QCoreApplication.translate
        label.setText(_translate("MainWindow", "Sequence: " + str(dataseqtext)))
        return dataseqtext