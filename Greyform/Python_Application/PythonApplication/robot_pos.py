import pandas as pd
import numpy as np


def setuprobotposition(row, stage2_rows, walls, xmaxwidth, ymaxwidth):
    pos_x, pos_y, pos_z = row["Position X"], row["Position Y"], row["Position Z"]
    wall_number, name = row["Wall Number"], row["Name"]
    extrusion_width, matched_wall = 0, None
    if str(wall_number).upper() == "F":
        if wall_number == "F" and "CP" not in name:
            for cp_row in stage2_rows:
                if "CP" in cp_row["Wall"] and cp_row["Wall Number"] == "F":
                    return pd.Series(
                        [
                            pos_x - cp_row["Position X"],
                            pos_y - cp_row["Position Y"],
                            pos_z,
                        ]
                    )
    elif isinstance(wall_number, int) and 1 <= wall_number <= len(walls):
        matched_wall = walls[wall_number - 1]
        if isinstance(wall_number, int) and 1 <= wall_number <= len(walls) / 2:
            getextrusion = walls[wall_number - 2]
        elif wall_number <= len(walls):
            if wall_number == len(walls):
                getextrusion = walls[wall_number - len(walls)]
            else:
                getextrusion = walls[wall_number]
        else:
            getextrusion = walls[len(walls)]
        getextrusion_index = walls.index(getextrusion)
        matched_cp = next(
            (
                row
                for row in stage2_rows
                if row.get("Wall Number") == getextrusion_index + 1
            ),
            None,
        )
        if matched_cp:
            extrusion_width = matched_cp.get("Width")
    else:
        matched_wall = None
    if matched_wall is None:
        return pd.Series([pos_x, pos_y, pos_z])
    wall_info = list(matched_wall.values())[0]
    facing = wall_info.get("facingaxis", "")
    if "CP" not in name:
        for cp_row in stage2_rows:
            if "CP" in cp_row["Wall"] and cp_row["Wall Number"] == wall_number:
                width = extrusion_width
                cp_x = cp_row["Position X"]
                cp_y = cp_row["Position Y"]
                cp_z = cp_row["Position Z"]
                if facing in ["+X", "-X"]:
                    dx = pos_x - cp_x
                    dy = -abs(ymaxwidth - width)
                    if dy == -abs(ymaxwidth):
                        dy = 0
                    dz = pos_z - cp_z
                    if facing == "-X":
                        if dx > 0:
                            dx = -abs(dx)
                        else:
                            dx = abs(dx)
                    return pd.Series([dx, dy, dz])
                elif facing in ["+Y", "-Y"]:
                    dy = pos_y - cp_y
                    dx = -abs(xmaxwidth - width)
                    if dx == -abs(xmaxwidth):
                        dx = 0
                    dz = pos_z - cp_z
                    if facing == "-Y":
                        if dy > 0:
                            dy = -abs(dy)
                        else:
                            dy = abs(dy)
                    return pd.Series([dy, dx, dz])
    return pd.Series([pos_x, pos_y, pos_z])


def setuprobotposition_fitting(
    row, stage2_rows, walls, xmaxwidth, ymaxwidth, dist_needed
):
    pos_x, pos_y, pos_z = row["Position X"], row["Position Y"], row["Position Z"]
    wall_number, name = row["Wall Number"], row["Name"]
    extrusion_width, matched_wall = 0, None
    matched_distance = None
    for distances in dist_needed:
        if distances["Name"] in name:
            matched_distance = distances["distance"]
    if str(wall_number).upper() == "F":
        if wall_number == "F" and "CP" not in name:
            for cp_row in stage2_rows:
                if "CP" in cp_row["Wall"] and cp_row["Wall Number"] == "F":
                    return pd.Series(
                        [
                            pos_x - cp_row["Position X"],
                            pos_y - cp_row["Position Y"],
                            pos_z,
                        ]
                    )
    elif isinstance(wall_number, int) and 1 <= wall_number <= len(walls):
        matched_wall = walls[wall_number - 1]
        if isinstance(wall_number, int) and 1 <= wall_number <= len(walls) / 2:
            getextrusion = walls[wall_number - 2]
        elif wall_number <= len(walls):
            if wall_number == len(walls):
                getextrusion = walls[wall_number - len(walls)]
            else:
                getextrusion = walls[wall_number]
        else:
            getextrusion = walls[len(walls)]
        getextrusion_index = walls.index(getextrusion)
        matched_cp = next(
            (
                row
                for row in stage2_rows
                if row.get("Wall Number") == getextrusion_index + 1
            ),
            None,
        )
        if matched_cp:
            extrusion_width = matched_cp.get("Width")
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
                    dy = -abs((ymaxwidth - extrusion_width) + matched_distance)
                    dz = pos_z - cp_z
                    if facing == "-X":
                        if dx > 0:
                            dx = -abs(dx)
                        else:
                            dx = abs(dx)
                    return pd.Series([dx, dy, dz])
                elif facing in ["+Y", "-Y"]:
                    dy = pos_y - cp_y
                    dx = -abs((xmaxwidth - extrusion_width) + matched_distance)
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
                                min_x ,max_x= np.min(x_coords) , np.max(x_coords)
                                if min_x + max_x > 0:
                                    pos_x = pos_x + f["Size"][0] / 2
    return pd.Series([round(pos_x), round(pos_y), round(pos_z)])
