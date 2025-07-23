import pandas as pd
import numpy as np

def setuprobotposition(row, stage2_rows, walls , xmaxwidth , ymaxwidth):
    pos_x, pos_y, pos_z = row["Position X"], row["Position Y"], row["Position Z"]
    wall_number = row["Wall Number"]
    name = row["Name"]
    matched_wall, getextrusion = None, None
    # Determine the wall dict to use
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
        if isinstance(wall_number, int) and 1 <= wall_number <= len(walls):
            getextrusion = walls[wall_number - 2]
        else:
            getextrusion = walls[len(walls)]
    else:
        matched_wall = None
    if matched_wall is None:
        return pd.Series([pos_x, pos_y, pos_z])
    wall_info = list(matched_wall.values())[0]
    facing = wall_info.get("facingaxis", "")
    if "CP" not in name:
        for i ,cp_row in enumerate(stage2_rows):
            if "CP" in cp_row["Wall"] and cp_row["Wall Number"] == wall_number:
                width = list(getextrusion.values())[0]["area"][0]
                cp_x = cp_row["Position X"]
                cp_y = cp_row["Position Y"]
                cp_z = cp_row["Position Z"]
                if facing in ["+X", "-X"]:
                    dx = pos_x - cp_x
                    dy = ymaxwidth - width
                    if dy == ymaxwidth:
                        dy =  0
                    dz = pos_z - cp_z
                    if facing == "-X":
                        if dx > 0:
                            dx = -abs(dx)
                        else:
                            dx = abs(dx)
                    return pd.Series([dx, dy, dz])
                elif facing in ["+Y", "-Y"]:
                    dy = pos_y - cp_y
                    dx = xmaxwidth - width
                    if dx == xmaxwidth:
                        dx = 0
                    dz = pos_z - cp_z
                    if facing == "-Y":
                        if dy > 0:
                            dy = -abs(dy)
                        else:
                            dy = abs(dy)
                    return pd.Series([dy, dx, dz])
    return pd.Series([pos_x, pos_y, pos_z])

def setuprobotposition_fitting(row, stage2_rows, walls , xmaxwidth , ymaxwidth):
    pos_x, pos_y, pos_z = row["Position X"], row["Position Y"], row["Position Z"]
    wall_number = row["Wall Number"]
    name = row["Name"]
    matched_wall = None
    # Determine the wall dict to use
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
        if isinstance(wall_number, int) and 1 <= wall_number <= len(walls):
            getextrusion = walls[wall_number - 2]
        else:
            getextrusion = walls[len(walls)]
    else:
        matched_wall = None
    if matched_wall is None:
        return pd.Series([pos_x, pos_y, pos_z])
    wall_info = list(matched_wall.values())[0]
    facing = wall_info.get("facingaxis", "")
    if "CP" not in name:
        for cp_row in stage2_rows:
            if "CP" in cp_row["Wall"] and cp_row["Wall Number"] == wall_number:
                width = list(getextrusion.values())[0]["area"][0]
                cp_x = cp_row["Position X"]
                cp_y = cp_row["Position Y"]
                cp_z = cp_row["Position Z"]
                if facing in ["+X", "-X"]:
                    dx = pos_x - cp_x
                    dy = pos_y - ymaxwidth
                    if width == ymaxwidth:
                        if dy < 0:
                            dy = dy + ymaxwidth
                    dz = pos_z - cp_z
                    if facing == "-X":
                        if dx > 0:
                            dx = -abs(dx)
                        else:
                            dx = abs(dx)
                    return pd.Series([dx, dy, dz])
                elif facing in ["+Y", "-Y"]:
                    dy = pos_y - cp_y
                    dx = pos_x - xmaxwidth
                    if width == xmaxwidth:
                        if dx < 0:
                            dx = dx + xmaxwidth
                    dz = pos_z - cp_z
                    if facing == "-Y":
                        if dy > 0:
                            dy = -abs(dy)
                        else:
                            dy = abs(dy)
                    return pd.Series([dy, dx, dz])
    return pd.Series([pos_x, pos_y, pos_z])

def setupfittingrequirement(row, all_objs , fitting_boundingbox , checklist):
    pos_x, pos_y, pos_z = row["Position X"], row["Position Y"], row["Position Z"]
    for f in fitting_boundingbox:
        for obj in all_objs:
            if f["Name"] in obj["name"]:
                if obj["type"] in ["IfcFlowTerminal", "IfcBuildingElementProxy"]:
                    if row["Name"] in f["Name"]:
                        row_name = str(row["Name"]) 
                        matched = checklist[
                            checklist["Name"].astype(str).apply(lambda x: x.lower() in row["Name"].lower())
                        ]
                        if not matched.empty:
                            remarks = matched["Remarks"].astype(str).values[0]
                            if "center point" in remarks.lower():
                                pos_z = pos_z + f["Size"][2]/2
                                vertices = obj.get("vertices")
                                x_coords = vertices[:, 0]  # extract X coordinates
                                min_x = np.min(x_coords)
                                max_x = np.max(x_coords)
                                if min_x + max_x > 0:
                                    pos_x = pos_x + f["Size"][0]/2
    return pd.Series([round(pos_x), round(pos_y), round(pos_z)])

# convert to other wall number for rotation
def apply_rotation_to_markers(df):
    if "Name" not in df.columns or df.empty:
        return df
    shape_types = []
    stages = []
    for name in df["Name"]:
        marker = "?"
        stage = "?"
        if isinstance(name, str):
            if name.startswith("TMP"):
                is_tmp7 = name[3:4] == "7"
                is_subtype = name[8:9] == "s"
                if is_tmp7 and is_subtype:
                    stage = 4 if "b" in name else 3
                elif "T" in name:
                    stage = 2
                    marker = "T"
                elif "+" in name:
                    stage = 1
                    marker = "+"
                elif "6" in name:
                    stage = 6
                    marker = "6"
            elif "6" in name:
                stage = 6
                marker = "6"
        shape_types.append(marker)
    df["Shape Type"] = shape_types
    return df

