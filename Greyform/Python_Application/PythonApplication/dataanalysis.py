import pandas as pd
import ifcopenshell
import PythonApplication.methodifcfindings as ifc_findings
import PythonApplication.fitting_width as fitting
from ifcopenshell.util.placement import get_local_placement
import PythonApplication.gettmps as tmps
import PythonApplication.loadmaintmp as tmps6sides
import PythonApplication.stage2walls as loadwallsstage2
import re
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
        walls_bss20 = [w for w in all_walls if "basic wall:bss.50" not in w["name"].lower()]
        walls_bss12 = [
            w
            for w in all_walls
            if re.search(r"basic wall:bss\.(1[0-9])", w["name"].lower())
            and "glass" not in w["name"].lower()
        ]
        openings, brep_z_data, furnishing_pos = ifc_findings.process_elements(
            self.ifc_file.by_type("IfcOpeningElement"), "basic wall:bss.50"
        )
        door, brep_z_data, furnishing_pos = ifc_findings.process_elements(
            self.ifc_file.by_type("IfcDoor"), "opening"
        )
        floor, brep_z_data, furnishing_pos = ifc_findings.process_elements(
            self.ifc_file.by_type("IfcSlab"), "floor"
        )
        all_objs, brep_z_data, furnishing_pos = ifc_findings.process_elements(
            self.ifc_file.by_type("IfcElement"), ""
        )
        used_names = set(w["name"] for w in all_walls + openings + door + floor)
        excluded_types = {
            "IfcFlowController",
            "IfcFlowSegment",
            "IfcCovering",
            "IfcDoor",
            "IfcFlowFitting",
        }
        remaining_objs = [
            obj
            for obj in all_objs
            if obj["name"] not in used_names and obj["type"] not in excluded_types
        ]
        seen_names = set()
        floor = [
            f
            for f in floor  
            if (f["name"] not in seen_names and not seen_names.add(f["name"]))
        ]
        # storeys for the minimum ceiling
        storeys, ground = ifc_findings.extract_storeys(self.ifc_file)
        # wallformula
        same = {}
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
            ) = fitting.get_internal_width(
                walls_bss50, start_wall, walls_bss20, walls_bss12
            )
            floor_offset = max(floor, key=lambda f: f["z"], default={"z": 0})["z"]
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
            top_twofloor_z = heapq.nlargest(2, (f["z"] for f in floor))
        counters, countersxy, width = 0, 0, 0
        stage2_rows, self.centerpoint_rows = [], []
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
        elif count_plus_y == 2:
            internal_y_width = fitting.compare_width_y(
                walls_facing_minus_y, internal_y_width, count_plus_y, count_minus_y
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
                        "Position X": width / 2,
                        "Position Y": y_wallsurface,
                        "Position Z": 1000,
                        "Width": width,
                        "Height": list(wall_dict.values())[0]["area"][2],
                    }
                )
                stage2_rows.append(
                    {
                        "Wall Number": i + 1,
                        "Wall": f"TMP{i + 1}S2a1",
                        "Position X": -abs(width / 2),
                        "Position Y": y_wallsurface,
                        "Position Z": -1000,
                        "Width": width,
                        "Height": list(wall_dict.values())[0]["area"][2],
                    }
                )
                self.centerpoint_rows.append(
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
                        "Position Y": width / 2,
                        "Position Z": 1000,
                        "Width": width,
                        "Height": list(wall_dict.values())[0]["area"][2],
                    }
                )
                stage2_rows.append(
                    {
                        "Wall Number": i + 1,
                        "Wall": f"TMP{i + 1}S2a1",
                        "Position X": -abs(width / 2),
                        "Position Y": x_wallsurface,
                        "Position Z": -1000,
                        "Width": width,
                        "Height": list(wall_dict.values())[0]["area"][2],
                    }
                )
                self.centerpoint_rows.append(
                    {
                        "Wall Number": i + 1,
                        "Wall": list(wall_dict.keys())[0],
                        "centerpointwidth": internaly_width,
                        "centerpointheight": 1000,  # manual m line based on the formula
                        "floortileheight": 1000 + offset,
                        "AxisDirection": list(wall_dict.values())[0]["facingaxis"],
                    }
                )
        for floor_obj in floor:
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
                self.centerpoint_rows.append(
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
                self.centerpoint_rows.append(
                    {
                        "Wall Number": "F",
                        "Wall": floor_obj["name"],
                        "centerpointwidth": internalx_width,
                        "centerpointheight": internaly_width,
                        "floortileheight": [1000 + abs(floor_offset)],
                        "AxisDirection": floor_obj["facingaxis"],
                    }
                )
        floor_z = abs(max(f["z"] for f in floor) if floor else 0)
        floor_z = floor_z - 1000
        stage2_rows.append(
            {
                "Wall Number": "F",
                "Wall": f"CP{len(visited) + 1}S2",
                "Position X": internalx_width,
                "Position Y": internaly_width,
                "Position Z": floor_z,
                "Width": internalxmax_width,
                "Height": internalymax_width,
            }
        )
        # stage 3
        stage3_objects = []
        for obj in remaining_objs:
            stage3_objects.append(
                {
                    "name": obj["name"],
                    "x": obj["x"],
                    "y": obj["y"],
                    "z": obj["z"],
                }
            )
        glass_walls = [obj for obj in all_objs if "glass" in obj["name"].lower()]
        df_visited = pd.DataFrame(stage2_rows)
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
            floor,
            wall_info,
            ground,
            glass_walls,
            count_minus_y,
            count_plus_y,
            self.centerpoint_rows,
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
                floor,
                self.centerpoint_rows,
                storeys,
                brep_z_data,
                furnishing_pos,
            )
            tmptemp, distance = Tmpholder.getTMPFloor()
        else:
            Tmpholder = tmps6sides.loadmainTMP(
                all_objs,
                start,
                stage2_rows,
                visited,
                fitting_stage3,
                walls_bss20,
                walls_bss12,
                origin_x,
                origin_y,
                floor,
                storeys,
                self.centerpoint_rows,
            )
            tmptemp, distance = Tmpholder.getTMPFloor()
        """df_tmptemp = pd.DataFrame(tmptemp)
        processor = tmpprocesses.TMPProcessor(centerpoint_rows , walls_bss20 , walls_bss50)
        df_tmptemp[["Position X", "Position Y", "Position Z"]] = df_tmptemp.apply(processor.applywallpoints, axis=1)
        df_combined = pd.concat([df_tmptemp, df_visited], ignore_index=True)
        df_combined["Wall Number Sort"] = pd.to_numeric(df_combined["Wall Number"], errors='coerce')
        df_combined = df_combined.sort_values(by=["Wall Number Sort", "Point Name"]).drop(columns="Wall Number Sort")
        df_combined = df_combined.reset_index(drop=True)
        df_combined.index = df_combined.index + 1
        df_fitting.index = df_fitting.index + 1"""
        # fitting.oppsidespositionwall(distance, fitting_stage3, visited , count_minus_y)
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
