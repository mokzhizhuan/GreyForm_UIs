import heapq


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
    glass_x_pos = 0
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
            if wall_data["axis"] == "X":
                dist = abs(fy - wy)
            elif wall_data["axis"] == "Y":
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
            elif len(walls) == 4:
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
                "Marking Type": "Tile",
                "Point Name": fitting["name"],
                "Position X": fx + origin_x,
                "Position Y": fy + origin_y,
                "Position Z": fz,
                "Wall Number": nearestwallindex,
                "Shape Type": 6,
                "Status": "",
                "Quadrant": 1,
                "Unamed : 9": "",
                "Width": width,
                "Height": height,
                "Orientation": "",
                "Diameter": "",
                "Remark": Remark,
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


def get_internal_width(walls, startingwall, wall20, wall12, axis_widths):
    xwidths, ywidths, wall_range = [], [], {}
    for i, wall in enumerate(walls):
        area = wall["area"]
        axis = wall["axis"]
        width, height, depth = area
        if axis == "X":
            xwidths.append(width)
            wall_range[i + 1] = {
                "axis": axis,
                "width": width,
                "height": depth,
                "thickness": height,
            }
            axis_widths[axis.lower()].append(width)
        else:
            ywidths.append(width)
            wall_range[i + 1] = {
                "axis": axis,
                "width": width,
                "height": depth,
                "thickness": height,
            }
            axis_widths[axis.lower()].append(width)
    internalx_width, internaly_width = 0, 0
    xwidths_sorted = sorted(xwidths, reverse=True)
    ywidths_sorted = sorted(ywidths, reverse=True)
    internal_x_width, internal_y_width = [], []
    if max(xwidths) > max(ywidths):
        starting_area = startingwall["area"]
        xstarting, height50, ___ = starting_area
        if xstarting >= max(xwidths):
            internaly_width = max(xwidths)
        else:
            internaly_width = min(xwidths)
        height = max(w["area"][1] for w in wall20)
        internalx_width = max(xwidths)
        internalx_width = (internalx_width / 2) - height
        max_y_width = max(ywidths)
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
        internal_x_width, internal_y_width = identifyinternal(
            wall20,
            walls,
            height50,
            internalx_width,
            internaly_width,
            xwidths_sorted,
            ywidths_sorted,
        )
    return (
        round(internalx_width),
        round(internaly_width),
        round(internalx_width) * 2,
        round(internaly_width) * 2,
        internal_x_width,
        internal_y_width,
        wall_range,
        axis_widths,
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
        maxwidth = maxwidth / 2 - height50 - height20
    return maxwidth
