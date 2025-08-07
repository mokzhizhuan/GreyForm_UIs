from PyQt5 import QtCore, QtWidgets, QtOpenGL, QtGui, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import vtk
from vtk import *
from vtkmodules.vtkCommonColor import vtkNamedColors
import re



def setupactors(
    walls,
    stagetext,
    wall_identifiers,
    ren,
    walllabel,
    robotplacement,
    objectrobot,
):
    identifier = {}
    wall_actors = {}
    wallname = None  # Initialize wallname to ensure valid return
    for wall, properties in walls.items():
        if wall == "Floor":
            wall_number = "F"  # Special case for Floor
        else:
            match = re.search(r"\d+", wall)
            wall_number = int(match.group()) if match else None
        if wall_number is None or stagetext not in wall_identifiers:
            continue
        sheet_data = wall_identifiers[stagetext]
        sheet_data = {
            col.strip().replace('\u00A0', ''): values
            for col, values in sheet_data.items()
        }
        if wall_number == "F":
            indexes = [i for i, wn in enumerate(sheet_data["Wall Number"]) if wn == "F"]
        else:
            indexes = [
                i for i, wn in enumerate(sheet_data["Wall Number"]) if wn == wall_number
            ]
        if not indexes:
            continue
        for idx in indexes:
            if (
                0 <= idx < len(sheet_data["markingidentifiers"])
                and 0 <= idx < len(sheet_data["Position X"])
                and 0 <= idx < len(sheet_data["Position Y"])
                and 0 <= idx < len(sheet_data["Position Z"])
                and 0 <= idx < len(sheet_data["Shape Type"])
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
                        "Position X": sheet_data["Position X"][idx],
                        "Position Y": sheet_data["Position Y"][idx],
                        "Position Z": sheet_data["Position Z"][idx],
                        "Shape Type": sheet_data["Shape Type"][idx],
                        "width": sheet_data["width"][idx],
                        "height": sheet_data["height"][idx],
                        "Status": sheet_data["Status"][idx],
                    }
                )
        if wall not in wall_actors:
            for wall, properties in walls.items():
                if wall not in wall_actors:
                    actor = None
                    floor_properties = walls["Floor"]
                    floor_actor = create_floor_actor(
                        name="FloorPlaceholder",
                        position=floor_properties["position"],
                        points_list=floor_properties["points"],
                        color=floor_properties["color"],
                        rotation=floor_properties["rotation"],
                    )
                    ren.AddActor(floor_actor)
                    position_map = robotplacement[0]
                    for wall_name in position_map:
                        if wall_name != "Floor":
                            position = position_map[wall_name]
                            actor = create_robot_actor(
                                name=wall_name,
                                position=position,
                                size=objectrobot,
                                color=(0.8, 0.2, 0.2),
                                rotation=(0, 0, 0),
                            )
                            wall_actors[wall_name] = actor
                            ren.AddActor(actor)
                        else:
                            floor_positions = robotplacement[0].get("Floor", [])
                            wall_actors["Floor"] = []  # initialize as list
                            for i, pos in enumerate(floor_positions):
                                offset_pos = [pos[0], pos[1], pos[2] + (i * 200)]  # e.g., separate in Z
                                actor = create_robot_actor(
                                    name=f"Floor_{i+1}",
                                    position=offset_pos,
                                    size=objectrobot,
                                    color=(0.3, 0.6, 0.9),
                                    rotation=(0, 0, 0),
                                )
                                actor.VisibilityOff()  # only show one later
                                wall_actors["Floor"].append(actor)
                                ren.AddActor(actor)
    if identifier:
        first_wall_number = min(identifier.keys(), key=lambda x: (x == "F", x))
        for wall_name in wall_actors:
            match = re.search(r"\d+", wall_name)
            wall_number = (
                int(match.group()) if match else "F" if  wall_name == "Floor" else None
            )
            if wall_number == first_wall_number:
                wall_actors[wall_name].VisibilityOn()
                wallname = wall_name  # Set the valid wallname
                walllabel.setText(f"Wall : {wallname}")
    if wallname is None:
        if identifier:
            first_wall_number = min(identifier.keys(), key=lambda x: (x == "F", x))
            wallname = f"Wall {first_wall_number}"
    return wall_actors, identifier, wallname


