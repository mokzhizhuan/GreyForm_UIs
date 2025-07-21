import heapq
import pandas as pd
import methodifcfindings as ifc_findings

def assign_nearest_fitting(
    walls,
    fittings,
    storeys,
    floor,
    wall_info,
    ground,
    glass_walls,
    count_minus_y,
    count_plus_y,
    centerpoint_rows,
    origin_x,
    origin_y,
    wall_bss20,
    wall_bss12
):
    stage3_results = []
    top_twofloor_z = heapq.nlargest(2, (f["z"] for f in floor))
    lowest_floor = abs(min(f["z"] for f in floor) if floor else 0)
    storey_min_height = min(
        storeys, key=lambda s: s["elevation"], default={"elevation": 0}
    )["elevation"]
    ground_min_height = min(
        ground, key=lambda s: s["elevation"], default={"elevation": 0}
    )["elevation"]
    wall_finishes_lowest_height = min(
        wall_bss20, key=lambda s: s["z"], default={"z": 0}
    )["z"]
    combined_walls = wall_bss20 + wall_bss12
    shower_walls = [
        wall for wall in combined_walls
        if wall.get("z", 0) - wall_finishes_lowest_height == 0
    ]
    if glass_walls:
        glass_x_pos = glass_walls[0]["x"]
    width, height = 0, 0
    for fitting in fittings:
        fx, fy, fz = fitting["x"], fitting["y"], fitting["z"]
        min_dist = float("inf")
        nearestwallindex = 0
        for i, wall_dict in enumerate(walls):
            wall_data = list(wall_dict.values())[0]
            wx, wy = wall_data["x"], wall_data["y"]
            if wall_data["axis"] == "X":
                dist = abs(fy - wy)
            elif wall_data["axis"] == "Y":
                dist = abs(fx - wx)
            next_w, _ = ifc_findings.find_closest_wall_rotation(
                wall_data, wall_bss20 + wall_bss12
            )
            if len(walls) == 6:
                if count_minus_y == 2 and i > 0 and wx < glass_x_pos:
                    for row in centerpoint_rows:
                        if row["Wall Number"] == i + 1:
                            row["floortileheight"] = (
                                1000 + lowest_floor + top_twofloor_z[0]
                            )
                elif count_plus_y == 2 and i > 0 and wx > glass_x_pos:
                    for row in centerpoint_rows:
                        if row["Wall Number"] == i + 1:
                            row["floortileheight"] = (
                                1000 + lowest_floor + top_twofloor_z[0]
                            )
                if (
                    count_minus_y == 2
                    and i > 0
                    and wx < glass_x_pos
                    and dist < min_dist
                ):
                    min_dist = dist
                    nearestwallindex = i + 1
                elif (
                    count_plus_y == 2 and i > 0 and wx > glass_x_pos and dist < min_dist
                ):
                    min_dist = dist
                    nearestwallindex = i + 1
                elif dist < min_dist:
                    min_dist = dist
                    nearestwallindex = i + 1
            else:
                if dist < min_dist:
                    min_dist = dist
                    nearestwallindex = i + 1
        if fz >= storey_min_height:
            continue
        else:
            if next_w in shower_walls:
                if next_w["z"] + next_w["area"][1] >= fz <= next_w["z"]:
                    nearestwallindex = "F"
            elif fz < 0:
                nearestwallindex = "F"
        match = next(
            (w for w in wall_info if w["Wall Number"] == nearestwallindex), None
        )
        if match:
            width = match["Width"]
            height = match["Height"]
        stage3_results.append(
            {
                "Wall Number": nearestwallindex,
                "Name": fitting["name"],
                "Position X": fx + origin_x,
                "Position Y": fy + origin_y,
                "Position Z": fz,
                "Width": width,
                "Height": height,
            }
        )
    return stage3_results

