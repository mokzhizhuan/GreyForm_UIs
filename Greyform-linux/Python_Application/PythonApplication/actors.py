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


def setupactors(walls, stagetext, wall_identifiers, ren, walllabel, camera_actors):
    identifier = {}
    wall_actors = {}
    camera_actors_set = {}
    wallname = None  # Initialize wallname to ensure valid return

    for wall, properties in walls.items():
        if wall == "Floor":
            wall_number = "F"  # Special case for Floor
        else:
            match = re.search(r"\d+", wall)
            wall_number = int(match.group()) if match else None

        # Skip walls that are not in the stage text or Excel data
        if wall_number is None or stagetext not in wall_identifiers:
            continue

        sheet_data = wall_identifiers[stagetext]

        # Get indexes where wall number matches the Excel data
        if wall_number == "F":
            indexes = [
                i for i, wn in enumerate(sheet_data["Wall Number"]) if wn == "F"
            ]
        else:
            indexes = [
                i for i, wn in enumerate(sheet_data["Wall Number"]) if wn == wall_number
            ]

        if not indexes:  # If no valid indexes, skip to the next wall
            continue

        # Store identifier information
        for idx in indexes:
            if (
                0 <= idx < len(sheet_data["markingidentifiers"])
                and 0 <= idx < len(sheet_data["Position X (mm)"])
                and 0 <= idx < len(sheet_data["Position Y (mm)"])
                and 0 <= idx < len(sheet_data["Position Z (mm)"])
                and 0 <= idx < len(sheet_data["Shape type"])
                and 0 <= idx < len(sheet_data["width"])
                and 0 <= idx < len(sheet_data["height"])
                and 0 <= idx < len(sheet_data["Status"])
            ):
                if wall_number not in identifier:
                    identifier[wall_number] = []
                identifier[wall_number].append(
                    {
                        "sheet_name": stagetext,
                        "markingidentifiers": sheet_data["markingidentifiers"][idx],
                        "Wall Number": wall_number,
                        "Position X (mm)": sheet_data["Position X (mm)"][idx],
                        "Position Y (mm)": sheet_data["Position Y (mm)"][idx],
                        "Position Z (mm)": sheet_data["Position Z (mm)"][idx],
                        "Shape type": sheet_data["Shape type"][idx],
                        "width": sheet_data["width"][idx],
                        "height": sheet_data["height"][idx],
                        "Status": sheet_data["Status"][idx],
                    }
                )

        # Create wall actor if not already created
        if wall not in wall_actors:
            if wall != "Floor":
                actor = create_wall_actor(
                    name=wall,
                    position=properties["position"],
                    size=properties["size"],
                    color=properties["color"],
                    rotation=properties["rotation"],
                )
                # Create camera actor if the camera key exists
                camera_key = f"Camera_{wall_number}"
                if camera_key not in camera_actors:
                    if "position" in properties and "size" in properties:
                        view_up = (0, 0, 1)  # Horizontal walls (sideways)
                        camera_position = (
                            properties["position"][0] - properties["size"][0] * 1.5, 
                            properties["position"][1], 
                            properties["position"][2] + properties["size"][0] / 2
                        )
                        camera_actor = create_camera_actor(
                            position=camera_position,
                            focal_point=properties["position"],
                            view_up=view_up,
                            height=properties["size"][1],
                            width=properties["size"][0],
                        )
                        camera_actors[camera_key] = {
                            "position": camera_position,
                            "focal_point": properties["position"],
                            "view_up": view_up,
                        }
                    else:
                        continue
                else:
                    camera_actor = create_camera_actor(
                        position=camera_actors[camera_key]["position"],
                        focal_point=camera_actors[camera_key]["focal_point"],
                        view_up=camera_actors[camera_key]["view_up"],
                        height=properties["size"][1],
                        width=properties["size"][0],
                    )
                camera_actors_set[wall] = camera_actor
            else:
                actor = create_floor_actor(
                    name=wall,
                    position=properties["position"],
                    points_list=properties["points"],
                    color=properties["color"],
                    rotation=properties["rotation"],
                )
            wall_actors[wall] = actor
            ren.AddActor(actor)
    # Determine the first valid wall to display
    if identifier:
        # Find the first wall number based on valid identifiers
        first_wall_number = min(identifier.keys(), key=lambda x: (x == "F", x))
        for wall_name in wall_actors:
            match = re.search(r"\d+", wall_name)
            wall_number = (
                int(match.group()) if match else "F" if wall_name == "Floor" else None
            )
            if wall_number == first_wall_number:
                wall_actors[wall_name].VisibilityOn()
                wallname = wall_name  # Set the valid wallname
                walllabel.setText(f"Wall : {wallname}")
                break  # Stop after finding the first valid wall
            else:
                wall_actors[wall_name].VisibilityOff()

    # Ensure that wallname is correctly set as the first valid wall
    if wallname is None:
        # Get the first key from identifier if no wall was set
        if identifier:
            first_wall_number = min(identifier.keys(), key=lambda x: (x == "F", x))
            wallname = f"Wall {first_wall_number}"

    # Return the result, ensuring wallname is included
    return wall_actors, identifier, wallname, camera_actors_set

