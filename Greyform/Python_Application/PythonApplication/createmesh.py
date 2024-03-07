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
import pandas as pd
import cv2
from vtk import *
from vtk import vtkUnstructuredGridReader

class createMesh(QMainWindow):
    def createmesh(CurrentMesh, plotters):
        if plotters:
            plotters.clear()
        
        #mesh data insertion
        cylinder = pv.Cylinder(resolution=100, center=(60, 140, 471), direction=(0, 0, 1), height=16 , radius=8).triangulate().subdivide(3)
        

        polydata = pv.read(CurrentMesh)
        plotters.add_mesh(polydata, color=(230, 230, 250), show_edges=True, edge_color=(128,128,128) ,cmap="terrain", clim=[1,3] ,  name='roombuilding', opacity="linear")
        plotters.set_focus(polydata.center)
        plotters.add_mesh(cylinder , pickable = False)
        #actor.SetVisibility(False)
        def callback(actor):
            plotters.set_focus(cylinder.points[0])
        plotters.allow_quit_keypress = False
        plotters.clear_events_for_key('q')
        plotters.show_axes()
        label_actor = plotters.add_point_labels([cylinder.points[0]], [""], point_size=20, font_size=36, pickable=False)
        plotters.remove_actor(label_actor)
        plotters.add_actor(label_actor, reset_camera=False, name='label', pickable=True)

        plotters.enable_mesh_picking(callback(label_actor))
        def my_cpos_callback(*args):
            plotters.add_text(str(plotters.camera_position), name="cpos")
            return

        plotters.iren.add_observer(vtk.vtkCommand.EndInteractionEvent, my_cpos_callback)
        plotters.show()


    def createmeshsloop(plotters, sequence):
        for i in range(1, sequence):
            cylinder = pv.Cylinder(resolution=100, center=(140, 200, (47-(i*16))), direction=(0, 0, 1), height=16 , radius=8).triangulate().subdivide(3)
            plotters.add_mesh(cylinder, color='white' , show_edges=True)
            plotters.show()

    
