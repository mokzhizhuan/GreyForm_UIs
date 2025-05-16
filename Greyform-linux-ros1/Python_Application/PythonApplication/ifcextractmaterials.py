import numpy as np


def shapesformat(wallsformat):
    centers = np.array([w["center"] for w in wallsformat])
    x_min, x_max = centers[:, 0].min(), centers[:, 0].max()
    y_min, y_max = centers[:, 1].min(), centers[:, 1].max()
    x_range = x_max - x_min
    y_range = y_max - y_min
    south = [w for w in wallsformat if w["center"][1] < y_min + y_range * 0.3]
    north = [w for w in wallsformat if w["center"][1] > y_min + y_range * 0.7]
    remaining = [w for w in wallsformat if w not in south + north]
    west = [w for w in remaining if w["center"][0] < x_min + x_range * 0.3]
    east = [w for w in remaining if w["center"][0] > x_min + x_range * 0.7]
    south.sort(key=lambda w: w["center"][0])  # A
    west.sort(key=lambda w: -w["center"][0])  # B
    north.sort(key=lambda w: w["center"][0])  # C, E
    east.sort(key=lambda w: -w["center"][1])  # D (top), F (bottom)
    label_map = []
    label_letters = iter("ABCDEF")
    counter = 1
    # South (front, left → right)
    if south:
        south.sort(key=lambda w: w["center"][0])
        for wall in south:
            axis = detect_axis(wall["mesh"])
            label_map.append(
                (next(label_letters), wall, "South", axis, f"Wall {counter}")
            )
            counter += 1
    # West (left, bottom → top)
    if west:
        west.sort(key=lambda w: w["center"][1])
        for wall in west:
            axis = detect_axis(wall["mesh"])
            label_map.append(
                (next(label_letters), wall, "West", axis, f"Wall {counter}")
            )
            counter += 1
    # North (back, left → right)
    if north:
        north.sort(key=lambda w: w["center"][0])
        for wall in north:
            axis = detect_axis(wall["mesh"])
            label_map.append(
                (next(label_letters), wall, "North", axis, f"Wall {counter}")
            )
            counter += 1
    # East (right, top → bottom)
    if east:
        east.sort(key=lambda w: -w["center"][1])
        for wall in east:
            axis = detect_axis(wall["mesh"])
            label_map.append(
                (next(label_letters), wall, "East", axis, f"Wall {counter}")
            )
            counter += 1
    label_map.sort(key=lambda x: x[0])
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
        curr_label, curr_wall, curr_elevation, curr_axis, name = label_map[i]
        next_label, next_wall, next_elevation, next_axis, name = label_map[
            (i + 1) % num_walls
        ]
        curr_center = curr_wall["center"]
        next_center = next_wall["center"]
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

def get_x_y(label_map, wall_dimensions, wall_height):
    x_widths = []  # for labels A, C, E (even index)
    y_heights = []  # for labels B, D, F (odd index)
    top_two = []
    for i, (label, wall, direction, axiss, wall_name) in enumerate(label_map):
        wall_name = wall["name"]
        if wall_name in wall_dimensions:
            wall_dimensions[wall_name]["label"] = label
            width = wall_dimensions[wall_name].get("width", 0)
            if i % 2 == 0:
                x_widths.append(width)
            else:  # Odd labels: B, D, F → Y axis
                y_heights.append(width)
    top_two = [
        max(x_widths) + (wall_height * 2) if x_widths else 0,
        max(y_heights) if y_heights else 0,
    ]
    return top_two

# include error in text file
def log_error(self, message):
    with open("error_log.txt", "a") as log_file:
        log_file.write(message + "\n")

def log(self, message):
    with open("log.txt", "a") as log_file:
        log_file.write(message + "\n")
