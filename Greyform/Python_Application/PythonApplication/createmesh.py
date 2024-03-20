from PyQt5 import QtCore, QtWidgets ,QtOpenGL, QtGui , uic
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *  
from PyQt5.QtGui import *
import vtk
from ipywidgets import interact
from vtk import *
import ifcopenshell
import ifcopenshell.geom
from ifcopenshell.util.placement import get_local_placement
import multiprocessing
from vtkmodules.vtkCommonColor import vtkNamedColors
import PythonApplication.progressBarvtk as progressvtk

class createMesh(QMainWindow):
    def __init__(self):
        self.reader = None
        self.bathview = None
        self.showerview = None
        self.meshbounds = None

    #vtkrenderwindow
    def createmesh(self, CurrentMesh, renderwindowinteractor , ylabel , xlabel, xlabelbefore, ylabelbefore, zlabelbefore):
        ren = vtk.vtkRenderer()
        renderwindowinteractor.GetRenderWindow().SetMultiSamples(0)
        renderwindowinteractor.GetRenderWindow().AddRenderer(ren)
        self.renderwindowinteractor = renderwindowinteractor
        ren.UseHiddenLineRemovalOn()
        if "ifc" in CurrentMesh:
            polydataverts, polydatafaces = createMesh.loadmeshinGLView(self, CurrentMesh)
            polydata = vtkPolyData()
            polydata.SetPoints(polydataverts)
            polydata.SetPolys(polydatafaces)
        else:
            progressbarprogram = progressvtk.pythonProgressBar(60000, CurrentMesh, ren, renderwindowinteractor, xlabelbefore, ylabelbefore,  zlabelbefore,xlabel , ylabel)
            progressbarprogram.exec_()
            
    #load mesh in GLViewWidget
    def loadmeshinGLView(self, file_path):
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
                    return grouped_verts , grouped_faces

    
    def polyDataToActor(self, polydata):
        """Wrap the provided vtkPolyData object in a mapper and an actor, returning
    the actor."""
        mapper = vtk.vtkPolyDataMapper()
        if vtk.VTK_MAJOR_VERSION <= 5:
            mapper.SetInput(self.reader.GetOutput())
            mapper.SetInput(polydata)
        else:
            mapper.SetInputConnection(self.reader.GetOutputPort())
        actor = vtk.vtkActor()
        surface_filter = vtk.vtkDataSetSurfaceFilter()
        surface_filter.SetInputConnection(self.reader.GetOutputPort())
        surface_filter.Update()
        decimate = vtk.vtkDecimatePro()
        decimate.SetInputConnection(surface_filter.GetOutputPort())
        # Set the desired reduction factor or target number of polygons
        decimate.SetTargetReduction(0.9)  # Example: reduce mesh to 10% of original size
        decimate.PreserveTopologyOn()  # Preserve topology
        decimate.Update()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToSurface()
        self.meshbounds = []
        for i in range(6):
            self.meshbounds.append(actor.GetBounds()[i])
        #color RGB must be /255 for Red, green , blue color code
        actor.GetProperty().SetColor((230/255),(230/255), (250/255))
        actor.GetProperty().SetDiffuse(0.8)
        actor.GetProperty().BackfaceCullingOn()
        colorsd = vtkNamedColors()
        actor.GetProperty().SetDiffuseColor(colorsd.GetColor3d('LightSteelBlue'))
        actor.GetProperty().SetSpecular(0.3)
        actor.GetProperty().SetSpecularPower(60.0)
        return actor
    
    def closeEvent(self, event):
        super().closeEvent(QCloseEvent)
        self.renderwindowinteractor.GetRenderWindow().MakeCurrent()
        self.renderwindowinteractor.Finalize()     ############################ important
        self.renderwindowinteractor.GetRenderWindow().ClearInRenderStatus()
        self.renderwindowinteractor.GetRenderWindow().RemoveAllObservers()
        self.renderwindowinteractor.GetRenderWindow().Finalize()
        self.renderwindowinteractor.GetRenderWindow().GetInteractor().TerminateApp()




    
