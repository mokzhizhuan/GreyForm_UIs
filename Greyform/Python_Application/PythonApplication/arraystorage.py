import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def stagecatergorize(ifc_file):
    data = {"Stage 1": [], "Stage 2": [], "Stage 3": []}

    def safe_get_name(element):
        return getattr(element, "Name", None)

    for element in ifc_file:
        name = safe_get_name(element)
        if element.is_a("IfcFlowSegment"):
            if name:
                data["Stage 1"].append(name)
        elif element.is_a("IfcCovering") or element.is_a("IfcWallStandardCase"):
            if name:
                data["Stage 2"].append(name)
        elif name and (
            "Shallow" in name
            or "Shower Door Hand Rail" in name
            or "Ceiling Access" in name
            or "GOMGO" in name
        ):
            data["Stage 2" if "Shallow" in name else "Stage 3"].append(name)
        elif (
            element.is_a("IfcDoor")
            or element.is_a("IfcFurnishingElement")
            or element.is_a("IfcSlab")
            or element.is_a("IfcFlowTerminal")
            or element.is_a("IfcFlowFitting")
        ):
            if name:
                if "Floor" in name or "Wall" in name:
                    data["Stage 2"].append(name)
                elif "BSS.Round" in name or "Elbow" in name or "M_Transition" in name:
                    data["Stage 1"].append(name)
                else:
                    data["Stage 3"].append(name)
    return data


def add_legends():
    dataframe_Legend = pd.read_excel("Pin Allocation BOM for PBU_T1a.xlsx", skiprows=2)
    pen_column = dataframe_Legend.columns[3]
    pin_id_column = dataframe_Legend.columns[9]
    dataframe_Legend = dataframe_Legend[[pen_column, pin_id_column]]
    if (
        pen_column in dataframe_Legend.columns
        and pin_id_column in dataframe_Legend.columns
    ):
        dataframe_Legend[pen_column].fillna("", inplace=True)
        dataframe_Legend[pin_id_column].fillna("", inplace=True)
        filtered_dataframe = dataframe_Legend[
            (dataframe_Legend[pen_column] != "")
            & (dataframe_Legend[pin_id_column] != "")
        ]
        wall_legend = filtered_dataframe.to_dict(orient="records")
        wall_name = "BSS.20mm Wall Finishes (600x600mm)"
        wall_600x600mm = []
        indexwall = 0
        index = 0
        for data_legend in wall_legend:
            data_pen_name = data_legend.get(pen_column)
            data_pin_id = data_legend.get(pin_id_column)
            if wall_name in data_pen_name:
                wall_600x600mm.append(
                    {
                        "Penetration/Fitting/Reference Point Name": data_pen_name,
                        "Pin ID": data_pin_id,
                    }
                )
    return wall_legend, pen_column, pin_id_column, wall_600x600mm, wall_name, indexwall


def wall_format(wall, floor, label_map):
    wall_format = {}
    axis = ""
    direction_groups = {}

    for label, wall_data, direction, axiss in label_map:
        wall_name = wall_data["name"]
        wall_width = wall[wall_name]["width"]
        direction_groups.setdefault(direction, []).append(wall_width)
    direction_max_width = {d: max(wlist) for d, wlist in direction_groups.items()}
    direction_totals = {d: sum(wlist) for d, wlist in direction_groups.items()}
    for index, (label, wall_data, direction, axiss) in enumerate(label_map, start=1):
        wall_name = wall_data["name"]
        wall_info = wall[wall_name]
        raw_width = wall_info["width"]
        height = wall_info["height"]
        depth = wall_info["depth"]
        if index % 2 == 0:
            axis = "y"
        else:
            axis = "x"
        if index == 1:
            final_width = raw_width + 2 * height
        elif raw_width == direction_max_width[direction]:
            if direction_totals[direction] in floor:
                final_width = raw_width  # keep it
            else:
                final_width = raw_width + height  # adjust
        else:
            final_width = raw_width  # not largest → no change

        wall_format[index] = {
            "axis": axis,
            "width": final_width,
            "height": depth + height + 10,
        }
        heighttotal = depth + height + 10
    return wall_format, heighttotal, height


def wall_format_finishes(wall):
    heights = []

    # Iterate through the walls to collect heights
    for index, (wall, dims) in enumerate(wall.items(), start=0):
        height = dims.get("height", None)
        if height is not None:
            heights.append(height)

    # Calculate max and min height if heights are collected
    if heights:
        max_height = max(heights)
        min_height = min(heights)
    else:
        max_height = min_height = "Not available"
    return max_height, min_height


def wall_format4sides(wall):
    wall_format = {}
    axis = ""
    for index, (wall, dims) in enumerate(wall.items(), start=0):
        width = dims.get("width", "Not available")
        depth = dims.get("depth", "Not available")
        height = dims.get("height", "Not available")
        if index % 2 == 0:
            axis = "y"
        else:
            axis = "x"
        if index + 1 in [2, 3]:
            wall_format[index + 1] = {
                "axis": axis,
                "width": width + height,
                "height": depth + height + 10,
            }
        elif index + 1 in [4]:
            wall_format[index + 1] = {
                "axis": axis,
                "width": width + (height * 2),
                "height": depth + height + 10,
            }
        else:
            wall_format[index + 1] = {
                "axis": axis,
                "width": width,
                "height": depth + height + 10,
            }
        heighttotal = depth + height + 10
    return wall_format, heighttotal
