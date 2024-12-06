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
import PythonApplication.interactiveevent as events
import PythonApplication.exceldatavtk as vtk_data_excel
import PythonApplication.markingprogressbar as stageofmarking
import PythonApplication.stagedialog as addStage
import PythonApplication.sequencedialog as addsequence


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
        seqButton,
        NextButton_Page_3,
        localizebutton,
        ros_node,
        file_path,
        excelfiletext,
        seqlabel,
        mainwindow,
        Stagelabel,
        StageButton,
    ):
        # starting initialize
        super().__init__()
        self.defaultposition = [0, 0, 1]
        self.reader = vtk.vtkPolyData()
        self.meshbounds = None
        self.polydata = polydata
        self.ren = ren
        self.dialog = None
        self.renderwindowinteractor = renderwindowinteractor
        self.renderwindowinteractor.GetRenderWindow().AddRenderer(self.ren)
        self.xlabelbefore = xlabelbefore
        self.ylabelbefore = ylabelbefore
        self.zlabelbefore = zlabelbefore
        self.xlabels = xlabel
        self.ylabels = ylabel
        self.localizebutton = localizebutton
        self.ros_node = ros_node
        self.filepath = file_path
        self.excelfiletext = excelfiletext
        self.ren.SetBackground(1, 1, 1)
        self.renderwindowinteractor.GetRenderWindow().SetMultiSamples(0)
        self.ren.UseHiddenLineRemovalOn()
        self.seqButton = seqButton
        self.NextButton_Page_3 = NextButton_Page_3
        self.seqlabel = seqlabel
        self.mainwindow = mainwindow
        self.Stagelabel = Stagelabel
        self.StageButton = StageButton
        self.stagetext = None
        self.dataseqtext = None
        self.button_UI()
        if self.excelfiletext.toPlainText() != "":
            self.wall_identifiers = vtk_data_excel.exceldataextractor(
                self.excelfiletext.toPlainText()
            )
            self.excel_elements = vtk_data_excel.exceldataextractorelement(
                self.excelfiletext.toPlainText()
            )
        self.dataseqtext = None

    # setup button interaction and store in the ui
    def button_UI(self):
        self.seqButton.clicked.connect(lambda: self.addseqtext())
        self.StageButton.clicked.connect(lambda: self.addStagetext())

    def addStagetext(self):
        stagedialog = addStage.StageNumberDialog()
        stagenumber = None
        if stagedialog.exec_() == QDialog.Accepted:
            stagenumber = stagedialog.get_selected_stagenumber()
        self.stagetext = f"Stage {stagenumber}"
        self.Stagelabel.setText(self.stagetext)
        self.shownextpage()
        

    # store sequence as a variable
    def addseqtext(self):
        seqdialog = addsequence.SeqnumberDialog()
        self.dataseqtext = None
        if seqdialog.exec_() == QDialog.Accepted:
            self.dataseqtext = seqdialog.get_selected_seqnumber()
        self.sequencetext = f"Sequence : {self.dataseqtext}"
        self.seqlabel.setText(self.sequencetext)
        self.markingreq = self.checkseqreq()
        self.excel_elements_data, self.maxarraylen, self.counter = self.dialogmarking()
        self.shownextpage()
    

    def shownextpage(self):
        if self.stagetext and self.dataseqtext:
            markingprogessbar = stageofmarking.MarkingProgressBar()
            markingprogessbar.exec_()
            self.NextButton_Page_3.show()
            self.loadStl(self.dataseqtext)

    def checkseqreq(self):
        markingreq = None
        if self.dataseqtext == 1:
            target_category = "Piping"
            markingreq = self.find_in_categories(self.excel_elements, target_category)
        elif self.dataseqtext == 2:
            target_category = "Tiling/Floor"
            markingreq = self.find_in_categories(self.excel_elements, target_category)
        elif self.dataseqtext == 3:
            target_category = "Fitting"
            markingreq = self.find_in_categories(self.excel_elements, target_category)
        return markingreq

    def dialogmarking(self):
        counter = 0
        combined_data = {
            "markingidentifiers": [],
            "wall_numbers": [],
            "Position X (m)": [],
            "Position Y (m)": [],
            "Position Z (m)": [],
            "Shape type": [],
            "Stages": [],
        }
        for sheet_name, data in self.markingreq.items():
            combined_data["markingidentifiers"].extend(data["markingidentifiers"])
            combined_data["wall_numbers"].extend(data["wall_numbers"])
            combined_data["Position X (m)"].extend(data["Position X (m)"])
            combined_data["Position Y (m)"].extend(data["Position Y (m)"])
            combined_data["Position Z (m)"].extend(data["Position Z (m)"])
            combined_data["Shape type"].extend(data["Shape type"])
            combined_data["Stages"].extend([None] * len(data["markingidentifiers"]))
        maxarray = len(combined_data)
        return combined_data, maxarray, counter

    def find_in_categories(self, wall_numbers_by_sheet, target_category):
        result = {}
        for sheet_name, sheet_data in wall_numbers_by_sheet.items():
            matching_indexes = [
                i
                for i, category in enumerate(sheet_data["Categories"])
                if category == target_category
            ]
            if matching_indexes:
                result[sheet_name] = {
                    "markingidentifiers": [
                        sheet_data["markingidentifiers"][i] for i in matching_indexes
                    ],
                    "wall_numbers": [
                        sheet_data["wall_numbers"][i] for i in matching_indexes
                    ],
                    "Position X (m)": [
                        sheet_data["Position X (m)"][i] for i in matching_indexes
                    ],
                    "Position Y (m)": [
                        sheet_data["Position Y (m)"][i] for i in matching_indexes
                    ],
                    "Position Z (m)": [
                        sheet_data["Position Z (m)"][i] for i in matching_indexes
                    ],
                    "Shape type": [
                        sheet_data["Shape type"][i] for i in matching_indexes
                    ],
                    "Categories": [
                        sheet_data["Categories"][i] for i in matching_indexes
                    ],
                }
        return result

    # load stl in vtk frame
    def loadStl(self, dataseqtext):
        meshs = mesh.Mesh.from_file(self.polydata)
        points = meshs.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)
        vtk_points = vtk.vtkPoints()
        for vertex in points:
            vtk_points.InsertNextPoint(vertex)
        vtk_faces = vtk.vtkCellArray()
        for face in faces:
            polygon = vtk.vtkPolygon()
            for vertex_index in face:
                polygon.GetPointIds().InsertNextId(vertex_index)
            vtk_faces.InsertNextCell(polygon)
        self.reader.SetPoints(vtk_points)
        self.reader.SetPolys(vtk_faces)
        self.polyDataToActor()
        self.fixedposition()
        self.center = [
            (self.meshbounds[0] + self.meshbounds[1]) / 2,
            (self.meshbounds[2] + self.meshbounds[3]) / 2,
            (self.meshbounds[4] + self.meshbounds[5]) / 2,
        ]
        x_coords = []
        y_coords = []
        z_coords = []
        if self.excelfiletext.toPlainText() != "":
            for wall_identify in self.wall_identifiers:
                x_coords.append(wall_identify["Position X (m)"])
                y_coords.append(wall_identify["Position Y (m)"])
                z_coords.append(wall_identify["Position Z (m)"])
        self.cubeactor = self.create_cube_actor()
        self.cameraactor = self.create_cube_actor()
        self.cubeactor.SetPosition(160, self.center[1], self.center[2])
        self.cubeactor.SetOrientation(
            self.defaultposition[0], self.defaultposition[1], self.defaultposition[2]
        )
        self.spaceseperation = 50
        self.cameraactor.SetPosition(
            160,
            self.center[1] - self.spaceseperation,
            self.center[2] - self.spaceseperation,
        )
        self.cameraactor.SetOrientation(
            self.defaultposition[0], self.defaultposition[1], self.defaultposition[2]
        )
        self.ren.AddActor(self.cameraactor)
        self.ren.AddActor(self.cubeactor)
        self.ren.AddActor(self.actor)
        self.oldcamerapos = self.cubeactor.GetPosition()
        self.set_Collision()
        self.setupvtkframe(dataseqtext)

    # include collision
    def set_Collision(self):
        self.collisionFilter = vtk.vtkCollisionDetectionFilter()
        self.collisionFilter.SetInputData(0, self.cubeactor.GetMapper().GetInput())
        self.collisionFilter.SetInputData(1, self.actor.GetMapper().GetInput())
        self.collisionFilter.SetTransform(0, vtk.vtkTransform())
        self.collisionFilter.SetTransform(1, vtk.vtkTransform())
        self.collisionFilter.SetMatrix(0, self.cubeactor.GetMatrix())
        self.collisionFilter.SetMatrix(1, self.actor.GetMatrix())
        self.collisionFilter.SetCollisionModeToAllContacts()
        self.collisionFilter.GenerateScalarsOn()

    # setup vtk frame ui
    def setupvtkframe(self, dataseqtext):
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
            self.polydata,
            self.reader,
            self.cubeactor,
            self.cameraactor,
            self.oldcamerapos,
            self.collisionFilter,
            self.spaceseperation,
            self.center,
            self.filepath,
            self.Stagelabel,
            self.excelfiletext,
            dataseqtext,
            self.excel_elements_data,
            self.maxarraylen,
            self.counter,
            self.dialog,
            self.Stagelabel
        ]
        camera = events.myInteractorStyle(
            setcamerainteraction,
            self.wall_identifiers,
            self.localizebutton,
            self.ros_node,
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

    # fixed x y and z pos
    def fixedposition(self):
        minBounds = [self.meshbounds[0], self.meshbounds[2], self.meshbounds[4]]
        transform = vtk.vtkTransform()
        transform.Translate(-minBounds[0], -minBounds[1], -minBounds[2])
        transformFilter = vtkTransformPolyDataFilter()
        transformFilter.SetInputData(self.reader)
        transformFilter.SetTransform(transform)
        transformFilter.Update()
        transformedPolyData = transformFilter.GetOutput()
        self.setnormals(transformedPolyData)

    # set the mesh to the 0,0,0 starting pos
    def setnormals(self, transformedPolyData):
        normals = vtkPolyDataNormals()
        normals.SetInputData(transformedPolyData)
        normals.ComputePointNormalsOn()
        normals.ComputeCellNormalsOff()
        normals.Update()
        mesh_with_normals = normals.GetOutput()
        mapper = vtkPolyDataMapper()
        mapper.SetInputData(mesh_with_normals)
        self.setactor(mapper)

    # setup main actor
    def setactor(self, mapper):
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

    # create visual actor for frame controls
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

    # clear actor
    def clearactor(self):
        actors = self.ren.GetActors()
        actors.InitTraversal()
        actor = actors.GetNextActor()
        while actor:
            self.ren.RemoveActor(actor)
            actor = actors.GetNextActor()

    # set actor in the vtk mapper
    def polyDataToActor(self):
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.reader)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToSurface()
        self.meshbounds = []
        for i in range(6):
            self.meshbounds.append(actor.GetBounds()[i])

