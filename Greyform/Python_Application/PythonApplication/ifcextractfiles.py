import pandas as pd
import ifcopenshell.util.element as Element
from ifcopenshell.util.placement import get_local_placement, get_axis2placement
import PythonApplication.arraystorage as storingelement
import ifcopenshell
import numpy as np


def get_attribute_value(object_data, attribute):
    if "." not in attribute:
        return object_data[attribute]
    elif "." in attribute:
        pset_name = attribute.split(".", 1)[0]
        prop_name = attribute.split(".", -1)[1]
        if pset_name in object_data["PropertySets"].keys():
            if prop_name in object_data["PropertySets"][pset_name].keys():
                return object_data["PropertySets"][pset_name][prop_name]
            else:
                return None
        if pset_name in object_data["QuantitySets"].keys():
            if prop_name in object_data["QuantitySets"][pset_name].keys():
                return object_data["QuantitySets"][pset_name][prop_name]
            else:
                return None
    else:
        return None


# convert to other wall number for rotation
def apply_rotation_to_markers(worksheet, df_class):
    marker_col_index = df_class.columns.get_loc("Shape type")
    for row_idx, (name, marker) in enumerate(
        zip(df_class["Point number/name"], df_class["Shape type"]), start=1
    ):
        if pd.isna(marker) or marker == "":
            marker = "?"  # default placeholder or leave it as-is
        new_marker = marker  # Default fallback
        if isinstance(name, str) and name.startswith("TMP"):
            is_tmp7 = name[3:4] == "7"
            is_subtype = name[8:9] == "s"
            if is_tmp7 and is_subtype:
                if "b" in name:
                    new_marker = 4
                else:
                    new_marker = 3
            elif marker == "T":
                new_marker = 2
            elif marker == "+":
                new_marker = 1
            elif marker == "6":
                new_marker = 6
            worksheet.write(row_idx, marker_col_index + 1, new_marker)
        else:
            if marker == "6":
                new_marker = 6
            worksheet.write(row_idx, marker_col_index + 1, new_marker)


def add_pset_attributes(psets, pset_attributes):
    for pset_name, pset_data in psets.items():
        for property_name in pset_data.keys():
            pset_attributes.add(f"{pset_name}.{property_name}")


# error will send into the error log text
def log_error(message):
    with open("error_log.txt", "a") as log_file:
        log_file.write(message + "\n")


def log_text(message):
    with open("log.txt", "a") as log_file:
        log_file.write(message + "\n")


def get_objects_data_by_class(file, class_type):
    objects_data = []
    verts_data = []
    pset_attributes = set()
    objects = file.by_type(class_type)
    for object in objects:
        storey = None
        if object.is_a() != "IfcOpeningElement":
            wall_number = object.Tag if object.Tag else ""
            name = object.Name if object.Name else ""
            psets = Element.get_psets(object, psets_only=True)
            add_pset_attributes(psets, pset_attributes)
            qtos = Element.get_psets(object, qtos_only=True)
            add_pset_attributes(qtos, pset_attributes)
            placement_matrix = get_local_placement(object.ObjectPlacement)
            # Extract Vertices of Elements
            x, y, z = (0, 0, 0)
            if object.ObjectPlacement:
                placement = object.ObjectPlacement.RelativePlacement
                if placement and placement.Location:
                    x, y, z = placement.Location.Coordinates
            scale_factor = 1000.0
            if object.Representation is not None:
                settings = ifcopenshell.geom.settings()
                shape = ifcopenshell.geom.create_shape(settings, object)
                verts = shape.geometry.verts
                grouped_verts = [[verts[i], verts[i + 1], verts[i + 2]] for i in range(0, len(verts), 3)]
                scaled_grouped_verts = np.array(grouped_verts) * scale_factor
                scaled_grouped_verts = scaled_grouped_verts.astype(int)
            else:
                scaled_grouped_verts = []
            for rel in object.ContainedInStructure:
                if rel.RelatingStructure.is_a("IfcBuildingStorey"):
                    storey = rel.RelatingStructure
            if storey and "Ceiling" in storey.Name:
                continue
            if "CP" in name:
                z = abs(z)
            objects_data.append(
                {
                    "Stage": "",
                    "Marking type": object.is_a(),
                    "Point number/name": name,
                    "Position X (mm)": int(round(x)),
                    "Position Y (mm)": int(round(y)),
                    "Position Z (mm)": int(round(z)),
                    "Wall Number": str(wall_number),
                    "Shape type": "",
                    "Status": "blank",
                    "Quadrant": 1,
                    "Unnamed : 9": "",
                    "Width": "",
                    "Height": "",
                    "Orientation": "",
                    "Diameter": "",
                }
            )
            verts_data.append(
                {
                    "Point number/name": name,
                    "verticles" : scaled_grouped_verts,
                    "Position X (mm)": int(round(x)),
                    "Position Y (mm)": int(round(y)),
                    "Position Z (mm)": int(round(z)),
                    "PredefinedType" : Element.get_predefined_type(object),
                    "Level" : Element.get_container(object).Name if Element.get_container(object) else "",
                }
            )
    return objects_data , verts_data


