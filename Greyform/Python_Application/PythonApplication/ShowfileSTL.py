import sys
import os
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
from stl import mesh


class ShowfileSTL(object):
    #file path
    def browsefilesdirectory(self , Selectivefilelistview):
        dirpath = QFileDialog.getExistingDirectory(None,"Choose Directory",os.getcwd())
        model = QFileSystemModel()
        model.setRootPath(dirpath )
        model.setFilter(QDir.NoDotAndDotDot | QDir.Files)
        Selectivefilelistview.setModel(model)
        Selectivefilelistview.setRootIndex(model.index(dirpath))
        Selectivefilelistview.setAlternatingRowColors(True)
