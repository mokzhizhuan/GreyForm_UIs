import numpy as np
import re
import ifcopenshell
import math


def shapesformat(wall_objects, opening_wall_objects, scale_factor=1000.0):
    counter = 1
    closest_wall = None
    label_map = []
    unvisited = wall_objects.copy()
    starting_wall = None
    for opening_wall in opening_wall_objects:
        opening_wall_name = opening_wall["name"]
        opening_wall_vertices = opening_wall["vertices"]
        max_x = max(opening_wall_vertices[:, 0])
        min_x = min(opening_wall_vertices[:, 0])
        if max_x - min_x <= scale_factor:
            closest_wall = None
            starting_wall = next(
                (w for w in unvisited if w["name"] == opening_wall_name), None
            )
            if not starting_wall:
                continue
            unvisited.remove(starting_wall)
            axis = detect_axis(starting_wall["mesh"])
            label_map = [
                {
                    f"Wall {counter}": starting_wall,
                    "axis": axis,
                    "center": starting_wall["mesh"].center,
                }
            ]
            current_wall = starting_wall
            while unvisited:
                closest_wall, dist = find_closest_wall(current_wall, unvisited)
                if not closest_wall:
                    break
                axis = detect_axis(closest_wall["mesh"])
                label_map.append(
                    {
                        f"Wall {counter+1}": closest_wall,
                        "axis": axis,
                        "center": closest_wall["mesh"].center,
                    }
                )
                unvisited.remove(closest_wall)
                current_wall = closest_wall
                counter += 1
        elif len(opening_wall_objects) == 1:
            starting_wall = next((w for w in unvisited if w["name"] == opening_wall_name), None)
            if not starting_wall:
                continue 
            unvisited.remove(starting_wall)
            visited = [{f"Wall {counter}": starting_wall}]
            current_wall = starting_wall
            current_wall = starting_wall
            while unvisited:
                closest_wall, dist = find_closest_wall(current_wall, unvisited)
                if not closest_wall:
                    break
                visited.append({f"Wall {counter+1}": closest_wall}) 
                unvisited.remove(closest_wall)
                current_wall = closest_wall
                counter += 1
    return label_map


def detect_axis(mesh):
    bounds = mesh.bounds
    x_range = abs(bounds[1] - bounds[0])
    y_range = abs(bounds[3] - bounds[2])
    return "X" if x_range >= y_range else "Y"


def calculate_wall_directions(label_map):
    directions = []
    num_walls = len(label_map)
    for i in range(num_walls):
        curr_item = label_map[i]
        next_item = label_map[(i + 1) % num_walls]
        curr_label = list(curr_item.keys())[0]  # "Wall 1"
        curr_wall = curr_item[curr_label]
        curr_axis = curr_item["axis"]
        curr_center = curr_item["center"]
        next_label = list(next_item.keys())[0]  # "Wall 2"
        next_wall = next_item[next_label]
        next_center = next_item["center"]
        dx = next_center[0] - curr_center[0]
        dy = next_center[1] - curr_center[1]
        if curr_axis == "X":
            direction = "+X" if dx > 0 else "-X"
        elif curr_axis == "Y":
            direction = "+Y" if dy > 0 else "-Y"
        else:
            if abs(dx) > abs(dy):
                direction = "+X" if dx > 0 else "-X"
            else:
                direction = "+Y" if dy > 0 else "-Y"
        directions.append((curr_label, next_label, direction))
    return directions

def find_closest_wall(current_wall, wall_pool):
    x1, y1 = float(current_wall["x"]), float(current_wall["y"])
    min_dist = float("inf")
    closest_wall = None
    for wall in wall_pool:
        if wall["name"] == current_wall["name"]:
            continue
        x2, y2 = float(wall["x"]), float(wall["y"])
        dist = math.hypot(x2 - x1, y2 - y1)
        if dist < min_dist:
            min_dist = dist
            closest_wall = wall
    return closest_wall, min_dist

def get_x_y(label_map, wall_dimensions, wall_height):
    x_widths = []
    y_heights = []
    top_two = []
    for i, wall_item in enumerate(label_map):
        label = list(wall_item.keys())[0]         # e.g., "Wall 1"
        wall = wall_item[label]                   # wall dict
        axis = wall_item.get("axis", None)        # "X" or "Y"
        wall_name = wall.get("name", "")
        if wall_name in wall_dimensions:
            wall_dimensions[wall_name]["label"] = label
            width = wall_dimensions[wall_name].get("width", 0)
            if axis == "X":
                x_widths.append(width)
            elif axis == "Y":
                y_heights.append(width)
    if len(label_map) == 6:
        top_two = [
            max(x_widths) + (wall_height * 2) if x_widths else 0,
            max(y_heights) if y_heights else 0,
        ]
    else:
        top_two = [
            max(x_widths) if x_widths else 0,
            max(y_heights) + wall_height if y_heights else 0,
        ]
    return top_two

# include error in text file
def log_error(message):
    with open("error_log.txt", "a") as log_file:
        log_file.write(message + "\n")


def log(message):
    with open("log.txt", "a") as log_file:
        log_file.write(message + "\n")

def openings(ifc_file):
    openings = ifc_file.by_type("IfcOpeningElement")
    opening_wall_objects = []
    for opening in openings:
        opening_name = opening.Name
        if "basic wall:bss.50" in opening_name.lower():
            x, y, z = (0, 0, 0)
            if opening.ObjectPlacement:
                placement = opening.ObjectPlacement.RelativePlacement
                if placement and placement.Location:
                    x, y, z = placement.Location.Coordinates
            scale_factor = 1000.0
            scaled_grouped_verts = 0
            if opening.Representation is not None:
                settings = ifcopenshell.geom.settings()
                shape = ifcopenshell.geom.create_shape(settings, opening)
                verts = shape.geometry.verts
                grouped_verts = [
                    [verts[i], verts[i + 1], verts[i + 2]]
                    for i in range(0, len(verts), 3)
                ]
                scaled_grouped_verts = np.array(grouped_verts) * scale_factor
                scaled_grouped_verts = scaled_grouped_verts.astype(int)
            opening_wall_objects.append(
                {
                    "name": opening_name,
                    "x": x,
                    "y": y,
                    "z": z,
                    "vertices": scaled_grouped_verts,
                }
            )
    return opening_wall_objects
