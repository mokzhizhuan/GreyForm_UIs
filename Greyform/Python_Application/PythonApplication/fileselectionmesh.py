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


class FileSelectionMesh(object):
    #load meshdata from file
    def meshdata(self, file_path, viewer , viewer_2, currentSTL):

        stl_mesh = mesh.Mesh.from_file(file_path)
        
        #for ignoring the size of the stl but it will load longer depending on the stl file size
        np.seterr(divide='ignore', invalid='ignore')
        #points and faces 
        points = stl_mesh.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1,3)

        #mesh data insertion
        mesh_data = MeshData(vertexes=points, faces=faces)
        meshs = GLMeshItem(meshdata=mesh_data, smooth=True, drawFaces=True, drawEdges=True, edgeColor=(0, 1, 0, 1))
        currentSTL = meshs
        #add item to viewer
        viewer.addItem(currentSTL)
        viewer.show()
        viewer_2.addItem(currentSTL)
        viewer_2.show()
        
        return currentSTL


        
    