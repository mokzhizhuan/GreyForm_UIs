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


# create the imported stl mesh in vtk frame
class createMesh(QMainWindow):
    def __init__(
        self,
        ren,
        polydata,
        renderwindowinteractor,
        xlabelbefore,
        ylabelbefore,
        zlabelbefore,
        localizebutton,
        ros_node,
        file_path,
        mainwindow,
        Stagelabel,
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
        self.localizebutton = localizebutton
        self.ros_node = ros_node
        self.filepath = file_path
        self.ren.SetBackground(1, 1, 1)
        self.renderwindowinteractor.GetRenderWindow().SetMultiSamples(0)
        self.ren.UseHiddenLineRemovalOn()
        self.mainwindow = mainwindow
        self.stagestorage = ["Stage 1", "Stage 2", "Stage 3"]
        self.currentindexstage = 0
        self.stagetext = self.stagestorage[self.currentindexstage]
        Stagelabel.setText(f"Stage : {self.stagetext}")
        self.Stagelabel = Stagelabel
        self.wall_identifiers, self.wall, self.excelfiletext = (
            vtk_data_excel.exceldataextractor()
        )
        self.wallaxis = vtk_data_excel.wall_format(self.wall)
        self.loadStl()

    def show_cancelation_dialog(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Cancellation")
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

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
        self.addranges()
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

        self.walls = {
            "wall 1": {
                "position": ((self.meshbounds[0] + self.meshbounds[1]), -100, 0),
                "size": (self.wallaxis[1]["height"], self.wallaxis[1]["width"]),
                "color": (0, 1, 1),
                "rotation": (90, 0, 90),
            },  # Cyan
            "wall 2": {
                "position": (self.meshbounds[0] - 100, 0, 0),
                "size": (
                    (self.meshbounds[2] + self.meshbounds[3]),
                    self.wallaxis[1]["height"],
                ),
                "color": (1, 0, 0),
                "rotation": (0, 90, 90),
            },  # Red
            "wall 3": {
                "position": (
                    self.wallaxis[3]["width"],
                    (self.meshbounds[2] + self.meshbounds[3]) + 100,
                    0,
                ),
                "size": (
                    self.wallaxis[1]["height"],
                    self.wallaxis[3]["width"],
                ),
                "color": (1, 0, 1),
                "rotation": (90, 0, 90),
            },  # Magenta
            "wall 4": {
                "position": (
                    (self.meshbounds[0] + self.meshbounds[1]),
                    (self.meshbounds[2] + self.meshbounds[3]) - 300,
                    0,
                ),
                "size": (
                    self.wallaxis[1]["height"],
                    self.wallaxis[5]["width"],
                ),
                "color": (0.5, 0.5, 0),
                "rotation": (90, 0, 90),
            },  # Brown
            "wall 5": {
                "position": (
                    self.wallaxis[3]["width"] + 100,
                    self.wallaxis[3]["width"] - 200,
                    0,
                ),
                "size": (self.wallaxis[4]["width"], self.wallaxis[1]["height"]),
                "color": (0, 0.5, 0.5),
                "rotation": (0, 90, 90),
            },  # Teal
            "wall 6": {
                "position": (self.meshbounds[0] + self.meshbounds[1] + 100, 0, 0),
                "size": ((self.wallaxis[6]["width"], self.wallaxis[1]["height"])),
                "color": (0, 1, 0),
                "rotation": (0, 90, 90),
            },  # Green
            "floor": {
                "position": (0, 0, -100),
                "points": (
                    (0, 0, -100),
                    (0, (self.meshbounds[2] + self.meshbounds[3]), -100),
                    (
                        (self.meshbounds[2] + self.meshbounds[3]),
                        (self.meshbounds[2] + self.meshbounds[3]),
                        -100,
                    ),
                    (
                        (self.meshbounds[2] + self.meshbounds[3]),
                        self.wallaxis[6]["width"],
                        -100,
                    ),
                    (
                        (self.meshbounds[0] + self.meshbounds[1]),
                        self.wallaxis[6]["width"],
                        -100,
                    ),
                    ((self.meshbounds[0] + self.meshbounds[1]), 0, -100),
                ),
                "color": (1, 1, 0),
                "rotation": (0, 0, 0),
            },  # Yellow
        }
        self.wall_actors = {}
        for wall, properties in self.walls.items():
            if wall != "floor":
                actor = self.create_wall_actor(
                    name=wall,
                    position=properties["position"],
                    size=properties["size"],
                    color=properties["color"],
                    rotation=properties["rotation"],
                )
            else:
                actor = self.create_floor_actor(
                    name=wall,
                    position=properties["position"],
                    points_list=properties["points"],
                    color=properties["color"],
                    rotation=properties["rotation"],
                )
            self.ren.AddActor(actor)
        self.set_Collision()
        self.setupvtkframe()

    def create_wall_actor(self, name, position, size, color, rotation):
        """Creates a wall (rectangular plane) at a given position, size, and color."""
        # Define the plane source
        plane = vtk.vtkPlaneSource()
        plane.SetOrigin(0, 0, 0)
        plane.SetPoint1(size[0], 0, 0)  # Width
        plane.SetPoint2(0, size[1], 0)  # Height

        transform = vtk.vtkTransform()
        transform.RotateX(rotation[0])  # Rotation around X-axis
        transform.RotateY(rotation[1])  # Rotation around Y-axis
        transform.RotateZ(rotation[2])  # Rotation around Z-axis

        # Apply transformation to the plane
        transform_filter = vtk.vtkTransformPolyDataFilter()
        transform_filter.SetInputConnection(plane.GetOutputPort())
        transform_filter.SetTransform(transform)
        transform_filter.Update()

        # Mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(transform_filter.GetOutputPort())

        # Actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.SetPosition(position)
        actor.VisibilityOff()

        self.wall_actors[name] = actor

        return actor

    def create_floor_actor(self, name, position, points_list, color, rotation):
        points = vtk.vtkPoints()
        for i, point in enumerate(points_list):
            points.InsertNextPoint(point)

        # Step 2: Define a polygon with the points
        polygon = vtk.vtkPolygon()
        polygon.GetPointIds().SetNumberOfIds(len(points_list))
        for i in range(len(points_list)):
            polygon.GetPointIds().SetId(i, i)

        # Step 3: Create PolyData and set the polygon
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)

        cells = vtk.vtkCellArray()
        cells.InsertNextCell(polygon)
        poly_data.SetPolys(cells)

        # Step 4: Create mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.SetPosition(position)

        # Apply rotation
        actor.RotateX(rotation[0])
        actor.RotateY(rotation[1])
        actor.RotateZ(rotation[2])

        # Add metadata for hiding or naming
        actor.name = name  # Assign a name for reference
        actor.VisibilityOff()

        return actor

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
    def setupvtkframe(self):
        setcamerainteraction = [
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

    def addranges(self):
        current_y = 0
        current_x = 0
        max_y = self.wall7[1]  # Maximum Y position based on the image
        max_x = self.wall7[0]  # Maximum X position based on the image

        for wall_id, wall in self.wallaxis.items():
            if "pos_y_range" not in wall or wall["pos_y_range"] is None:
                wall["pos_y_range"] = (0, 0)

            if "pos_x_range" not in wall or wall["pos_x_range"] is None:
                wall["pos_x_range"] = (0, 0)
            if wall["axis"] == "y":  # Wall along the Y-axis
                # Y-axis walls increase current_y
                if wall_id == 2:  # Specific for Wall 1
                    wall["pos_x_range"] = (0, 50)
                    wall["pos_y_range"] = (0, self.wall7[0])
                elif wall_id == 4:  # Specific for wall 3
                    wall["pos_x_range"] = (self.wall7[1] - 50, self.wall7[1])
                    wall["pos_y_range"] = (
                        self.wall7[1] - self.wallaxis[4]["width"],
                        self.wall7[1],
                    )
                elif wall_id == 6:  # Specific for wall 5
                    wall["pos_x_range"] = (self.wall7[0] - 100, max_x)
                    wall["pos_y_range"] = (0, max_y)
                else:
                    wall["pos_x_range"] = (0, max_x)
                    wall["pos_y_range"] = (current_y, current_y + self.wall7[0])
            elif wall["axis"] == "x":  # Wall along the X-axis
                # X-axis walls increase current_x
                if wall_id == 3:  # Specific for Wall 2
                    wall["pos_x_range"] = (0, wall["width"])
                    wall["pos_y_range"] = (
                        max_y - self.wallaxis[4]["width"] + 50,
                        max_y,
                    )
                elif wall_id == 5:  # Specific for Wall 4
                    wall["pos_x_range"] = (self.wall7[1], max_x)
                    wall["pos_y_range"] = (max_y - 50, max_y)
                elif wall_id == 1:  # Wall 6
                    wall["pos_x_range"] = (0, max_x)  # Corrected range
                    wall["pos_y_range"] = (0, 50)
                else:
                    wall["pos_x_range"] = (current_x, current_x + max_x)
                    wall["pos_y_range"] = (0, max_y)
            wall["pos_x_range"] = (
                max(0, wall["pos_x_range"][0]),
                min(max_x, wall["pos_x_range"][1]),
            )
            wall["pos_y_range"] = (
                max(0, wall["pos_y_range"][0]),
                min(max_y, wall["pos_y_range"][1]),
            )