def stagenumber(name):
    for prefix in ["CP", "LP", "SP"]:
        if prefix in name:
            index = name.index(prefix) + 4
            if index < len(name) and name[index].isdigit():
                return int(name[index])
    if "TMP" in name:
        index = name.index("TMP") + 5
        if index < len(name) and name[index].isdigit():
            return int(name[index])


def wallnumber(name):
    for prefix in ["CP", "LP", "SP"]:
        if prefix in name:
            index = name.index(prefix) + 2
            if index < len(name) and name[index].isdigit():
                return int(name[index])
    if "TMP" in name:
        index = name.index("TMP") + 3
        if index < len(name) and name[index].isdigit():
            return int(name[index])


def changemarkingtype(stage, markingtypes):
    if stage == "Stage 1":
        return markingtypes[0]
    elif stage == "Stage 2":
        return markingtypes[1]
    elif stage == "Stage 3":
        return markingtypes[2]
    else:
        return stage

def calculate_internaldimensionx(thickness, small_thickness, wallformat):
    small_thickness_range = range(small_thickness, thickness)
    x_max_values = [
        wall["pos_x_range"][1] for wall in wallformat.values() if wall["axis"] == "x"
    ]
    y_max_values = [
        wall["pos_y_range"][1] for wall in wallformat.values() if wall["axis"] == "y"
    ]
    y_min_values = [
        wall["pos_y_range"][0] for wall in wallformat.values() if wall["axis"] == "y"
    ]
    x_max = max(x_max_values)
    y_has_small_thickness = False
    for y_min, y_max in zip(y_min_values, y_max_values):
        for small_thickness in small_thickness_range:
            if (
                abs((y_max - y_min) - small_thickness) <= 10
                or abs((y_min + small_thickness) - y_max) <= 10
                or abs((y_max - small_thickness) - y_min) <= 10
                or abs((y_max - small_thickness) - (y_min + thickness)) <= 10
                or abs((y_max - thickness) - (y_min + small_thickness)) <= 10
                or abs((y_max - small_thickness) - (y_min + small_thickness)) <= 10
            ):
                y_has_small_thickness = True
                break
        if y_has_small_thickness:
            break
    if y_has_small_thickness:
        calculated_dimension1 = x_max - (thickness * 2)
        calculated_dimension2 = x_max - (thickness * 2)
        calculated_dimension3 = x_max - (thickness * 2)
    else:
        calculated_dimension1 = x_max - (small_thickness + thickness)
        calculated_dimension2 = x_max - (small_thickness * 2)
        calculated_dimension3 = x_max - (thickness * 2)
    internaldimensionx = None
    if (
        calculated_dimension3 > 0
        and calculated_dimension3 == calculated_dimension2
        or calculated_dimension3 == calculated_dimension1
    ):
        internaldimensionx = calculated_dimension3 + (thickness * 2)
        return internaldimensionx
    else:
        return calculated_dimension3 + (thickness * 2)

