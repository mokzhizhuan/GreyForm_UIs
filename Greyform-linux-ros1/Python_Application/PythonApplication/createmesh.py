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
import re
import PythonApplication.actors as createactorvtk
import PythonApplication.arraystorage as storingelement
import PythonApplication.ifcextractfiles as extractor
import cv2


# create the imported stl mesh in vtk frame
class createMesh(QMainWindow):
    def __init__(
        self,
        ren,
        polydata,
        renderwindowinteractor,
        ros_node,
        file_path,
        mainwindow,
        Stagelabel,
        walllabel,
        stacked_widget,
        listenerdialog,
        wall_dimensions,
        floor,
        wall_finishes_dimensions,
        label_map,
        directional_axes_axis,
        toggle_button,
        camera_label
    ):
        # starting initialize
        super().__init__()
        self.defaultposition = [0, 0, 1]
        self.reader = vtk.vtkPolyData()
        self.meshbounds = None
        self.polydata = polydata
        self.wall_dimensions = wall_dimensions
        self.floor = floor
        self.label_map = label_map
        self.directional_axes_axis = directional_axes_axis
        self.ren = ren
        self.dialog = None
        self.tracking = False
        self.tracker = None
        self.toggle_button = toggle_button
        self.cameralabel = camera_label
        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        self.frameSize = (frame.shape[1], frame.shape[0]) if ret else (640, 480)
        self.renderwindowinteractor = renderwindowinteractor
        self.wall_finishes_dimensions = wall_finishes_dimensions
        self.renderwindowinteractor.GetRenderWindow().AddRenderer(self.ren)
        self.ros_node = ros_node
        self.filepath = file_path
        self.walllabel = walllabel
        self.stacked_widget = stacked_widget
        self.listenerdialog = listenerdialog    
        self.axis_widths = {"x": [], "y": []}
        self.ren.SetBackground(1, 1, 1)
        self.renderwindowinteractor.GetRenderWindow().SetMultiSamples(0)
        self.ren.UseHiddenLineRemovalOn()
        self.mainwindow = mainwindow
        self.currentindexstage = 0
        self.Stagelabel = Stagelabel
        (
            self.wall_identifiers,
            self.wall,
            self.excelfiletext,
            self.stagewallnum,
            self.stagestorage,
        ) = vtk_data_excel.exceldataextractor()
        self.wall_finishes_height, self.small_wall_height = (
            storingelement.wall_format_finishes(self.wall_finishes_dimensions)
        )
        self.wallformat, self.heighttotal, self.wall_height = (
            storingelement.wall_format(
                self.wall_dimensions,
                self.floor,
                self.label_map,
                self.wall_finishes_height,
            )
        )
        self.wallformat, self.axis_widths = extractor.addranges(
            self.floor,
            self.wall_height,
            self.wall_finishes_height,
            self.label_map,
            self.wallformat,
            self.axis_widths,
            self.directional_axes_axis,
        )
        self.stagetext = self.stagestorage[self.currentindexstage]
        Stagelabel.setText(f"Stage : {self.stagetext}")
        self.wallaxis = vtk_data_excel.wall_format(self.wall)
        self.toggle_button.clicked.connect(self.toggle_view)
        self.loadStl()

    def show_cancelation_dialog(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Cancellation")
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def toggle_view(self):
        if self.showing_camera:
            # Switch to VTK
            self.timer.stop()
            self.cameralabel.hide()
            self.renderwindowinteractor.show()
            self.loadStl()
        else:
            # Switch to Camera
            self.renderwindowinteractor.hide()
            self.cameralabel.show()
            self.timer.start()
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)
        self.showing_camera = not self.showing_camera

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        frame = cv2.resize(frame, self.frameSize)
        if self.tracking and self.tracker:
            success, bbox = self.tracker.update(frame)
            if success:
                self.draw_box(frame, bbox)
            else:
                frame_h, frame_w = frame.shape[:2]
                font_scale = frame_w / 1600 * 0.7
                thickness = max(2, frame_w // 400)
                cv2.putText(frame, "Tracker Lost", (int(0.05 * frame_w), int(0.07 * frame_h)),
                            cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qimg))
        self.image_label.resize(w, h)
        self.resize(w, h + self.toggle_button.height())

    def draw_box(self, frame, bbox):
        x, y, w, h = map(int, bbox)
        frame_h, frame_w = frame.shape[:2]
        thickness = max(2, frame_w // 400)
        font_scale = frame_w / 1600 * 0.7
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), thickness)
        cv2.putText(frame, "Tracking", (int(0.05 * frame_w), int(0.07 * frame_h)),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)

    # load stl in vtk frame
    def loadStl(self):
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
        self.wall7 = [self.meshbounds[1], self.meshbounds[3]]
        self.walls = {}
        self.walls , self.cameraactors= createactorvtk.initialize_walls(self.wallformat,self.axis_widths , self.walls)
        self.wall_actors, self.identifier, self.wallname , self.cameraactors = createactorvtk.setupactors(
            self.walls, self.stagetext, self.wall_identifiers, self.ren, self.walllabel ,self.cameraactors
        )
        self.setupvtkframe()

    # setup vtk frame ui
    def setupvtkframe(self):
        setcamerainteraction = [
            self.ren,
            self.renderwindowinteractor,
            self.meshbounds,
            self.filepath,
            self.excelfiletext,
            self.dialog,
            self.stagetext,
            self.wall7,
            self.wallaxis,
            self.wall_identifiers,
            self.stagestorage,
            self.currentindexstage,
            self.Stagelabel,
            self.walls,
            self.wall_actors,
            self.wallname,
            self.identifier,
            self.stacked_widget,
            self.walllabel,
            self.listenerdialog,
        ]
        camera = events.myInteractorStyle(
            setcamerainteraction,
            self.cameraactors
        )
        self.renderwindowinteractor.SetInteractorStyle(camera)
        self.ren.GetActiveCamera().SetPosition(0, -1, 0)
        self.ren.GetActiveCamera().SetFocalPoint(0, 0, 0)
        self.ren.GetActiveCamera().SetViewUp(0, 0, 1)
        self.ren.ResetCameraClippingRange()
        self.ren.ResetCamera()
        self.renderwindowinteractor.GetRenderWindow().Render()
        self.renderwindowinteractor.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        renderWindow = self.renderwindowinteractor.GetRenderWindow()
        renderWindow.AddRenderer(self.ren)
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