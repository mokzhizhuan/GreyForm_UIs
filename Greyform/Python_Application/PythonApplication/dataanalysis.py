import pandas as pd
import ifcopenshell
import PythonApplication.methodifcfindings as ifc_findings
import PythonApplication.fitting_width as fitting
from ifcopenshell.util.placement import get_local_placement
import PythonApplication.gettmps as tmps
import PythonApplication.loadmaintmp as tmps6sides
import re
import PythonApplication.robot_pos as setuprobot
import PythonApplication.fitting_pointbox as pointbox
import heapq


class data_draft(object):
    def __init__(self, ifc_file, args):
        self.ifc_file = ifc_file
        self.args = args

    def analysis(self):
        # get the data  wall , opening , floor
        all_walls, brep_z_data, furnishing_pos = ifc_findings.process_elements(
            self.ifc_file.by_type("IfcWallStandardCase"), "basic wall:bss"
        )
        site = self.ifc_file.by_type("IfcSite")[0]  # Usually only one site
        placement = site.ObjectPlacement
        while hasattr(placement, "PlacementRelTo") and placement.PlacementRelTo:
            placement = placement.PlacementRelTo
        loc = placement.RelativePlacement.Location
        origin_x, origin_y, ____ = loc.Coordinates
        origin_x = round(origin_x)
        origin_y = round(origin_y)
        # indicating the width and height
        walls_bss50 = [w for w in all_walls if "basic wall:bss.50" in w["name"].lower()]
        tile_pattern = re.compile(r"\d+x\d+mm")
        walls_bss20 = [
            w
            for w in all_walls
            if "basic wall:bss.50" not in w["name"].lower()
            and tile_pattern.search(w["name"])
            and "glass" not in w["name"].lower()
        ]
        walls_bss_no_tile = [
            w
            for w in all_walls
            if not tile_pattern.search(w["name"])
            and "glass" not in w["name"].lower()
            and "basic wall:bss.50" not in w["name"].lower()
        ]
        openings, brep_z_data, furnishing_pos = ifc_findings.process_elements(
            self.ifc_file.by_type("IfcOpeningElement"), "basic wall:bss.50"
        )
        door, brep_z_data, furnishing_pos = ifc_findings.process_elements(
            self.ifc_file.by_type("IfcDoor"), "opening"
        )
        floors, brep_z_data, furnishing_pos = ifc_findings.process_elements(
            self.ifc_file.by_type("IfcSlab"), "floor"
        )
        unique_floors = []
        seen_names = set()
        for floor in floors:
            if floor["name"] not in seen_names:
                seen_names.add(floor["name"])
                unique_floors.append(floor)
        floors = unique_floors
        floor_bss_60 = [f for f in floors if "floor:bss.60" in f["name"].lower()]
        other_floor = [f for f in floors if "floor:bss.60" not in f["name"].lower()]
        all_objs, brep_z_data, furnishing_pos = ifc_findings.process_elements(
            self.ifc_file.by_type("IfcElement"), ""
        )
        box_up = ifc_findings.process_elements(self.ifc_file.by_type("IfcWall"), "box")
        """used_names = set(w["name"] for w in all_walls + openings + door + floors)
        excluded_types = {
            "IfcFlowController",
            "IfcFlowSegment",
            "IfcCovering",
            "IfcDoor",
            "IfcFlowFitting",
            "IfcOpeningElement", 
            "IfcCovering",
        }
        remaining_objs = [
            obj
            for obj in all_objs
            if obj["name"] not in used_names
            and obj["type"] not in excluded_types
            and "floor:bss.60" not in obj["name"].lower()
            and "basic wall:bss.20" not in obj["name"].lower()
        ]"""
        # storeys for the minimum ceiling
        storeys, ground = ifc_findings.extract_storeys(self.ifc_file)
        # wallformula
        same , fallback = {} , []
        if door:
            for doors in door:
                closest_wall, distance = ifc_findings.find_closest_wall(doors, walls_bss50)
                if closest_wall:
                    same[closest_wall["name"]] = closest_wall  # overwrite if already exists
        else:
            # fallback logic: openings
            fallback = [
                o for o in openings if any(o["name"] in w["name"] for w in walls_bss50)
            ]
            if fallback:
                max_opening = max(
                    fallback, key=lambda o: ifc_findings.compute_area(o["area"])
                )
                same[max_opening["name"]] = max_opening
        start = list(same.values())
        if isinstance(start, list) and len(start) == 1:
            start = start[0]
        start = [w for w in walls_bss50 if w["name"] == start["name"]]
        visited, unvisited = [], walls_bss50.copy()
        floor_offset, offset, floor_tile_height = 0, 0, 0
        internalx_width, internaly_width = 0, 0
        internalxmax_width, internalymax_width = 0, 0
        internal_x_width, internal_y_width = [], []
        # algorithmns for euclean distance
        if start:
            if isinstance(start, list):
                if len(start) == 1:
                    start = start[0]
                else:
                    raise ValueError("Expected 'start' to contain only one wall dict")
            unvisited = [w for w in unvisited if w["name"] != start["name"]]
            start_wall = next((w for w in walls_bss50 if w["name"] == start["name"]), start)
            visited = [{start["name"]: start_wall}]
            (
                internalx_width,  # centerpoint x
                internaly_width,  # centerpoint y
                internalxmax_width,
                internalymax_width,
                internal_x_width,
                internal_y_width,
                externalxmax_width,
                externalymax_width,
                xmaxwidths,
                ymaxwidths,
            ) = fitting.get_internal_width(
                walls_bss50, start_wall, walls_bss20, walls_bss_no_tile
            )
            floor_offset = max(floors, key=lambda f: f["z"], default={"z": 0})["z"]
            floor_offset = abs(floor_offset) if floor_offset else 0
            offset = abs(start["z"])
            curr = start
            while unvisited:
                next_w, _ = ifc_findings.find_closest_wall(curr, unvisited)
                if not next_w:
                    break
                visited.append({next_w["name"]: next_w})
                unvisited = [w for w in unvisited if w["name"] != next_w["name"]]
                curr = next_w
        # store the finalized rows in stage 2
        if len(visited) == 6:
            top_twofloor_z = heapq.nlargest(2, (f["z"] for f in floors))
        counters, countersxy, width = 0, 0, 0
        stage2_rows, centerpoint_rows, box_up_rows = [], [], []
        walls_facing_plus_y = [
            list(wall.values())[0]
            for wall in visited
            if list(wall.values())[0]["facingaxis"] == "+Y"
        ]
        walls_facing_minus_y = [
            list(wall.values())[0]
            for wall in visited
            if list(wall.values())[0]["facingaxis"] == "-Y"
        ]   
        count_plus_y = len(walls_facing_plus_y)
        count_minus_y = len(walls_facing_minus_y)
        if count_minus_y == 2:
            internal_x_width[-2], internal_x_width[-1] = (
                internal_x_width[-1],
                internal_x_width[-2],
            )
            internal_y_width.sort()
            internal_y_width = fitting.compare_width_y(
                walls_facing_minus_y, internal_y_width, count_plus_y, count_minus_y
            )
            ymaxwidths.sort()
            ymaxwidths[0], ymaxwidths[1] = (ymaxwidths[1], ymaxwidths[0])
            xmaxwidths[-2], xmaxwidths[-1] = (
                xmaxwidths[-1],
                xmaxwidths[-2],
            )   
        elif count_plus_y == 2:
            internal_y_width = fitting.compare_width_y(
                walls_facing_minus_y, internal_y_width, count_plus_y, count_minus_y
            )
        floor_z = max(f["z"] for f in other_floor) if other_floor else 0
        box_up = box_up[0][0]
        box_up_rows.append(
            {
                "name": box_up["name"],
                "type": box_up["type"],
                "x": box_up["x"],
                "y": box_up["y"],
                "z": box_up["z"],
                "axis": box_up["axis"],
                "facingaxis": box_up["facingaxis"],
                "area": box_up["area"],
                "vertices": box_up["vertices"],
            }
        )
        for i, wall_dict in enumerate(visited):
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
                    "Wall Number": i + 1,
                    "Wall": list(wall_dict.keys())[0],
                    "Position X": list(wall_dict.values())[0]["x"] + origin_x,
                    "Position Y": list(wall_dict.values())[0]["y"] + origin_y,
                    "Position Z": list(wall_dict.values())[0]["z"],
                    "Width": width,
                    "Height": list(wall_dict.values())[0]["area"][2],
                }
            )
            if list(wall_dict.values())[0]["axis"] == "X":
                dist_needed = 0 - (list(wall_dict.values())[0]["y"] + origin_y)
                y_wallsurface = (list(wall_dict.values())[0]["y"] + origin_y) + dist_needed
                stage2_rows.append(
                    {
                        "Wall Number": i + 1,
                        "Wall": f"CP{i + 1}S2",
                        "Position X": externalxmax_width / 2,
                        "Position Y": y_wallsurface,
                        "Position Z": 1000 + floor_z,
                        "Width": width,
                        "Height": list(wall_dict.values())[0]["area"][2],
                    }
                )
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
            elif list(wall_dict.values())[0]["axis"] == "Y":
                dist_needed = 0 - (list(wall_dict.values())[0]["x"] + origin_x)
                x_wallsurface = (list(wall_dict.values())[0]["x"] + origin_x) + dist_needed
                stage2_rows.append(
                    {
                        "Wall Number": i + 1,
                        "Wall": f"CP{i + 1}S2",
                        "Position X": x_wallsurface,
                        "Position Y": externalymax_width / 2,
                        "Position Z": 1000 + floor_z,
                        "Width": width,
                        "Height": list(wall_dict.values())[0]["area"][2],
                    }
                )
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
        for floor_obj in other_floor:
            stage2_rows.append(
                {
                    "Wall Number": "F",
                    "Wall": floor_obj["name"],
                    "Position X": floor_obj["x"] + origin_x,
                    "Position Y": floor_obj["y"] + origin_y,
                    "Position Z": floor_obj["z"],
                    "Width": internalxmax_width,
                    "Height": internalymax_width,
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
                        "AxisDirection": floor_obj["facingaxis"],
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
                        "AxisDirection": floor_obj["facingaxis"],
                    }
                )
        floor_z_off = floor_z - 1000
        stage2_rows.append(
            {
                "Wall Number": "F",
                "Wall": f"CP{len(visited) + 1}S2",
                "Position X": externalxmax_width / 2,
                "Position Y": externalymax_width / 2,
                "Position Z": floor_z,
                "Width": internalxmax_width,
                "Height": internalymax_width,
            }
        )
        # stage 3
        stage3_objects = []
        checklist_file = pd.ExcelFile(self.args.excel_checklist)
        df_checklist = checklist_file.parse("Sheet1")
        item_names = df_checklist.iloc[1:, 3].dropna().unique().tolist()
        filtered_item_names = [
            name
            for name in item_names
            if "bss.10 glass" not in name.lower()
            and "wall finishes" not in name.lower()
            and "floor finishes" not in name.lower()
        ]
        for obj in all_objs:
            if any(f_item in obj["name"] for f_item in filtered_item_names):
                stage3_objects.append(
                    {
                        "name": obj["name"],
                        "x": obj["x"],
                        "y": obj["y"],
                        "z": obj["z"],
                    }
                )   
        glass_walls = [
            obj
            for obj in all_objs
            if "glass" in obj["name"].lower()
            and not (obj.get("x", 0) == 0 and obj.get("y", 0) == 0 and obj.get("z", 0) == 0)
        ]
        df_checklist.columns = df_checklist.iloc[0]
        # assign fittings
        wall_info = [
            {
                "Wall Number": row["Wall Number"],
                "Width": row["Width"],
                "Height": row["Height"],
            }
            for row in stage2_rows
            if isinstance(row["Wall Number"], int)
        ]
        fitting_stage3 = fitting.assign_nearest_fitting(
            visited,
            stage3_objects,
            storeys,
            other_floor,
            wall_info,
            ground,
            glass_walls,
            count_minus_y,
            count_plus_y,
            centerpoint_rows,
            origin_x,
            origin_y,
            walls_bss20,
            walls_bss_no_tile
        )
        boxup = fitting.assign_nearest_fitting_rotation(
            visited,
            box_up_rows,
            storeys,
            other_floor,
            wall_info,
            ground,
            glass_walls,
            count_minus_y,
            count_plus_y,
            centerpoint_rows,
            origin_x,
            origin_y,
        )
        fitting_stage3.sort(
            key=lambda x: (
                int(x["Wall Number"]) if str(x["Wall Number"]).isdigit() else float("inf")
            )   
        )
        df_fitting = pd.DataFrame(fitting_stage3)
        tmptemp, distance = [], []
        if len(visited) == 4:
            Tmpholder = tmps.getTMP(
                all_objs,
                stage2_rows,
                visited,
                fitting_stage3,
                walls_bss20,
                origin_x,
                origin_y,
                other_floor,
                centerpoint_rows,
                storeys,
                brep_z_data,
                furnishing_pos,
            )
            # tmptemp, distance = Tmpholder.addTMP2()
        else:
            Tmpholder = tmps6sides.loadmainTMP(
                all_objs,
                stage2_rows,
                visited,
                fitting_stage3,
                walls_bss20,
                walls_bss_no_tile,
                origin_x,
                origin_y,
                other_floor,
                storeys,
                centerpoint_rows,
                fallback,
                boxup,
                glass_walls,
            )
            tmptemp, distance = Tmpholder.returnalltmps()
        df_tmptemp = pd.DataFrame(tmptemp)
        df_visited = pd.DataFrame(stage2_rows)
        df_combined = pd.concat([df_tmptemp, df_visited], ignore_index=True)
        df_combined["Wall Number Sort"] = pd.to_numeric(
            df_combined["Wall Number"], errors="coerce"
        )
        df_combined = df_combined.sort_values(by=["Wall Number Sort", "Point Name"]).drop(
            columns="Wall Number Sort"
        )
        df_combined = df_combined.reset_index(drop=True)
        df_combined.index = df_combined.index + 1
        df_fitting.index = df_fitting.index + 1
        df_combined[["Width", "Height"]] = df_combined.apply(
            lambda row: fitting.applyexternal(
                row, ymaxwidths, xmaxwidths, visited, walls_bss50
            ),
            axis=1,
        )
        df_combined["Point Name"] = df_combined.apply(
            lambda row: (
                row["Wall"]
                if pd.isna(row["Point Name"]) or row["Point Name"] == ""
                else row["Point Name"]
            ),
            axis=1,
        )
        df_combined = df_combined[
            ~df_combined["Wall"].str.contains("Basic Wall|Floor", na=False)
        ]
        df_combined.drop(columns=["Wall"], inplace=True)
        fittingbox = pointbox.boundingboxpoint(fitting_stage3, all_objs)
        fittingboundingbox = fittingbox.returnallfitting()
        df_fitting[["Position X", "Position Y", "Position Z"]] = df_fitting.apply(
            lambda row: setuprobot.setupfittingrequirement(
                row, all_objs, fittingboundingbox , df_checklist
            ),
            axis=1,
        )
        #robot tiling dont use it
        df_combined[["Position X", "Position Y", "Position Z"]] = df_combined.apply(
            lambda row: setuprobot.setuprobotposition(row, stage2_rows , visited, externalxmax_width , externalymax_width),
            axis=1
        ) 
        df_fitting[["Position X", "Position Y", "Position Z"]] = df_fitting.apply(
            lambda row: setuprobot.setuprobotposition_fitting(row, stage2_rows , visited , externalymax_width , externalymax_width),
            axis=1
        )
        with pd.ExcelWriter(self.output_excel, engine="openpyxl") as writer:
            df_visited.to_excel(writer, index=True, sheet_name="Stage 2")  # Include index
            df_fitting.to_excel(writer, index=True, sheet_name="Stage 3")   # Include index
        return (
            count_plus_y,
            count_minus_y,
            self.args.output_excel,
            #wall_format,
            self.axis_widths,
        )

    def applywallpoints(self, row):
        wall_number = row["Wall Number"]
        positionx = row["Position X"]
        positiony = row["Position Y"]
        positionz = row["Position Z"]
        for wall in self.centerpoint_rows:
            if wall_number == wall["Wall Number"]:
                floortile_offset = wall["floortileheight"]
                if wall["AxisDirection"] == "+X":
                    positionx = positionx - wall["centerpointwidth"]
                    return pd.Series(
                        [
                            positionx,
                            positiony,
                            positionz - floortile_offset,
                        ]
                    )
                elif wall["AxisDirection"] == "-X":
                    positionx = positionx - wall["centerpointwidth"]
                    if positionx > 0:
                        return pd.Series(
                            [
                                -abs(positionx),
                                positiony,
                                positionz - floortile_offset,
                            ]
                        )
                    else:
                        return pd.Series(
                            [
                                abs(positionx),
                                positiony,
                                positionz - floortile_offset,
                            ]
                        )
                elif wall["AxisDirection"] == "+Y":
                    positiony = positiony - wall["centerpointwidth"]
                    return pd.Series(
                        [
                            positionx,
                            positiony,
                            positionz - floortile_offset,
                        ]
                    )
                elif wall["AxisDirection"] == "-Y":
                    positiony = positiony - wall["centerpointwidth"]
                    if positionx > 0:
                        return pd.Series(
                            [
                                -abs(positiony),
                                positionx,
                                positionz - floortile_offset,
                            ]
                        )
                    else:
                        return pd.Series(
                            [
                                abs(positiony),
                                positionx,
                                positionz - floortile_offset,
                            ]
                        )
            if wall_number == "F":
                if wall_number == wall["Wall Number"]:
                    return pd.Series(
                        [
                            positionx - wall["centerpointwidth"],
                            positiony - wall["centerpointheight"],
                            positionz - 1000,
                        ]
                    )