def create_camera_actor(position, focal_point, view_up, height, width):
    camera = vtk.vtkCamera()
    distance_factor = 1.5  # Adjusted distance factor for better framing
    # Determine if the wall is vertical or horizontal based on position and focal point
    is_vertical = abs(focal_point[0] - position[0]) > abs(focal_point[1] - position[1])
    # Adjust the view-up vector dynamically based on wall orientation
    if is_vertical:
        view_up = (0, 1, 0)  # Upright orientation for vertical walls
        camera_position = (
            focal_point[0],
            focal_point[1] - distance_factor * width,
            focal_point[2] + height / 2,
        )
    else:
        view_up = (0, 0, 1)  # Sideways orientation for horizontal walls
        camera_position = (
            focal_point[0] - distance_factor * width,
            focal_point[1],
            focal_point[2] + height / 2,
        )
    # Set camera properties
    camera.SetPosition(*camera_position)
    camera.SetFocalPoint(*focal_point)
    camera.SetViewUp(*view_up)
    camera.SetViewAngle(75)  # Moderate angle to cover the full wall
    camera_actor = vtk.vtkCameraActor()
    camera_actor.SetCamera(camera)
    return camera_actor


def create_wall_actor(name, position, size, color, rotation):
    """Creates a wall (rectangular plane) at a given position, size, and color."""
    plane = vtk.vtkPlaneSource()
    plane.SetOrigin(0, 0, 0)
    plane.SetPoint1(size[0], 0, 0)  # Width
    plane.SetPoint2(0, size[1], 0)  # Height
    transform = vtk.vtkTransform()
    transform.RotateX(rotation[0])  # Rotation around X-axis
    transform.RotateY(rotation[1])  # Rotation around Y-axis
    transform.RotateZ(rotation[2])  # Rotation around Z-axis
    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetInputConnection(plane.GetOutputPort())
    transform_filter.SetTransform(transform)
    transform_filter.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(transform_filter.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.name = name
    actor.SetPosition(position)
    actor.VisibilityOff()
    return actor


def create_floor_actor(name, position, points_list, color, rotation):
    points = vtk.vtkPoints()
    for i, point in enumerate(points_list):
        points.InsertNextPoint(point)
    # Step 2: Define a polygon with the points
    polygon = vtk.vtkPolygon()
    polygon.GetPointIds().SetNumberOfIds(len(points_list))
    for i in range(len(points_list)):
        polygon.GetPointIds().SetId(i, i)
    poly_data = vtk.vtkPolyData()
    poly_data.SetPoints(points)
    cells = vtk.vtkCellArray()
    cells.InsertNextCell(polygon)
    poly_data.SetPolys(cells)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly_data)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.SetPosition(position)
    actor.RotateX(rotation[0])
    actor.RotateY(rotation[1])
    actor.RotateZ(rotation[2])
    actor.name = name
    actor.VisibilityOff()
    return actor


def switch_hidden_camera(wall_name, ren, camera_actors, renderwindowinteractor):
    if wall_name not in camera_actors:
        return
    # Get the selected camera actor
    hidden_camera = camera_actors[wall_name]
    ren.SetActiveCamera(hidden_camera.GetCamera())
    ren.ResetCameraClippingRange()
    renderwindowinteractor.GetRenderWindow().Render()

def initialize_walls(wallformat, axis_widths, walls):
    color_map = [
        (0, 1, 1),
        (1, 0, 0),
        (1, 0, 1),
        (0.5, 0.5, 0),
        (0, 0.5, 0.5),
        (0, 1, 0),
    ]
    rotation_map = {"x": (90, 0, 90), "y": (0, 90, 90)}
    camera_actors = {}
    for wall_id, wall_data in wallformat.items():
        axis = wall_data["axis"]
        width = wall_data["width"]
        height = wall_data["height"]
        pos_x_range = wall_data["pos_x_range"]
        pos_y_range = wall_data["pos_y_range"]
        position = (
            (pos_x_range[0] + pos_x_range[1]) / 2,
            (pos_y_range[0] + pos_y_range[1]) / 2,
            0,
        )
        size = (width, height)
        color = color_map[(wall_id - 1) % len(color_map)]
        rotation = rotation_map[axis]
        camera_position = (
            position[0] + 100 if axis == "x" else position[0],
            position[1] + 100 if axis == "y" else position[1],
            height / 2,
        )
        camera_actors[f"Camera_{wall_id}"] = {
            "position": camera_position,
            "focal_point": position,
            "view_up": (0, 0, 1),
        }
        walls[f"Wall {wall_id}"] = {
            "position": position,
            "size": size,
            "color": color,
            "rotation": rotation,
        }
    # Initialize floor separately
    walls["Floor"] = {
        "position": (0, 0, -100),
        "points": [
            (0, 0, -100),
            (0, max(axis_widths["y"]), -100),
            (max(axis_widths["x"]), max(axis_widths["y"]), -100),
            (max(axis_widths["x"]), 0, -100),
        ],
        "color": (1, 1, 0),
        "rotation": (0, 0, 0),
    }
    return walls, camera_actors
