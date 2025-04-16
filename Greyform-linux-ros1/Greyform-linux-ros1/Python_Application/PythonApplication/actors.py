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


def setupactors(walls, stagetext, wall_identifiers, ren, walllabel):
    identifier = {}
    wall_actors = {}

    for wall, properties in walls.items():
        if wall == "Floor":
            wall_number = "F"  # Special case for Floor
        else:
            match = re.search(r'\d+', wall)
            wall_number = int(match.group()) if match else None

        if wall_number is not None and stagetext in wall_identifiers:
            sheet_data = wall_identifiers[stagetext]
            
            if wall_number == "F":
                indexes = [i for i, wn in enumerate(sheet_data["wall_numbers"]) if wn == "F"]
            else:
                indexes = [i for i, wn in enumerate(sheet_data["wall_numbers"]) if wn == wall_number]

            for idx in indexes:  # Store all occurrences
                if (
                    0 <= idx < len(sheet_data["markingidentifiers"]) and
                    0 <= idx < len(sheet_data["Position X (mm)"]) and
                    0 <= idx < len(sheet_data["Position Y (mm)"]) and
                    0 <= idx < len(sheet_data["Position Z (mm)"]) and
                    0 <= idx < len(sheet_data["Shape type"]) and
                    0 <= idx < len(sheet_data["width"]) and
                    0 <= idx < len(sheet_data["height"]) and
                    0 <= idx < len(sheet_data["Status"])
                ):
                    if wall_number not in identifier:
                        identifier[wall_number] = []

                    identifier[wall_number].append({
                        "sheet_name": stagetext,
                        "markingidentifiers": sheet_data["markingidentifiers"][idx],
                        "Position X (mm)": sheet_data["Position X (mm)"][idx],
                        "Position Y (mm)": sheet_data["Position Y (mm)"][idx],
                        "Position Z (mm)": sheet_data["Position Z (mm)"][idx],
                        "Shape type": sheet_data["Shape type"][idx],
                        "width": sheet_data["width"][idx],
                        "height": sheet_data["height"][idx],
                        "Status": sheet_data["Status"][idx],
                    })
        if wall not in wall_actors:
            if wall != "Floor":
                actor = create_wall_actor(
                    name=wall,
                    position=properties["position"],
                    size=properties["size"],
                    color=properties["color"],
                    rotation=properties["rotation"]
                )
            else:
                actor = create_floor_actor(
                    name=wall,
                    position=properties["position"],
                    points_list=properties["points"],
                    color=properties["color"],
                    rotation=properties["rotation"]
                )

            wall_actors[wall] = actor
            ren.AddActor(actor)

    # Setting visibility logic (after all walls are processed)
    if identifier:
        first_wall_number = min(identifier.keys(), key=lambda x: (x == "F", x))  # Numeric walls first, "F" last
        for wall_name in wall_actors:
            match = re.search(r'\d+', wall_name)
            wall_number = int(match.group()) if match else "F" if wall_name == "Floor" else None

            if wall_number == first_wall_number:
                wall_actors[wall_name].VisibilityOn()
                wallname = wall_name
                walllabel.setText(f"Wall : {wallname}") 
            else:
                wall_actors[wall_name].VisibilityOff()

    return wall_actors, identifier, wallname

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