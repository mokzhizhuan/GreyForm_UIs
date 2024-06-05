from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import vtk
from vtk import *
from vtkmodules.vtkCommonColor import vtkNamedColors
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
        self.reader = vtk.vtkSTLReader()
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

    def loadStl(self):
        """Load the given STL file, and return a vtkPolyData object for it."""
        self.reader.SetFileName(self.polydata)
        self.reader.Update()
        polydata = self.reader.GetOutput()
        self.actor = self.polyDataToActor(polydata)
        center = [
            (self.meshbounds[0] + self.meshbounds[1]) / 2,
            (self.meshbounds[2] + self.meshbounds[3]) / 2,
            (self.meshbounds[4] + self.meshbounds[5]) / 2,
        ]
        self.cubeactor = self.create_cube_actor()
        self.cameraactor = self.create_cube_actor()
        if self.actor and self.cubeactor and self.cameraactor:
            self.ren.RemoveActor(self.actor)
            self.ren.RemoveActor(self.cameraactor)
            self.ren.RemoveActor(self.cubeactor)
            self.renderwindowinteractor.GetRenderWindow().Render()
        self.cubeactor.SetPosition(80, center[1], center[2])
        self.cubeactor.SetOrientation(
            self.defaultposition[0], self.defaultposition[1], self.defaultposition[2]
        )
        spaceseperation = 50
        self.cameraactor.SetPosition(
            80, center[1] - spaceseperation, center[2] - spaceseperation
        )
        self.cameraactor.SetOrientation(
            self.defaultposition[0], self.defaultposition[1], self.defaultposition[2]
        )
        # Translate the cube to set its center to the origin (0,0,0)
        transform = vtk.vtkTransform()
        transform.Translate(-center[0], -center[1], -center[2])

        transform_filter = vtk.vtkTransformPolyDataFilter()
        transform_filter.SetTransform(transform)
        transform_filter.SetInputData(polydata)
        transform_filter.Update()

        translated_polydata = transform_filter.GetOutput()

        # Get the new bounds of the mesh
        new_meshbounds = translated_polydata.GetBounds()
        axes_length = [center[0] / 2, center[1] / 2, center[2] / 2]
        orientations = ["x", "-x", "y", "-y", "z", "-z"]
        face_centers = [
            (new_meshbounds[1], 0, new_meshbounds[5]),  # +X face
            (new_meshbounds[1], new_meshbounds[3] * 2, new_meshbounds[5]),  # -X face
            (new_meshbounds[1], new_meshbounds[3], 0),  # +Y face
            (new_meshbounds[1], new_meshbounds[3], new_meshbounds[5] * 2),  # -Y face
            (0, new_meshbounds[3], new_meshbounds[5]),  # +Z face
            (new_meshbounds[1] * 2, new_meshbounds[3], new_meshbounds[5]),  # -Z face
        ]
        # Add axes to each face of the cube
        self.ren.AddActor(self.cameraactor)
        self.ren.AddActor(self.cubeactor)
        self.ren.AddActor(self.actor)
        self.oldcamerapos = self.cubeactor.GetPosition()
        self.collisionFilter = vtk.vtkCollisionDetectionFilter()
        self.collisionFilter.SetInputData(0, self.cubeactor.GetMapper().GetInput())
        self.collisionFilter.SetInputData(1, self.actor.GetMapper().GetInput())
        self.collisionFilter.SetTransform(0, vtk.vtkTransform())
        self.collisionFilter.SetTransform(1, vtk.vtkTransform())
        self.collisionFilter.SetMatrix(0, self.cubeactor.GetMatrix())
        self.collisionFilter.SetMatrix(
            1, self.actor.GetMatrix()
        )  # Static object transform
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
            polydata,
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
        self.renderwindowinteractor.GetRenderWindow().Finalize()
        self.renderwindowinteractor.GetRenderWindow().Render()
        self.renderwindowinteractor.Initialize()
        self.renderwindowinteractor.Start()
        # for face_center, orientation in zip(face_centers, orientations):
        # self.add_axes(self.ren, face_center, orientation, axes_length)

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

    # set mesh as actor in vtk frame
    def polyDataToActor(self, polydata):
        """Wrap the provided vtkPolyData object in a mapper and an actor, returning
        the actor."""
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.reader.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToSurface()
        self.meshbounds = []
        for i in range(6):
            self.meshbounds.append(actor.GetBounds()[i])
        # color RGB must be /255 for Red, Green , blue color code
        actor.GetProperty().SetColor((230 / 255), (230 / 255), (250 / 255))
        actor.GetProperty().SetDiffuse(0.8)
        actor.SetPosition(0, 0, 0)
        colorsd = vtkNamedColors()
        actor.GetProperty().SetDiffuseColor(colorsd.GetColor3d("LightSteelBlue"))
        actor.GetProperty().SetSpecular(0.3)
        actor.GetProperty().SetSpecularPower(60.0)
        actor.GetProperty().BackfaceCullingOn()
        actor.GetProperty().FrontfaceCullingOn()
        actor.SetOrientation(1, 0, 0)
        self.append_filterpolydata.AddInputData(actor.GetMapper().GetInput())
        self.append_filterpolydata.Update()
        return actor

    def add_axes(self, renderer, center, orientation, axes_length):
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(axes_length[0], axes_length[1], axes_length[2])

        transform = vtk.vtkTransform()
        transform.Translate(center)

        if orientation == "x":
            transform.RotateY(90)
        elif orientation == "-x":
            transform.RotateY(-90)
        elif orientation == "y":
            transform.RotateX(90)
        elif orientation == "-y":
            transform.RotateX(-90)
        elif orientation == "-z":
            transform.RotateX(180)

        axes.SetUserTransform(transform)

        renderer.AddActor(axes)