def assign_nearest_fitting_rotation(
    walls,
    fittings,
    storeys,
    floor,
    wall_info,
    ground,
    glass_walls,
    count_minus_y,
    count_plus_y,
    centerpoint_rows,
    origin_x,
    origin_y,

):
    stage3_results = []
    top_twofloor_z = heapq.nlargest(2, (f["z"] for f in floor))
    lowest_floor = abs(min(f["z"] for f in floor) if floor else 0)
    storey_min_height = min(
        storeys, key=lambda s: s["elevation"], default={"elevation": 0}
    )["elevation"]
    ground_min_height = min(
        ground, key=lambda s: s["elevation"], default={"elevation": 0}
    )["elevation"]
    if glass_walls:
        glass_x_pos = glass_walls[0]["x"]
    width, height = 0, 0
    for fitting in fittings:
        fx, fy, fz = fitting["x"], fitting["y"], fitting["z"]
        min_dist = float("inf")
        nearestwallindex = 0
        Remark = ""
        remarkreq = 0
        for i, wall_dict in enumerate(walls):
            wall_data = list(wall_dict.values())[0]
            wx, wy = wall_data["x"], wall_data["y"]
            if wall_data["axis"] == "X" and fitting["axis"] == "X":
                dist = abs(fy - wy)
            elif wall_data["axis"] == "Y" and fitting["axis"] == "Y":
                dist = abs(fx - wx)
            if len(walls) == 6:
                if count_minus_y == 2 and i > 0 and wx < glass_x_pos:
                    for row in centerpoint_rows:
                        if row["Wall Number"] == i + 1:
                            row["floortileheight"] = (
                                1000 + lowest_floor + top_twofloor_z[0]
                            )
                elif count_plus_y == 2 and i > 0 and wx > glass_x_pos:
                    for row in centerpoint_rows:
                        if row["Wall Number"] == i + 1:
                            row["floortileheight"] = (
                                1000 + lowest_floor + top_twofloor_z[0]
                            )
                if (
                    count_minus_y == 2
                    and i > 0
                    and wx < glass_x_pos
                    and dist < min_dist
                ):
                    min_dist = dist
                    nearestwallindex = i + 1
                    remarkreq = top_twofloor_z[1]
                elif (
                    count_plus_y == 2 and i > 0 and wx > glass_x_pos and dist < min_dist
                ):
                    min_dist = dist
                    nearestwallindex = i + 1
                    remarkreq = top_twofloor_z[1]
                elif dist < min_dist:
                    min_dist = dist
                    nearestwallindex = i + 1
                    remarkreq = top_twofloor_z[0]
            else:
                if dist < min_dist:
                    min_dist = dist
                    nearestwallindex = i + 1
                    remarkreq = top_twofloor_z[0]
        if fz >= storey_min_height:
            Remark = "Unreachable"
        elif fz < ground_min_height + remarkreq:
            Remark = "Unreachable"
        elif fz < ground_min_height:
            Remark = "Floor"
        match = next(
            (w for w in wall_info if w["Wall Number"] == nearestwallindex), None
        )
        if match:
            width = match["Width"]
            height = match["Height"]
        stage3_results.append(
            {
                "Wall Number": nearestwallindex,
                "Name": fitting["name"],
                "Position X": fx + origin_x,
                "Position Y": fy + origin_y,
                "Position Z": fz,
                "Width": width,
                "Height": height,
                "vertices": fitting["vertices"],
            }
        )
    return stage3_results

def compare_width_y(walls_facing_y, internal_y_width, count_plus_y, count_minus_y):
    for i in range(len(walls_facing_y)):
        wall_i = walls_facing_y[i]
        xi = wall_i["area"][0]
        name_i = wall_i["name"]
        for j in range(i + 1, len(walls_facing_y)):
            wall_j = walls_facing_y[j]
            xj = wall_j["area"][0]
            name_j = wall_j["name"]
            if xi > xj:
                if count_minus_y == 2:
                    internal_y_width[0], internal_y_width[1] = (
                        internal_y_width[1],
                        internal_y_width[0],
                    )
                elif count_plus_y == 2:
                    internal_y_width[-2], internal_y_width[-1] = (
                        internal_y_width[-1],
                        internal_y_width[-2],
                    )
                return internal_y_width
            elif xi < xj:
                return internal_y_width
            else:
                return internal_y_width