def create_robot_actor(name, position, size, color, rotation=(0, 0, 0)):
    cube = vtk.vtkCubeSource()
    cube.SetXLength(size[0])
    cube.SetYLength(size[1])
    cube.SetZLength(size[2])
    cube.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cube.GetOutputPort())
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


def setactor(mapper):
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetRepresentationToSurface()
    colorsd = vtkNamedColors()
    actor.GetProperty().SetColor((230 / 255), (230 / 255), (250 / 255))
    actor.GetProperty().SetColor((230 / 255), (230 / 255), (250 / 255))
    actor.GetProperty().SetDiffuseColor(colorsd.GetColor3d("LightSteelBlue"))
    actor.GetProperty().SetDiffuse(0.8)
    actor.GetProperty().SetSpecular(0.3)
    actor.GetProperty().SetSpecularPower(60.0)
    actor.GetProperty().BackfaceCullingOn()
    actor.GetProperty().FrontfaceCullingOn()
    return actor


def polyDataToActor(reader):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(reader)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetRepresentationToSurface()
    return actor


def create_floor_actor(name, position, points_list, color, rotation):
    stlpath = "floor.stl"
    reader = vtk.vtkSTLReader()
    reader.SetFileName(stlpath)
    reader.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.name = name
    actor.VisibilityOn()
    return actor


def switch_to_robot_view(robot_name, ren, wall_actors, renderwindowinteractor, index=0):
    actor_entry = wall_actors.get(robot_name)
    if actor_entry is None:
        print(f"[Warning] No actor found for: {robot_name}")
        return
    if isinstance(actor_entry, list):
        if index >= len(actor_entry):
            print(f"[Warning] Index {index} out of range for actor list: {robot_name}")
            return
        actor = actor_entry[index]
    else:
        actor = actor_entry
    bounds = actor.GetBounds()
    x_center = (bounds[0] + bounds[1]) / 2
    y_center = (bounds[2] + bounds[3]) / 2
    z_center = (bounds[4] + bounds[5]) / 2
    camera = vtk.vtkCamera()
    camera.SetPosition(x_center, y_center, z_center + 1000)  # top-down view
    camera.SetFocalPoint(x_center, y_center, z_center)
    camera.SetViewUp(0, 1, 0)
    camera.ParallelProjectionOn()
    camera.SetParallelScale((bounds[3] - bounds[2]) * 2)
    ren.SetActiveCamera(camera)
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
    rotation_map = {"X": (90, 0, 90), "Y": (0, 90, 90)}
    camera_actors = {}
    for i, wall_dict in enumerate(wallformat):  # i will be used as numeric color index
        for wall_id, wall_data in wall_dict.items():
            axis = wall_data["axis"]
            width = wall_data["area"][0]  # safer to use actual area width
            height = wall_data["area"][2]  # use actual height
            pos_x_range = wall_data.get("pos_x_range", [wall_data["x"], wall_data["x"] + width])
            pos_y_range = wall_data.get("pos_y_range", [wall_data["y"], wall_data["y"] + width])

            position = (
                (pos_x_range[0] + pos_x_range[1]) / 2,
                (pos_y_range[0] + pos_y_range[1]) / 2,
                0,
            )
            size = (width, height)
            color = color_map[i % len(color_map)]
            rotation = rotation_map.get(axis, (0, 0, 0))
            camera_position = (
                position[0] + 100 if axis == "X" else position[0],
                position[1] + 100 if axis == "Y" else position[1],
                height / 2,
            )
            camera_actors[f"Camera Wall {i+1}"] = {
                "position": camera_position,
                "focal_point": position,
                "view_up": (0, 0, 1),
            }
            walls[f"Wall {i+1}"] = {
                "position": position,
                "size": size,
                "color": color,
                "rotation": rotation,
            }
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

