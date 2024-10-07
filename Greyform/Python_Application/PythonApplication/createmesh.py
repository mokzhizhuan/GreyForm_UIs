from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import vtk
from vtk import *
from vtkmodules.vtkCommonColor import vtkNamedColors
import PythonApplication.interactiveevent as events
import PythonApplication.doormeshvtk as doormeshVTK
import PythonApplication.exceldatavtk as vtk_data_excel
import PythonApplication.markingprogressbar as stageofmarking


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
        seq1Button,
        seq2Button,
        seq3Button,
        NextButton_Page_3,
        Seqlabel,
        localizebutton,
        file_path,
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
        self.seq1Button = seq1Button
        self.seq2Button = seq2Button
        self.seq3Button = seq3Button
        self.NextButton_Page_3 = NextButton_Page_3
        self.Seqlabel = Seqlabel
        self.localizebutton = localizebutton
        self.filepath = file_path
        self.ren.SetBackground(1, 1, 1)
        self.dataseqtext = None
        self.renderwindowinteractor.GetRenderWindow().SetMultiSamples(0)
        self.ren.UseHiddenLineRemovalOn()
        self.door = doormeshVTK.doorMesh()
        seq1Button.clicked.connect(
            lambda: self.addseqtext(seq1Button, NextButton_Page_3)
        )
        seq2Button.clicked.connect(
            lambda: self.addseqtext(seq2Button, NextButton_Page_3)
        )
        seq3Button.clicked.connect(
            lambda: self.addseqtext(seq3Button, NextButton_Page_3)
        )
        self.wall_identifiers = vtk_data_excel.exceldataextractor()

    #load stl loader to pyvista
    def loadStl(self, dataseqtext):
        self.clearactor()
        self.reader.SetFileName(self.polydata)
        self.reader.Update()
        polydata = self.reader.GetOutput()
        self.polyDataToActor(polydata)
        self.doordimension = self.door.includedimension()
        self.fixedposition(polydata)
        center = [
            (self.meshbounds[0] + self.meshbounds[1]) / 2,
            (self.meshbounds[2] + self.meshbounds[3]) / 2,
            (self.meshbounds[4] + self.meshbounds[5]) / 2,
        ]
        x_coords = []
        y_coords = []
        z_coords = []
        for wall_identify in self.wall_identifiers:
            x_coords.append(wall_identify["Position X (m)"])
            y_coords.append(wall_identify["Position Y (m)"])
            z_coords.append(wall_identify["Position Z (m)"])
        for wall_identify, x, y, z in zip(
            self.wall_identifiers, x_coords, y_coords, z_coords
        ):
            point_id = self.find_closest_point(polydata, (x, y, z))
            wall_identify["Point ID"] = point_id
        self.cubeactor = self.create_cube_actor()
        self.cameraactor = self.create_cube_actor()
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
        self.ren.AddActor(self.cubeactor)
        self.ren.AddActor(self.actor)
        self.oldcamerapos = self.cubeactor.GetPosition()
        self.collisionFilter = vtk.vtkCollisionDetectionFilter()
        self.collisionFilter.SetInputData(0, self.cubeactor.GetMapper().GetInput())
        self.collisionFilter.SetInputData(1, self.actor.GetMapper().GetInput())
        self.collisionFilter.SetTransform(0, vtk.vtkTransform())
        self.collisionFilter.SetTransform(1, vtk.vtkTransform())
        self.collisionFilter.SetMatrix(0, self.cubeactor.GetMatrix())
        self.collisionFilter.SetMatrix(1, self.actor.GetMatrix())
        self.collisionFilter.SetCollisionModeToAllContacts()
        self.collisionFilter.GenerateScalarsOn()
        setcamerainteraction = [
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
            self.cubeactor,
            self.cameraactor,
            self.oldcamerapos,
            self.collisionFilter,
            spaceseperation,
            center,
            self.filepath
        ]
        camera = events.myInteractorStyle(
            setcamerainteraction, self.wall_identifiers, self.localizebutton
        )
        self.renderwindowinteractor.SetInteractorStyle(camera)
        self.ren.GetActiveCamera().SetPosition(0, -1, 0)
        self.ren.GetActiveCamera().SetFocalPoint(0, 0, 0)
        self.ren.GetActiveCamera().SetViewUp(0, 0, 1)
        self.ren.SetBackground(0.1, 0.2, 0.3)
        self.ren.ResetCameraClippingRange()
        self.ren.ResetCamera()
        self.renderwindowinteractor.GetRenderWindow().Render()
        self.renderwindowinteractor.GetRenderWindow().Finalize()
        self.renderwindowinteractor.GetRenderWindow().Render()
        self.renderwindowinteractor.Initialize()
        self.renderwindowinteractor.Start()

    #fixed position stl data
    def fixedposition(self, polydata):
        minBounds = [self.meshbounds[0], self.meshbounds[2], self.meshbounds[4]]
        transform = vtk.vtkTransform()
        transform.Translate(-minBounds[0], -minBounds[1], -minBounds[2])
        transformFilter = vtkTransformPolyDataFilter()
        transformFilter.SetInputData(polydata)
        transformFilter.SetTransform(transform)
        transformFilter.Update()
        transformedPolyData = transformFilter.GetOutput()
        """normals = vtkPolyDataNormals()
        normals.SetInputData(transformedPolyData)
        normals.ComputePointNormalsOn()
        normals.ComputeCellNormalsOff()
        normals.Update()
        mesh_with_normals = normals.GetOutput()
        internal_points = vtk.vtkPoints()
        thickness = self.doordimension[3]
        for i in range(mesh_with_normals.GetNumberOfPoints()):
            point = mesh_with_normals.GetPoint(i)
            normal = mesh_with_normals.GetPointData().GetNormals().GetTuple(i)
            new_point = [point[j] - thickness * normal[j] for j in range(3)]
            internal_points.InsertNextPoint(new_point)
        internal_mesh = vtkPolyData()
        internal_mesh.SetPoints(internal_points)
        internal_mesh.SetPolys(polydata.GetPolys())"""
        append_filter = vtkAppendPolyData()
        append_filter.AddInputData(transformedPolyData)
        # append_filter.AddInputData(internal_mesh)
        append_filter.Update()
        combined_mesh = append_filter.GetOutput()
        mapper = vtkPolyDataMapper()
        mapper.SetInputData(combined_mesh)
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
        for i in range(6):
            self.meshbounds[i] = int(self.actor.GetBounds()[i])
        print(self.actor.GetBounds())

    #clear actor
    def clearactor(self):
        actors = self.ren.GetActors()
        actors.InitTraversal()
        actor = actors.GetNextActor()
        while actor:
            self.ren.RemoveActor(actor)
            actor = actors.GetNextActor()

    #create visual actor for camera range
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
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)
        self.meshbounds = []
        for i in range(6):
            self.meshbounds.append(self.actor.GetBounds()[i])

    #set sequence as a variable
    def addseqtext(self, buttonseq, buttonnextpage):
        self.dataseqtext = buttonseq.text()
        self.dataseqtext = self.dataseqtext.replace("Sequence ", "")
        self.dataseqtext = int(self.dataseqtext)
        markingprogessbar = stageofmarking.MarkingProgressBar()
        markingprogessbar.exec_()
        buttonnextpage.show()
        self.loadStl(self.dataseqtext)
