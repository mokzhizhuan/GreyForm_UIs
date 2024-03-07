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
from stl import mesh
import pyqtgraph as pg
import trimesh
import pyvista as pv


class FileSelectionMesh(object):
    #load meshdata from file
    def meshdata(file_path, plotterloader , plotterloader_2):
        #clear mesh
        plotterloader.clear()
        plotterloader_2.clear()

        #load mesh
        meshsplot = pv.read(file_path)
        plotterloader.add_mesh(meshsplot, color=(230, 230, 250), show_edges=True, edge_color=(128,128,128) ,cmap="terrain", clim=[1,3] ,  name='roombuilding', opacity="linear")
        plotterloader_2.add_mesh(meshsplot, color=(230, 230, 250), show_edges=True, edge_color=(128,128,128) ,cmap="terrain", clim=[1,3] ,  name='roombuilding', opacity="linear")


        #show Frame
        plotterloader.show()
        plotterloader_2.show()


        
    