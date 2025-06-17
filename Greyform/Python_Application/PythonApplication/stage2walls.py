def getstage2(
    visited,
    wall_format,
    walls_bss50,
    floor,
    internal_x_width,
    internal_y_width,
    offset,
    origin_x,
    origin_y,
    internalx_width,
    internaly_width,
    internalxmax_width,
    internalymax_width,
    top_twofloor_z,
    floor_offset,
):
    stage2_rows = []
    centerpoint_rows = []
    counters, countersxy, width = 0, 0, 0
    for i, wall_dict in enumerate(visited):
        wall = wall_format[i + 1]
        if len(walls_bss50) == 6:
            if list(wall_dict.values())[0]["axis"] == "X":
                width = internal_x_width[counters]
                countersxy += 1
                if countersxy == 2:
                    countersxy = 0
                    counters += 1
            elif list(wall_dict.values())[0]["axis"] == "Y":
                width = internal_y_width[counters]
                countersxy += 1
                if countersxy == 2:
                    countersxy = 0
                    counters += 1
        elif len(walls_bss50) == 4:
            if list(wall_dict.values())[0]["axis"] == "X":
                width = internal_x_width[counters]
            else:
                width = internal_y_width[counters]
        stage2_rows.append(
            {
                "Marking Type": "Tile",
                "Point Name": list(wall_dict.keys())[0],
                "Position X": list(wall_dict.values())[0]["x"] + origin_x,
                "Position Y": list(wall_dict.values())[0]["y"] + origin_y,
                "Position Z": list(wall_dict.values())[0]["z"],
                "Wall Number": i + 1,
                "Shape Type": 6,
                "Status": "",
                "Quadrant": 1,
                "Unamed : 9": "",
                "Width": width,
                "Height": list(wall_dict.values())[0]["area"][2],
                "Orientation": "",
                "Diameter": "",
            }
        )
        if list(wall_dict.values())[0]["axis"] == "X":
            centerpoint_rows.append(
                {
                    "Wall Number": i + 1,
                    "Wall": list(wall_dict.keys())[0],
                    "centerpointwidth": internalx_width,
                    "centerpointheight": 1000,  # manual m line based on the formula
                    "floortileheight": 1000 + offset,
                    "AxisDirection": list(wall_dict.values())[0]["facingaxis"],
                }
            )
            if list(wall_dict.values())[0]["facingaxis"] == "+X":
                wall["pos_x_range"] = (
                    list(wall_dict.values())[0]["x"],
                    list(wall_dict.values())[0]["x"] + wall["width"],
                )
                wall["pos_y_range"] = (
                    list(wall_dict.values())[0]["y"],
                    list(wall_dict.values())[0]["y"] + wall["thickness"],
                )
            else:
                wall["pos_x_range"] = (
                    list(wall_dict.values())[0]["x"] - wall["width"],
                    list(wall_dict.values())[0]["x"],
                )
                wall["pos_y_range"] = (
                    list(wall_dict.values())[0]["y"] - wall["thickness"],
                    list(wall_dict.values())[0]["y"],
                )
        elif list(wall_dict.values())[0]["axis"] == "Y":
            centerpoint_rows.append(
                {
                    "Wall Number": i + 1,
                    "Wall": list(wall_dict.keys())[0],
                    "centerpointwidth": internaly_width,
                    "centerpointheight": 1000,  # manual m line based on the formula
                    "floortileheight": 1000 + offset,
                    "AxisDirection": list(wall_dict.values())[0]["facingaxis"],
                }
            )
            if list(wall_dict.values())[0]["facingaxis"] == "+Y":
                wall["pos_x_range"] = (
                    list(wall_dict.values())[0]["x"] - wall["thickness"],
                    list(wall_dict.values())[0]["x"],
                )
                wall["pos_y_range"] = (
                    list(wall_dict.values())[0]["y"],
                    list(wall_dict.values())[0]["y"] + wall["width"],
                )
            else:
                wall["pos_x_range"] = (
                    list(wall_dict.values())[0]["x"],
                    list(wall_dict.values())[0]["x"] + wall["thickness"],
                )
                wall["pos_y_range"] = (
                    list(wall_dict.values())[0]["y"] - wall["width"],
                    list(wall_dict.values())[0]["y"],
                )
        for floor_obj in floor:
            stage2_rows.append(
                {
                    "Marking Type": "Tile",
                    "Point Name": floor_obj["name"],
                    "Position X": floor_obj["x"] + origin_x,
                    "Position Y": floor_obj["y"] + origin_y,
                    "Position Z": floor_obj["z"],
                    "Wall Number": "F",
                    "Shape Type": 6,
                    "Status": "",
                    "Quadrant": 1,
                    "Unamed : 9": "",
                    "Width": internalxmax_width,
                    "Height": internalymax_width,
                    "Orientation": "",
                    "Diameter": "",
                }
            )
            if len(visited) == 6:
                centerpoint_rows.append(
                    {
                        "Wall Number": "F",
                        "Wall": floor_obj["name"],
                        "centerpointwidth": internalx_width,
                        "centerpointheight": internaly_width,
                        "floortileheight": [
                            1000 + abs(top_twofloor_z[0]),
                            1000 + abs(top_twofloor_z[1]),
                        ],
                    }
                )
            else:
                centerpoint_rows.append(
                    {
                        "Wall Number": "F",
                        "Wall": floor_obj["name"],
                        "centerpointwidth": internalx_width,
                        "centerpointheight": internaly_width,
                        "floortileheight": [1000 + abs(floor_offset)],
                    }
                )
    return stage2_rows , centerpoint_rows , wall_format