def get_internal_width(walls, startingwall, wall20, wall12):
    xwidths, ywidths = [], []
    for wall in walls:
        area = wall["area"]
        axis = wall["axis"]
        width, height, depth = area
        if axis == "X":
            xwidths.append(width)
        else:
            ywidths.append(width)
    internalx_width, internaly_width = 0, 0
    xwidths_sorted = sorted(xwidths, reverse=True)
    ywidths_sorted = sorted(ywidths, reverse=True)
    internal_x_width, internal_y_width = [], []
    external_x_width, external_y_width = 0, 0
    if max(xwidths) > max(ywidths):
        starting_area = startingwall["area"]
        xstarting, height50, ___ = starting_area
        if xstarting >= max(xwidths):
            internalx_width = max(xwidths)
            internaly_width = max(xwidths)
        else:
            internalx_width = min(xwidths)
            internaly_width = min(xwidths)
        height = max(w["area"][1] for w in wall20)
        internalx_width = (internalx_width / 2) - height
        max_y_width = max(ywidths)
        external_x_width = (internalx_width + height + height50) * 2
        external_y_width = max_y_width
        internaly_width = identifywall12(wall12, wall20, max_y_width, height50)
        internal_x_width, internal_y_width = identifyinternal(
            wall20,
            walls,
            height50,
            internalx_width,
            internaly_width,
            xwidths_sorted,
            ywidths_sorted,
        )
        xwidths_sorted[1] += height50
        ywidths_sorted[1] += height50
        xwidths_sorted[0] += height50 * 2
    elif max(ywidths) > max(xwidths):
        starting_area = startingwall["area"]
        height = max(w["area"][1] for w in wall20)
        y_starting, height50, ___ = starting_area
        if y_starting >= max(ywidths):
            internaly_width = max(ywidths)
        else:
            internaly_width = min(ywidths)
        internaly_width = (internaly_width / 2) - height
        max_x_width = max(xwidths)
        internalx_width = identifywall12(wall12, wall20, max_x_width, height50)
        external_y_width = (internal_y_width + height50 + height) * 2
        external_x_width = max_x_width
        internal_x_width, internal_y_width = identifyinternal(
            wall20,
            walls,
            height50,
            internalx_width,
            internaly_width,
            xwidths_sorted,
            ywidths_sorted,
        )
        xwidths_sorted[1] += height50
        ywidths_sorted[1] += height50
        ywidths_sorted[0] += height50 * 2
    return (
        round(internalx_width),
        round(internaly_width),
        round(internalx_width) * 2,
        round(internaly_width) * 2,
        internal_x_width,
        internal_y_width,
        external_x_width,
        external_y_width,
        xwidths_sorted,
        ywidths_sorted,
    )


def identifyinternal(
    wall20,
    walls,
    height50,
    internalx_width,
    internaly_width,
    xwidths_sorted,
    ywidths_sorted,
):
    internal_x_width, internal_y_width = [], []
    if len(walls) == 6:
        height20 = max(w["area"][1] for w in wall20)
        secondinternaly_width = ywidths_sorted[1] - (height20 * 2) - height50
        lastinternaly_width = (internaly_width * 2) - secondinternaly_width
        secondinternalx_width = xwidths_sorted[1] - (height20 * 2) - height50
        lastinternalx_width = (internalx_width * 2) - secondinternalx_width
        internal_x_width = [
            round(internalx_width * 2),
            round(secondinternalx_width),
            round(lastinternalx_width),
        ]
        internal_y_width = [
            round(internaly_width * 2),
            round(secondinternaly_width),
            round(lastinternaly_width),
        ]
    elif len(walls) == 4:
        internal_x_width = [round(internalx_width * 2)]
        internal_y_width = [round(internaly_width * 2)]
    return internal_x_width, internal_y_width


