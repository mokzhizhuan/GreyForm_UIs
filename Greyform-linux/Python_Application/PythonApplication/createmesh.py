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
import PythonApplication.markingitem as markingdialogitem


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
        Stagelabel,
        localizebutton,
        ros_node,
        file_path,
        excelfiletext,
        seqlabel,
        mainwindow,
        markingitembutton
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
        self.seq1Button = seq1Button
        self.seq2Button = seq2Button
        self.seq3Button = seq3Button
        self.NextButton_Page_3 = NextButton_Page_3
        self.seqlabel = seqlabel
        self.mainwindow = mainwindow
        self.markingitembutton = markingitembutton
        self.button_UI()
        self.retranslateUi()
        self.Stagelabel = Stagelabel
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
        self.seq1Button.clicked.connect(
            lambda: self.addseqtext(self.seq1Button, self.NextButton_Page_3)
        )
        self.seq2Button.clicked.connect(
            lambda: self.addseqtext(self.seq2Button, self.NextButton_Page_3)
        )
        self.seq3Button.clicked.connect(
            lambda: self.addseqtext(self.seq3Button, self.NextButton_Page_3)
        )
        self.NextButton_Page_3.clicked.connect(self.open_marking_dialog)
        self.markingitembutton.clicked.connect(self.open_marking_dialog)

    # store sequence as a variable
    def addseqtext(self, buttonseq, buttonnextpage):
        self.dataseqtext = buttonseq.text()
        self.dataseqtext = self.dataseqtext.replace("Sequence ", "")
        self.dataseqtext = int(self.dataseqtext)
        self.textseq = buttonseq.text()
        self.textseq = self.textseq.replace("Sequence ", "Sequence : ")
        self.seqlabel.setText(self.textseq)
        markingprogessbar = stageofmarking.MarkingProgressBar()
        markingprogessbar.exec_()
        buttonnextpage.show()
        self.markingreq = self.checkseqreq()
        self.excel_elements_data, self.maxarraylen, self.counter = self.dialogmarking()
        self.loadStl(self.dataseqtext)

    def checkseqreq(self):
        if self.dataseqtext == 1:
            target_category = "Piping"
            markingreq = self.find_in_categories(self.excel_elements, target_category)
        elif self.dataseqtext == 2:
            target_category = "Tiling/Floor"
            markingreq  = self.find_in_categories(self.excel_elements, target_category)
        elif self.dataseqtext == 3:
            target_category = "Fitting"
            markingreq  = self.find_in_categories(self.excel_elements, target_category)
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
        }
        for sheet_name, data in self.markingreq.items():
            combined_data["markingidentifiers"].extend(data["markingidentifiers"])
            combined_data["wall_numbers"].extend(data["wall_numbers"])
            combined_data["Position X (m)"].extend(data["Position X (m)"])
            combined_data["Position Y (m)"].extend(data["Position Y (m)"])
            combined_data["Position Z (m)"].extend(data["Position Z (m)"])
            combined_data["Shape type"].extend(data["Shape type"])
        maxarray = len(combined_data)
        return combined_data, maxarray, counter

    def open_marking_dialog(self):
        if self.dialog is not None:
            self.dialog.close()
        if self.counter < self.maxarraylen:
            self.dialog = markingdialogitem.markingitemdialog(
                self.excel_elements_data, self.counter , self.maxarraylen
            )
            font = self.dialog.font() 
            font.setPointSize(20) 
            self.dialog.setFont(font)
            self.dialog.show()
        else:
            print("Marking is completed, You can proceed to click another sequence or close the application")


    def checkseqreq(self):
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

    # insert collision
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
            self.dialog
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

    # clear actor
    def clearactor(self):
        actors = self.ren.GetActors()
        actors.InitTraversal()
        actor = actors.GetNextActor()
        while actor:
            self.ren.RemoveActor(actor)
            actor = actors.GetNextActor()

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

    def retranslateUi(self):
        self.seq1Button.setToolTip("Please include sequence")
        self.seq2Button.setToolTip("Please include sequence")
        self.seq3Button.setToolTip("Please include sequence")