def addranges(floor , wall_height, wall_finishes_height, label_map, wallformat, axis_widths, directional_axes_axis):
    max_x, max_y = floor
    thickness = wall_height + wall_finishes_height
    direction_widths = {}
    direction_axes = {}
    for index, (label, wall_data, direction, axis, ____) in enumerate(
        label_map, start=1
    ):
        wall_width = wallformat[index]["width"]
        if (
            direction not in direction_widths
            or wall_width > direction_widths[direction]
        ):
            direction_widths[direction] = wall_width
            direction_axes[direction] = axis.lower()
        axis_widths[axis.lower()].append(wall_width)
    x_min, x_max = min(axis_widths["x"]), max(axis_widths["x"])
    y_min, y_max = min(axis_widths["y"]), max(axis_widths["y"])
    interior_x, interior_y = None, None
    direction_stack = []
    for index, (start, end, direction) in enumerate(directional_axes_axis):
        direction_stack.append(direction)
        count_minus_y = direction_stack.count("-Y")
        count_plus_y = direction_stack.count("+Y")
        if count_plus_y >= 2:
            interior_x = (x_max - (x_max - x_min), x_max)
            interior_y = (y_max - y_min, y_max)
            direction_stack.clear()
        elif count_minus_y >= 2:
            interior_x = (x_max - x_min, x_max)
            interior_y = (y_max - y_min, y_max)
            direction_stack.clear()
    directional_signs = {
        label: sign for label, _, sign in directional_axes_axis
    }
    for index, (_, _, direction, _, _) in enumerate(label_map, start=1):
        wall = wallformat[index]
        wall_width = wall["width"]
        axis = direction_axes[direction]
        is_exterior = wall_width == direction_widths[direction]
        next_index = index % len(label_map)
        next_label = label_map[next_index][0]
        next_sign = directional_signs.get(next_label, "")
        if is_exterior:
            if direction == "South":
                wall["pos_x_range"] = (0, wall_width)
                wall["pos_y_range"] = (0, thickness)
            elif direction == "North":
                if next_sign == "-Y" and next_index == 3:
                    wall["pos_x_range"] = (0, wall_width)
                    wall["pos_y_range"] = (max_y - thickness - (wall_height*11), max_y)
                else:
                    wall["pos_x_range"] = (interior_x[0], interior_x[1])
                    wall["pos_y_range"] = (max_y - thickness - (wall_height*11), max_y)
            elif direction == "West":
                if next_sign == "+Y":
                    wall["pos_x_range"] = (
                        interior_x[0] - thickness,
                        interior_x[1] - thickness,
                    )
                    wall["pos_y_range"] = (max_y - thickness, max_y)
                else:
                    wall["pos_x_range"] = (0, thickness)
                    wall["pos_y_range"] = (0, wall_width)
            elif direction == "East":
                wall["pos_x_range"] = (max_x - thickness, max_x)
                wall["pos_y_range"] = (0, wall_width)
        else:
            if direction == "North":
                wall["pos_x_range"] = (interior_x[0] - thickness, interior_x[0])
                wall["pos_y_range"] = (
                    interior_y[0] - thickness,
                    interior_y[1] - thickness,
                )
            elif direction == "East":
                wall["pos_x_range"] = (
                    interior_x[0] - thickness,
                    interior_x[1] - thickness,
                )
                wall["pos_y_range"] = (interior_y[0] - thickness, interior_y[0])
            elif direction == "South":
                wall["pos_x_range"] = (interior_x[0] - thickness, interior_x[0])
                wall["pos_y_range"] = (
                    interior_y[0] - thickness,
                    interior_y[1] - thickness,
                )
            elif direction == "West":
                if next_sign == "+Y":
                    wall["pos_x_range"] = (thickness, wall_width)
                    wall["pos_y_range"] = (interior_y[0] - thickness, interior_y[0])
                else:
                    wall["pos_x_range"] = (
                        interior_x[0] - thickness,
                        interior_x[1] - thickness,
                    )
                    wall["pos_y_range"] = (interior_y[0] - thickness, interior_y[0])
    return wallformat , axis_widths
