import pandas as pd
import compute_wall_center as wc


def getstage2andstage3(
    all_objs,
    args,
    visited,
    walls_bss50,
    internal_x_width,
    internal_y_width,
    origin_x,
    origin_y,
    internalx_width,
    internalxmax_width,
    internalymax_width,
    offset,
    internaly_width,
    other_floor,
    top_twofloor_z,
    floor_offset,
    thickness
):
    def _first_kv(d):
        k = next(iter(d))
        return k, d[k]
    stage2_rows, centerpoint_rows = [], []
    counters = countersxy = 0
    six = (len(walls_bss50) == 6)
    four = (len(walls_bss50) == 4)
    x_iter = iter(internal_x_width) if six else None
    y_iter = iter(internal_y_width) if six else None
    curr_xw = next(x_iter, 0) if six else None
    curr_yw = next(y_iter, 0) if six else None
    wallcenterpoints = [] 
    centerrows = [] 
    for i, wall_dict in enumerate(visited):
        posz_cp = 1000
        name, w = _first_kv(wall_dict)
        axis = w["axis"]
        width = 0
        if six:
            wallcenterpoints = wc.compute_wall_centerpoints_six(
                internal_x_width, internal_y_width, visited, posz_cp
            )
            width = curr_xw if axis == "X" else curr_yw
            countersxy += 1
            if countersxy == 2:
                countersxy = 0
                curr_xw = next(x_iter, curr_xw)
                curr_yw = next(y_iter, curr_yw)
                counters += 1
        elif four:
            width = (internal_x_width[counters] if axis == "X" else internal_y_width[counters])
        width_val = w["area"][0]
        row = {
            "Marking Type": "Wall",
            "Name": name,
            "GX": w["x"],
            "GY": w["y"],
            "GZ": w["z"],
            "Wall Number": i + 1,
            "Shape Type" : "",
            "Width": width_val,
            "Height": w["area"][2],
        }
        stage2_rows.append(row)
        if axis == "X":
            dist_needed = -(w["y"] + origin_y)
            y_wallsurface = (w["y"] + origin_y) + dist_needed
            stage2_rows.append({
                "Marking Type": "Center Point",
                "Name": f"CP{i + 1}S2",
                "GX": (internalxmax_width / 2)+ thickness,
                "GY": y_wallsurface,
                "GZ": posz_cp,
                "Wall Number": i + 1,
                "Shape Type" : "",
                "Width": width,
                "Height": w["area"][2],
            })
            centerrows.append({
                "Marking Type": "CenterWallPoint",
                "Name": f"WallCP{i + 1}({name})",
                "X": wallcenterpoints[i]["GX"]/1000,
                "Y": wallcenterpoints[i]["GY"]/1000,
                "Z": wallcenterpoints[i]["GZ"]/1000,
                "Wall Number": i + 1,
                "Shape Type" : "",
                "Width": width,
                "Height": w["area"][2],
            })
            centerpoint_rows.append({
                "Wall Number": i + 1,
                "Name": name,
                "centerpointwidth": internalx_width,  
                "centerpointhheight": posz_cp,        
                "floortileheight": posz_cp + offset,
                "AxisDirection": w["facingaxis"],
            })
        elif axis == "Y":  
            dist_needed = -(w["x"] + origin_x)
            x_wallsurface = (w["x"] + origin_x) + dist_needed
            stage2_rows.append({
                "Marking Type": "Center Point",
                "Name": f"CP{i + 1}S2",
                "GX": x_wallsurface,
                "GY": (internalymax_width / 2)+thickness,
                "GZ": posz_cp,
                "Wall Number": i + 1,
                "Shape Type" : "",
                "Width": width, 
                "Height": w["area"][2],
            })
            centerrows.append({
                "Marking Type": "CenterWallPoint",
                "Name": f"WallCP{i + 1}({name})",
                "X": wallcenterpoints[i]["GX"]/1000,
                "Y": wallcenterpoints[i]["GY"]/1000,
                "Z": wallcenterpoints[i]["GZ"]/1000,
                "Wall Number": i + 1,
                "Shape Type" : "",
                "Width": width,
                "Height": w["area"][2],
            })
            centerpoint_rows.append({
                "Wall Number": i + 1,
                "Name": name,
                "centerpointwidth": internaly_width,
                "centerpointhheight": posz_cp,
                "floortileheight": posz_cp + offset,
                "AxisDirection": w["facingaxis"],
            })
    for floor_obj in other_floor:
        stage2_rows.append({
            "Wall Number": "F",
            "Name": floor_obj["name"],
            "Marking Type": "Floor",
            "Shape Type" : "",
            "GX": floor_obj["x"],
            "GY": floor_obj["y"],
            "GZ": floor_obj["z"],
            "Width": internalxmax_width,
            "Height": internalymax_width,
        })
        if len(visited) == 6:
            centerpoint_rows.append({
                "Wall Number": "F",
                "Name": floor_obj["name"],
                "centerpointwidth": internalx_width,
                "centerpointheight": internaly_width,
                "floortileheight": [1000 + abs(top_twofloor_z[0]), 1000 + abs(top_twofloor_z[1])],
                "AxisDirection": floor_obj["facingaxis"],
            })
        else:
            centerpoint_rows.append({
                "Wall Number": "F",
                "Name": floor_obj["name"],
                "centerpointwidth": internalx_width,
                "centerpointheight": internaly_width,
                "floortileheight": [1000 + abs(floor_offset)],
                "AxisDirection": floor_obj["facingaxis"],
            })
    floor_z_off = -abs(1000)
    stage2_rows.append({
        "Marking Type" : "Center Point",
        "Name": f"CP{len(visited) + 1}S2",
        "GX": (internalxmax_width / 2)+ thickness,
        "GY": (internalymax_width / 2)+ thickness,
        "GZ": floor_z_off,
        "Wall Number": "F",
        "Shape Type" : "",
        "Width": internalxmax_width,
        "Height": internalymax_width,
    })
    checklist_file = pd.ExcelFile(args.excel_checklist)
    df_checklist = checklist_file.parse("Sheet1")
    item_names = df_checklist.iloc[1:, 3].dropna().unique().tolist()
    filtered_item_names = [n for n in item_names
                        if "bss.10 glass" not in n.lower()
                        and "wall finishes" not in n.lower()
                        and "floor finishes" not in n.lower()]
    stage3_objects = [
        {"name": o["name"], "x": o["x"], "y": o["y"], "z": o["z"]}
        for o in all_objs
        if any(f in o["name"] for f in filtered_item_names)
    ]
    return stage2_rows, centerpoint_rows, stage3_objects, df_checklist , centerrows