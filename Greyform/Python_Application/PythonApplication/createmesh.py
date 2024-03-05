import sys
from PyQt5 import QtCore, QtWidgets ,QtOpenGL, QtGui , uic
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *  
from PyQt5.QtGui import *
import OpenGL.GL as gl        
from OpenGL import GLU   
from pyqtgraph.opengl import  GLMeshItem 
import pyqtgraph.opengl as gl
import numpy as np
from stl import mesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pyvista as pv
import vtk
from ipywidgets import interact
from pyvistaqt import QtInteractor

class createMesh(QMainWindow):
    def createmesh(CurrentMesh, plotters):
        #mesh data insertion
        func = lambda line: line
        cylinder = pv.Cylinder(resolution=100, center=(100, 300, 47), direction=(0, 0, 1), height=16 , radius=8).triangulate().subdivide(3)
        meshs = pv.read(CurrentMesh)
        plotters.add_mesh(meshs, color=(31, 236, 67), show_edges=True, edge_color="black" ,cmap="terrain", clim=[1,3] ,  name='roombuilding')
        plotters.set_focus(meshs.center)
        plotters.add_mesh(cylinder, color='white' , show_edges=True, edge_color="black")

        ctf = vtk.vtkColorTransferFunction()
        ctf.AddRGBPoint(0,1,0,0)
        ctf.AddRGBPoint(1,0,1,0)
        ctf.AddRGBPoint(2,0,0,1)
        plotters.camera_set = True
        plotters.where_is('roombuilding')
        def my_cpos_callback(*args):
            plotters.add_text(str(plotters.camera_position), name="cpos")
            return
        plotters.iren.add_observer(vtk.vtkCommand.EndInteractionEvent, my_cpos_callback)
        plotters.show_axes()
        
        plotters.show()
        plotters.enable()


    def createmeshsloop(plotters, sequence):
        for i in range(1, sequence):
            cylinder = pv.Cylinder(resolution=100, center=(140, 200, (47-(i*16))), direction=(0, 0, 1), height=16 , radius=8).triangulate().subdivide(3)
            plotters.add_mesh(cylinder, color='white' , show_edges=True)
            plotters.show()

    
