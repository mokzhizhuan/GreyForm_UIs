import pandas as pd
import ifcopenshell
import methodifcfindings as ifc_findings
import loadtmp6sides as tmps6sidesPBU
import fitting_width as fitting
import gettmps as tmps
import getstagesvar as stage_val
import fitting_pointbox as pointbox
from ifcopenshell.util.placement import get_local_placement
import robot_pos as setuprobot
import annotation as modellines
import material as mats
import ifcopenshell , re , heapq

class data_draft(object):
    def __init__(self, ifc_file, model_sides, usb_path):
        self.ifc_file = ifc_file
        self.model_sides = model_sides
        self.usb_path = usb_path

    def analysis(self):
        ifc_file = ifcopenshell.open(self.ifc_file)
        # get the data  wall , opening , floor
        all_walls = ifc_findings.process_elements(
            ifc_file.by_type("IfcWall"), "basic wall:bss"
        )
        site = ifc_file.by_type("IfcSite")[0]  # Usually only one site
        placement = site.ObjectPlacement
        while hasattr(placement, "PlacementRelTo") and placement.PlacementRelTo:
            placement = placement.PlacementRelTo
        loc = placement.RelativePlacement.Location
        origin_x, origin_y, ____ = loc.Coordinates
        origin_x, origin_y = round(origin_x), round(origin_y)
        box_up = ifc_findings.process_elements(ifc_file.by_type("IfcWall"), "box")
        walls_bss50 = [w for w in all_walls if "basic wall:bss.50" in w["name"].lower()]
        tile_pattern = re.compile(r"no pattern", re.IGNORECASE)
        walls_bss20, walls_bss_no_tile = [], []
        for w in all_walls:
            name = w["name"].lower()
            if "glass" in name or "basic wall:bss.50" in name:
                continue
            if tile_pattern.search(name):
                walls_bss20.append(w)
            else:
                walls_bss_no_tile.append(w)
        openings = ifc_findings.process_elements(
            ifc_file.by_type("IfcOpeningElement"), "basic wall:bss.50"
        )
        door = ifc_findings.process_elements(ifc_file.by_type("IfcDoor"), "opening")
        floors = ifc_findings.process_elements(ifc_file.by_type("IfcSlab"), "floor")
        seen, same, fallback = set(), {}, []
        floors = [f for f in floors if not (f["name"] in seen or seen.add(f["name"]))]
        other_floor = [f for f in floors if "floor:bss.60" not in f["name"].lower()]
        all_objs = ifc_findings.process_elements(ifc_file.by_type("IfcElement"), "")
        storeys = ifc_findings.extract_storeys(ifc_file)
        materials = mats.getmaterial(ifc_file, names_only=True, first_only=True)
        modelline = modellines.getannotation(self.ifc_file)
        if door:
            for doors in door:
                closest_wall, distance = ifc_findings.find_closest_wall(
                    doors, walls_bss50
                )
                if closest_wall:
                    same[closest_wall["name"]] = closest_wall
        else:
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
        visited, tmptemp, unvisited = [], [], walls_bss50.copy()
        floor_offset, offset = 0, 0
        internalx_width, internaly_width = 0, 0
        internalxmax_width, internalymax_width = 0, 0
        internal_x_width, internal_y_width = [], []
        if start:
            if isinstance(start, list):
                if len(start) == 1:
                    start = start[0]
            unvisited = [w for w in unvisited if w["name"] != start["name"]]
            start_wall = next(
                (w for w in walls_bss50 if w["name"] == start["name"]), start
            )
            visited = [{start["name"]: start_wall}]
            (
                internalx_width,
                internaly_width,
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
            floor_offset = abs(max((f.get("z", 0) for f in floors), default=0))
            offset, curr = abs(start["z"]), start
            while unvisited:
                next_w, _ = ifc_findings.find_closest_wall(curr, unvisited)
                if not next_w:
                    break
                visited.append({next_w["name"]: next_w})
                unvisited = [w for w in unvisited if w["name"] != next_w["name"]]
                curr = next_w
        if self.model_sides != len(visited):
            return None
        if len(visited) == 6:
            top_twofloor_z = heapq.nlargest(2, (f["z"] for f in floors))
        walls_facing_plus_y = [
            list(w.values())[0]
            for w in visited
            if list(w.values())[0]["facingaxis"] == "+Y"
        ]
        walls_facing_minus_y = [
            list(w.values())[0]
            for w in visited
            if list(w.values())[0]["facingaxis"] == "-Y"
        ]
        count_plus_y, count_minus_y = len(walls_facing_plus_y), len(
            walls_facing_minus_y
        )
        if count_minus_y == 2:
            ifc_findings.swap_last_two(internal_x_width)
            internal_y_width.sort()
            ymaxwidths.sort()
            ifc_findings.swap_first_two(ymaxwidths)
            ifc_findings.swap_last_two(xmaxwidths)
        if count_minus_y == 2 or count_plus_y == 2:
            internal_y_width = fitting.compare_width_y(
                walls_facing_minus_y, internal_y_width, count_plus_y, count_minus_y
            )
        thickness = walls_bss50[0]["area"][1] + walls_bss20[1]["area"][1]
        stage2_rows, centerpoint_rows, stage3_objects, df_checklist = (
            stage_val.getstage2andstage3(
                all_objs,
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
            )
        )
        glass_walls = [
            obj
            for obj in all_objs
            if "glass" in obj["name"].lower()
            and not (
                obj.get("x", 0) == 0 and obj.get("y", 0) == 0 and obj.get("z", 0) == 0
            )
        ]
        df_checklist.columns = df_checklist.iloc[0]
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
            glass_walls,
            count_minus_y,
            count_plus_y,
            centerpoint_rows,
            walls_bss20,
            walls_bss_no_tile,
        )
        boxup = fitting.assign_nearest_fitting_rotation(
            visited,
            box_up,
            other_floor,
            wall_info,
            glass_walls,
            count_minus_y,
            count_plus_y,
            centerpoint_rows,
        )
        walls_bss20_wall_num = fitting.assign_nearest_fitting_rotation(
            visited,
            walls_bss20 + walls_bss_no_tile,
            other_floor,
            wall_info,
            glass_walls,
            count_minus_y,
            count_plus_y,
            centerpoint_rows,
        )
        model_lines_walls = fitting.assign_nearest_line(
            visited,
            modelline,
            storeys,
            other_floor,
            wall_info,
            glass_walls,
            count_minus_y,
            count_plus_y,
            centerpoint_rows,
            walls_bss20,
            walls_bss_no_tile,
        )
        model_lines_walls.sort(
            key=lambda x: (
                int(x["Wall Number"])
                if str(x["Wall Number"]).isdigit()
                else float("inf")
            )
        )
        fitting_stage3.sort(
            key=lambda x: (
                int(x["Wall Number"])
                if str(x["Wall Number"]).isdigit()
                else float("inf")
            )
        )
        if len(visited) == 4:
            Tmpholder = tmps.getTMP(
                all_objs,
                visited,
                walls_bss20,
                materials,
                model_lines_walls, 
                other_floor,
                centerpoint_rows,
                storeys,
                externalxmax_width,
                externalymax_width,
                door,
                origin_x,
                origin_y
            )
            tmptemp = Tmpholder.returntmp()
        else:
            Tmpholder = tmps6sidesPBU.loadTMP6sides(
                all_objs,
                stage2_rows,
                visited,
                walls_bss20,
                walls_bss_no_tile,
                materials,
                model_lines_walls, 
                other_floor,
                storeys,
                centerpoint_rows,
                fallback,
                boxup,
                walls_bss20_wall_num,
                externalxmax_width,
                externalymax_width,
                origin_x,
                origin_y
            )
            tmptemp, thickness = Tmpholder.returnalltmps()
        df_tmptemp = pd.DataFrame(tmptemp)
        df_visited = pd.DataFrame(stage2_rows)
        df_fitting = pd.DataFrame(fitting_stage3)
        df_combined = pd.concat([df_tmptemp, df_visited], ignore_index=True)
        df_combined["Wall Number Sort"] = pd.to_numeric(
            df_combined["Wall Number"], errors="coerce"
        )
        df_combined = df_combined.sort_values(by=["Wall Number Sort", "Name"]).drop(
            columns="Wall Number Sort"
        )
        df_combined[["Width", "Height"]] = df_combined.apply(
            lambda row: fitting.applyexternal(
                row, internal_y_width, internal_x_width, visited
            ),
            axis=1,
        )
        fittingbox = pointbox.boundingboxpoint(fitting_stage3, all_objs)
        fittingboundingbox = fittingbox.returnallfitting()
        df_fitting[["GX", "GY", "GZ"]] = df_fitting.apply(
            lambda row: setuprobot.setupfittingrequirement(
                row, all_objs, fittingboundingbox, df_checklist
            ),
            axis=1,
        )
        df_fitting[["Width", "Height"]] = df_fitting.apply(
            lambda row: fitting.applyexternal(
                row, internal_y_width, internal_x_width, visited
            ),
            axis=1,
        )
        df_combined = setuprobot.insert_L_cols_between_GZ_and_width(df_combined)
        df_fitting = setuprobot.insert_L_cols_between_GZ_and_width(df_fitting)
        df_combined[["Position X", "Position Y", "Position Z"]] = df_combined.apply(
            lambda row: setuprobot.setuprobotposition(
                row, stage2_rows, visited, internalxmax_width, internalymax_width, thickness , origin_x, origin_y
            ),
            axis=1,
        )
        df_fitting[["Position X", "Position Y", "Position Z"]] = df_fitting.apply(
            lambda row: setuprobot.setuprobotposition_fitting(
                row, stage2_rows, visited, internalxmax_width, internalymax_width, thickness , origin_x, origin_y
            ),  
            axis=1,
        )
        df_combined = df_combined.dropna(subset=["Position X", "Position Y", "Position Z"])
        df_fitting = df_fitting.dropna(subset=["Position X", "Position Y", "Position Z"])
        df_combined = df_combined.drop(columns=["GX", "GY", "GZ", "Type"], errors="ignore")
        df_fitting = df_fitting.drop(columns=["GX", "GY", "GZ"], errors="ignore")
        for col in ["Orientation", "Diameter"]:
            if col not in df_combined.columns:
                df_combined[col] = ""   # create the column if missing
            else:
                df_combined[col] = df_combined[col].fillna("").astype(str)
        df_combined_all = pd.concat([df_combined, df_fitting], ignore_index=True)
        with pd.ExcelWriter(f"{self.usb_path}/PBU_TERRAHL2.xlsx", engine="openpyxl") as writer:
            for df, sheet in [(df_combined, "Stage 2"), (df_fitting, "Stage 3")]:
                df.reset_index(drop=True, inplace=True)
                df.index += 1
                df.to_excel(writer, index=True, sheet_name=sheet)
        return df_combined_all

if __name__ == "__main__":
    main()
