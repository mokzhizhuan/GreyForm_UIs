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
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element as Element
from ifcopenshell.util.placement import get_local_placement
import multiprocessing


class FileSelectionMesh(object):
    #load meshdata from file
    def meshdata(file_path, plotterloader , plotterloader_2):
        #clear mesh
        plotterloader.clear()
        plotterloader_2.clear()
        if "ifc" in file_path:
            try:
                ifc_file = ifcopenshell.open(file_path)
            except:
                print(ifcopenshell.get_log())
            else:
                settings = ifcopenshell.geom.settings()
                iterator = ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count())
                if iterator.initialize():
                    while True:
                        shape = iterator.get()
                        element = ifc_file.by_guid(shape.guid)
                        faces = shape.geometry.faces # Indices of vertices per triangle face e.g. [f1v1, f1v2, f1v3, f2v1, f2v2, f2v3, ...]
                        verts = shape.geometry.verts # X Y Z of vertices in flattened list e.g. [v1x, v1y, v1z, v2x, v2y, v2z, ...]
                        materials = shape.geometry.materials # Material names and colour style information that are relevant to this shape
                        material_ids = shape.geometry.material_ids # Indices of material applied per triangle face e.g. [f1m, f2m, ...]

                        # Since the lists are flattened, you may prefer to group them per face like so depending on your geometry kernel
                        grouped_verts = [[verts[i], verts[i + 1], verts[i + 2]] for i in range(0, len(verts), 3)]
                        grouped_faces = [[faces[i], faces[i + 1], faces[i + 2]] for i in range(0, len(faces), 3)]
                        if not iterator.next():
                            break
                        shape = pv.PolyData(grouped_verts , grouped_faces)
                        shape.plot(show_edges=True, line_width=5)
                        plotterloader.add_mesh(shape, color=(230, 230, 250), show_edges=True, edge_color=(128,128,128) ,cmap="terrain", clim=[1,3] ,  name='roombuilding', opacity="linear")
                        plotterloader_2.add_mesh(shape, color=(230, 230, 250), show_edges=True, edge_color=(128,128,128) ,cmap="terrain", clim=[1,3] ,  name='roombuilding', opacity="linear")
                        plotterloader.show()
                        plotterloader_2.show()
        else:
            #load mesh
            meshsplot = pv.read(file_path)
            plotterloader.add_mesh(meshsplot, color=(230, 230, 250), show_edges=True, edge_color=(128,128,128) ,cmap="terrain", clim=[1,3] ,  name='roombuilding', opacity="linear")
            plotterloader_2.add_mesh(meshsplot, color=(230, 230, 250), show_edges=True, edge_color=(128,128,128) ,cmap="terrain", clim=[1,3] ,  name='roombuilding', opacity="linear")
            #show Frame
            plotterloader.show()
            plotterloader_2.show()


        
    