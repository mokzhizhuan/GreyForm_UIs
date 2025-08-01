import pandas as pd
import numpy as np


def setuprobotposition(
    row,
    stage2_rows,
    walls,
    externalxmax_width,
    externalymax_width,
):
    pos_x, pos_y, pos_z = row["Position X"], row["Position Y"], row["Position Z"]
    wall_number, name = row["Wall Number"], row["Name"]
    if (
        (pos_x == 0 and pos_y == 0)
        or pos_x == externalxmax_width
        or pos_y == externalymax_width
    ):
        return pd.Series([None, None, None])
    matched_wall = None
    if str(wall_number).upper() == "F":
        if wall_number == "F" and "CP" not in name:
            for cp_row in stage2_rows:
                if "CP" in cp_row["Wall"] and cp_row["Wall Number"] == "F":
                    return pd.Series(
                        [
                            pos_x - cp_row["Position X"],
                            pos_y - cp_row["Position Y"],
                            pos_z + cp_row["Position Z"],
                        ]
                    )
    elif isinstance(wall_number, int) and 1 <= wall_number <= len(walls):
        matched_wall = walls[wall_number - 1]
    else:
        matched_wall = None
    if matched_wall is None:
        return pd.Series([pos_x, pos_y, pos_z])
    wall_info = list(matched_wall.values())[0]
    facing = wall_info.get("facingaxis", "")
    if "CP" not in name:
        for cp_row in stage2_rows:
            if "CP" in cp_row["Wall"] and cp_row["Wall Number"] == wall_number:
                cp_x = cp_row["Position X"]
                cp_y = cp_row["Position Y"]
                cp_z = cp_row["Position Z"]
                dz = pos_z - cp_z
                if dz < -1000:
                    return pd.Series([None, None, None])
                if facing in ["+X", "-X"]:
                    dx = pos_x - cp_x
                    dy = pos_y - cp_y
                    """if dy == -abs(ymaxwidth):
                        dy = 0"""
                    if facing == "-X":
                        if dx > 0:
                            dx = -abs(dx)
                        else:
                            dx = abs(dx)
                    return pd.Series([dx, dy, dz])
                elif facing in ["+Y", "-Y"]:
                    dy = pos_y - cp_y
                    dx = pos_x - cp_x
                    """if dx == -abs(xmaxwidth):
                        dx = 0"""
                    if facing == "-Y":
                        if dy > 0:
                            dy = -abs(dy)
                        else:
                            dy = abs(dy)
                    return pd.Series([dx, dy, dz])
    return pd.Series([pos_x, pos_y, pos_z])


def setuprobotposition_fitting(
    row,
    stage2_rows,
    walls,
    externalxmax_width,
    externalymax_width,
):
    pos_x, pos_y, pos_z = row["Position X"], row["Position Y"], row["Position Z"]
    if (pos_x == 0 and pos_y == 0) or (
        pos_x == externalxmax_width or pos_y == externalymax_width
    ):
        return pd.Series([None, None, None])
    wall_number, name = row["Wall Number"], row["Name"]
    matched_wall = None
    if str(wall_number).upper() == "F":
        if wall_number == "F" and "CP" not in name:
            for cp_row in stage2_rows:
                if "CP" in cp_row["Wall"] and cp_row["Wall Number"] == "F":
                    return pd.Series(
                        [
                            pos_x - cp_row["Position X"],
                            pos_y - cp_row["Position Y"],
                            pos_z + cp_row["Position Z"],
                        ]
                    )
    elif isinstance(wall_number, int) and 1 <= wall_number <= len(walls):
        matched_wall = walls[wall_number - 1]
    else:
        matched_wall = None
    if matched_wall is None:
        return pd.Series([pos_x, pos_y, pos_z])
    wall_info = list(matched_wall.values())[0]
    facing = wall_info.get("facingaxis", "")
    if "CP" not in name:
        for cp_row in stage2_rows:
            if "CP" in cp_row["Wall"] and cp_row["Wall Number"] == wall_number:
                cp_x = cp_row["Position X"]
                cp_y = cp_row["Position Y"]
                cp_z = cp_row["Position Z"]
                if facing in ["+X", "-X"]:
                    dx = pos_x - cp_x
                    dy = pos_y - cp_y
                    dz = pos_z - cp_z
                    if facing == "-X":
                        if dx > 0:
                            dx = -abs(dx)
                        else:
                            dx = abs(dx)
                    return pd.Series([dx, dy, dz])
                elif facing in ["+Y", "-Y"]:
                    dy = pos_y - cp_y
                    dx = pos_x - cp_x
                    dz = pos_z - cp_z
                    if facing == "-Y":
                        if dy > 0:
                            dy = -abs(dy)
                        else:
                            dy = abs(dy)
                    return pd.Series([dy, dx, dz])
    return pd.Series([pos_x, pos_y, pos_z])


def setupfittingrequirement(row, all_objs, fitting_boundingbox, checklist):
    pos_x, pos_y, pos_z = row["Position X"], row["Position Y"], row["Position Z"]
    for f in fitting_boundingbox:
        for obj in all_objs:
            if f["Name"] in obj["name"]:
                if obj["type"] in ["IfcFlowTerminal", "IfcBuildingElementProxy"]:
                    if row["Name"] in f["Name"]:
                        row_name = str(row["Name"])
                        matched = checklist[
                            checklist["Name"]
                            .astype(str)
                            .apply(lambda x: x.lower() in row_name.lower())
                        ]
                        if not matched.empty:
                            remarks = matched["Remarks"].astype(str).values[0]
                            if "center point" in remarks.lower():
                                pos_z = pos_z + f["Size"][2] / 2
                                vertices = obj.get("vertices")
                                x_coords = vertices[:, 0]  # extract X coordinates
                                min_x, max_x = np.min(x_coords), np.max(x_coords)
                                if min_x + max_x > 0:
                                    pos_x = pos_x + f["Size"][0] / 2
    return pd.Series([round(pos_x), round(pos_y), round(pos_z)])