def identifywall12(wall12, wall20, maxwidth, height50):
    if wall12:
        height20 = max(w["area"][1] for w in wall20)
        height12 = max(w["area"][1] for w in wall12)
        maxwidth = (maxwidth - (height50 * 2) - height20 - height12) / 2
    else:
        height20 = max(w["area"][1] for w in wall20)
        maxwidth = maxwidth / 2 - height50
    return maxwidth


def compute_area_from_vertices(obj):
    vertices = obj["vertices"]
    if len(vertices) == 0:
        return (0, 0, 0)
    min_x, max_x = vertices[:, 0].min(), vertices[:, 0].max()
    min_y, max_y = vertices[:, 1].min(), vertices[:, 1].max()
    min_z, max_z = vertices[:, 2].min(), vertices[:, 2].max()
    width = max_x - min_x
    depth = max_y - min_y
    height = max_z - min_z
    return (width, depth, height)


def oppsidespositionwall(distance, fittings, walls, count_minus_y):
    results = []
    max_x_widths = []
    max_y_widths = []
    min_abs_dist = min(abs(d["Distance"]) for d in distance)
    wall_info_map = {}
    for d in distance:
        wall_number = d["Wall Number"]
        axis = d["Axis"]
        max_width = d["Max_Width"]
        dist = abs(d["Distance"])
        if axis == "X":
            max_x_widths.append(max_width)
        elif axis == "Y":
            max_y_widths.append(max_width)
        wall_info_map[wall_number] = {
            "axis": axis,
            "max_width": max_width,
            "dist": dist,
        }
    max_x_width = max(max_x_widths)
    max_y_width = max(max_y_widths)
    for wall_dict in walls:
        wall_name, wall_data = list(wall_dict.items())[0]
        for wall_number in wall_info_map:
            if wall_info_map[wall_number].get("area") is None:
                wall_info_map[wall_number]["area"] = wall_data["area"]
    for fit in fittings:
        wall_number = fit["Wall Number"]
        if wall_number not in wall_info_map:
            continue
        wall_info = wall_info_map[wall_number]
        axis = wall_info["axis"]
        max_width = max_y_width if axis == "X" else max_x_width
        dist = wall_info["dist"]
        area = wall_info["area"]
        fitting_pos = fit["Position Y"] if axis == "X" else fit["Position X"]
        if abs(dist) <= min_abs_dist:
            corrected_pos = -abs(fitting_pos - area[1])
        else:
            corrected_pos = fitting_pos - max_width
            if len(walls) == 6 and count_minus_y == 2:
                if wall_number == 4:
                    corrected_pos = -abs(max_width + corrected_pos)
        results.append(
            {
                "Wall Number": wall_number,
                "Point Name": fit["Name"],
                "Position X": fit["Position X"] if axis == "X" else corrected_pos,
                "Position Y": fit["Position Y"] if axis == "Y" else corrected_pos,
                "Position Z": fit["Position Z"] - 1000,
            }
        )


def applyexternal(row, ymaxwidths, xmaxwidths, walls, wall_bss50):
    counters, width , height, countersxy = 0, 0, 0 , 0
    wall_number = row["Wall Number"]
    for i, wall_dict in enumerate(walls):
            height = list(wall_dict.values())[0]["area"][2]
            if len(walls) == 6:
                if list(wall_dict.values())[0]["axis"] == "X":
                    if i + 1 == wall_number:
                        width = xmaxwidths[counters]
                    countersxy += 1
                    if countersxy == 2:
                        countersxy = 0
                        counters += 1
                elif list(wall_dict.values())[0]["axis"] == "Y":
                    if i + 1 == wall_number:
                        width = ymaxwidths[counters]
                    countersxy += 1
                    if countersxy == 2:
                        countersxy = 0
                        counters += 1
            elif len(wall_bss50) == 4:
                if list(wall_dict.values())[0]["axis"] == "X":
                    if i + 1 == wall_number:
                        width = xmaxwidths[counters]
                else:
                    if i + 1 == wall_number:
                        width = ymaxwidths[counters]
    if wall_number == "F":
        width = max(xmaxwidths)
        height = max(ymaxwidths)
    return pd.Series([width , height])
