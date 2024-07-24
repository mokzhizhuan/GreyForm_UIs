from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import vtk
from vtk import *
from vtkmodules.vtkCommonColor import vtkNamedColors
import numpy as np
from stl import mesh
import gc
import PythonApplication.interactiveevent as events


# create the imported stl mesh in vtk frame
class createMesh(QMainWindow):
    def __init__(
        self,
        ren,
        polydata,
        renderwindowinteractor,
        ylabel,
        xlabel,
        xlabelbefore,
        ylabelbefore,
        zlabelbefore,
        append_filterpolydata,
    ):
        # variable for loading bar ui
        self.defaultposition = [0, 0, 1]
        self.reader = vtk.vtkPolyData()
        self.meshbounds = None
        self.polydata = polydata
        self.ren = ren
        self.renderwindowinteractor = renderwindowinteractor
        self.renderwindowinteractor.GetRenderWindow().AddRenderer(self.ren)
        self.xlabelbefore = xlabelbefore
        self.ylabelbefore = ylabelbefore
        self.zlabelbefore = zlabelbefore
        self.xlabels = xlabel
        self.ylabels = ylabel
        self.append_filterpolydata = append_filterpolydata
        self.ren.SetBackground(1, 1, 1)
        self.renderwindowinteractor.GetRenderWindow().SetMultiSamples(0)
        self.ren.UseHiddenLineRemovalOn()
        self.loadStl()

    def addfeatureEdges(self):
        featureEdges = vtkFeatureEdges()
        featureEdges.SetInputData(self.reader)
        featureEdges.BoundaryEdgesOn()
        featureEdges.FeatureEdgesOff()
        featureEdges.ManifoldEdgesOff()
        featureEdges.NonManifoldEdgesOff()
        featureEdges.ColoringOn()
        featureEdges.Update()

        # Visualize
        edgeMapper = vtkPolyDataMapper()
        edgeMapper.SetInputConnection(featureEdges.GetOutputPort())
        edgeActor = vtkActor()
        edgeActor.SetMapper(edgeMapper)
        return edgeActor


    def loadStl(self):
        """Load the given STL file, and return a vtkPolyData object for it."""
        meshs = mesh.Mesh.from_file(self.polydata)
        shape = meshs.points.shape
        points = meshs.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)
        # Create VTK Points
        vtk_points = vtk.vtkPoints()
        for vertex in points:
            vtk_points.InsertNextPoint(vertex)
        # Create VTK CellArray
        vtk_faces = vtk.vtkCellArray()
        for face in faces:
            # Create VTK Polygon (assuming all faces are polygons)
            polygon = vtk.vtkPolygon()
            for vertex_index in face:
                polygon.GetPointIds().InsertNextId(vertex_index)
            vtk_faces.InsertNextCell(polygon)
        self.reader.SetPoints(vtk_points)
        self.reader.SetPolys(vtk_faces)
        self.polyDataToActor()
        self.fixedposition()
        center = [
            (self.meshbounds[0] + self.meshbounds[1]) / 2,
            (self.meshbounds[2] + self.meshbounds[3]) / 2,
            (self.meshbounds[4] + self.meshbounds[5]) / 2,
        ]
        self.cubeactor = self.create_cube_actor()
        self.cameraactor = self.create_cube_actor()
        edgeActor = self.addfeatureEdges()
        self.cubeactor.SetPosition(160, center[1], center[2])
        self.cubeactor.SetOrientation(
            self.defaultposition[0], self.defaultposition[1], self.defaultposition[2]
        )
        spaceseperation = 50
        self.cameraactor.SetPosition(
            160, center[1] - spaceseperation, center[2] - spaceseperation
        )
        self.cameraactor.SetOrientation(
            self.defaultposition[0], self.defaultposition[1], self.defaultposition[2]
        )
        self.ren.AddActor(self.cameraactor)
        self.ren.AddActor(edgeActor)
        self.ren.AddActor(self.cubeactor)
        self.ren.AddActor(self.actor)
        self.oldcamerapos = self.cubeactor.GetPosition()
        self.collisionFilter = vtk.vtkCollisionDetectionFilter()
        # Set up the collision filter
        self.collisionFilter.SetInputData(0, self.cubeactor.GetMapper().GetInput())
        self.collisionFilter.SetInputData(1, self.actor.GetMapper().GetInput())
        self.collisionFilter.SetTransform(
            0, vtk.vtkTransform()
        )  # Moving object transform
        self.collisionFilter.SetTransform(
            1, vtk.vtkTransform()
        )  # Static object transform
        self.collisionFilter.SetMatrix(
            0, self.cubeactor.GetMatrix()
        )  # Static object transform
        self.collisionFilter.SetMatrix(1, self.actor.GetMatrix())  # Static object transform
        self.collisionFilter.SetCollisionModeToAllContacts()
        self.collisionFilter.GenerateScalarsOn()
        camera = events.myInteractorStyle(
            self.xlabels,
            self.ylabels,
            self.ren,
            self.renderwindowinteractor,
            self.meshbounds,
            self.xlabelbefore,
            self.ylabelbefore,
            self.zlabelbefore,
            self.actor,
            self.polydata,
            self.reader,
            self.append_filterpolydata,
            self.cubeactor,
            self.cameraactor,
            self.oldcamerapos,
            self.collisionFilter,
            spaceseperation,
            center,
        )
        self.renderwindowinteractor.SetInteractorStyle(camera)
        self.ren.GetActiveCamera().SetPosition(0, -1, 0)
        self.ren.GetActiveCamera().SetFocalPoint(0, 0, 0)
        self.ren.GetActiveCamera().SetViewUp(0, 0, 1)
        self.ren.ResetCameraClippingRange()
        self.ren.ResetCamera()
        self.renderwindowinteractor.GetRenderWindow().Render()
        self.renderwindowinteractor.Initialize()
        self.renderwindowinteractor.Start()

    def fixedposition(self):
        minBounds = [self.meshbounds[0], self.meshbounds[2], self.meshbounds[4]]
        transform = vtk.vtkTransform()
        transform.Translate(-minBounds[0], -minBounds[1], -minBounds[2])
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetInputData(self.reader)
        transformFilter.SetTransform(transform)
        transformFilter.Update()
        transformedPolyData = transformFilter.GetOutput()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(transformedPolyData)
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)
        self.actor.GetProperty().SetRepresentationToSurface()
        colorsd = vtkNamedColors()
        self.actor.GetProperty().SetColor((230 / 255), (230 / 255), (250 / 255))
        self.actor.GetProperty().SetColor((230 / 255), (230 / 255), (250 / 255))
        self.actor.GetProperty().SetDiffuseColor(colorsd.GetColor3d("LightSteelBlue"))
        self.actor.GetProperty().SetDiffuse(0.8)
        self.actor.GetProperty().SetSpecular(0.3)
        self.actor.GetProperty().SetSpecularPower(60.0)
        self.actor.GetProperty().BackfaceCullingOn()
        self.actor.GetProperty().FrontfaceCullingOn()
        print(self.actor.GetBounds())
        for i in range(6):
            self.meshbounds[i] = self.actor.GetBounds()[i]

    def create_cube_actor(self):
        self.cube_source = vtk.vtkCubeSource()
        self.cube_source.SetXLength(10)
        self.cube_source.SetYLength(10)
        self.cube_source.SetZLength(10)
        self.cube_mapper = vtk.vtkPolyDataMapper()
        self.cube_mapper.SetInputConnection(self.cube_source.GetOutputPort())
        self.cube_mapper.ScalarVisibilityOff()
        self.cube_actor = vtk.vtkActor()
        self.cube_actor.SetMapper(self.cube_mapper)
        self.cube_actor.GetProperty().BackfaceCullingOn()
        self.cube_actor.GetProperty().FrontfaceCullingOn()
        self.cube_actor.GetProperty().SetOpacity(0.0)
        return self.cube_actor

    def polyDataToActor(self):
        """Wrap the provided vtkPolyData object in a mapper and an actor, returning
        the actor."""
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.reader)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToSurface()
        self.meshbounds = []
        for i in range(6):
            self.meshbounds.append(actor.GetBounds()[i])

