import re , string , math
import methodifcfindings as ifc_findings
import poscheck as poscheckPBU


class getTMP(object):
    def __init__(
        self,
        all_objs,
        walls,
        wall_bss20,
        materials,
        model_lines_walls,
        floor,
        centerpoint_rows,
        storeys,
        externalxmax_width,
        externalymax_width,
        door,
        origin_x,
        origin_y
    ):
        self.all_objs = all_objs
        self.walls = walls
        self.centerpoint_rows = centerpoint_rows
        self.wall_bss20 = wall_bss20
        self.model_lines_walls = model_lines_walls
        self.materials = materials
        self.floor = floor
        min_thickness = min(
            wall_data["area"][1]
            for wall_dict in self.walls
            for wall_data in wall_dict.values()
        )
        self.min_thickness20 = min(wall["area"][1] for wall in self.wall_bss20)
        self.thickness = min_thickness + self.min_thickness20
        self.externalxmax_width = externalxmax_width
        self.externalymax_width = externalymax_width
        self.door = door
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.index = 0
        self.storeys = storeys
        self.storey_min_height = min(
            storeys, key=lambda s: s["elevation"], default={"elevation": 0}
        )["elevation"]
        z_values = [w["z"] for w in self.wall_bss20 if "z" in w]
        self.getlowestground = min(z_values)
        self.alphabet_list = list(string.ascii_lowercase)
        self.tmptemp = []
        self.dist_neededarray = []
        self.maxwidths = []
        self.build_all_tmp()

    def returnalpha(self, count):
        for index, item in enumerate(self.alphabet_list):
            if index == (count):
                return item

    def _get_model_lines_for_wall(self, wall_idx):
        wn = wall_idx + 1
        return [row for row in self.model_lines_walls if row.get("Wall Number") == wn]

    def build_all_tmp(self):
        self.tmptemp = []
        self._seen_xyz_per_wall = {}
        self._seen_name_per_wall = {}
        for wall_idx in range(len(self.walls)):
            self._build_wall(wall_idx)
        self.getTMPFloor()

    def _append_unique_point(self, row):
        wn = row.get("Wall Number")
        if wn is None:
            return
        self._seen_xyz_per_wall.setdefault(wn, set())
        self._seen_name_per_wall.setdefault(wn, set())
        name_key = row.get("Name")
        xyz_key = (row.get("GX"), row.get("GY"), row.get("GZ"))
        if (name_key in self._seen_name_per_wall[wn]) or (
            xyz_key in self._seen_xyz_per_wall[wn]
        ):
            return
        self._seen_name_per_wall[wn].add(name_key)
        self._seen_xyz_per_wall[wn].add(xyz_key)
        self.tmptemp.append(row)

    def setgetwall(self, w, wall_idx):
        if not hasattr(self, "_seen_wall_rows"):
            self._seen_wall_rows = set()
        wall_name = w.get("name", "")
        wall_key = (wall_idx, wall_name)
        if wall_key in self._seen_wall_rows:
            return
        self._seen_wall_rows.add(wall_key)
        area = w.get("area", (0, 0, 0))
        if isinstance(area, (tuple, list, np.ndarray)) and len(area) >= 3:
            width, height = area[0], area[2]
        else:
            width = height = 0
        if not width or not height:
            verts = w.get("vertices")
            if isinstance(verts, np.ndarray) and verts.size > 0:
                width, _, height = poscheckPBU.lengths_xyz(verts)
        self.tmptemp.append(
            {
                "Marking Type": "Wall",
                "Name": wall_name,
                "GX": w.get("x", 0),
                "GY": w.get("y", 0),
                "GZ": w.get("z", 0),
                "Wall Number": wall_idx + 1,
                "Shape Type": "",
                "Status": "blank",
                "Quadrant": 1,
                "Unnamed": "",
                "Width": width,
                "Height": height,
                "Orientation": "",
                "Diameter": "",
            }
        )

    def _build_wall(wall_idx)(self):
        wall_dict = self.walls[wall_idx]
        wall_obj = list(wall_dict.values())[0]
        opening = self.find_opening_by_name(wall_obj["name"])
        axis_obj = wall_obj["axis"]
        main_area = wall_obj.get("area", (0, 0, 0))
        width = main_area[0]
        axis_letter = axis_obj.lower()
        model_lines = self._get_model_lines_for_wall(wall_idx)
        z_ref = min(
            (r.get("SGZ", 0) for r in model_lines if r.get("SGZ", 0) > 0), default=0
        )
        edge_max = (
            self.externalxmax_width if axis_letter == "x" else self.externalymax_width
        )
        shape_type = 1
        origin = self.origin_x if axis_letter == "x" else self.origin_y
        a_min, a_max, z_min, z_max = poscheckPBU.getopeningvert(opening, axis_obj)
        added_wall_names = set()
        w2, _ = ifc_findings.find_closest_wall(
            wall_obj, self.wall_bss20 + self.walls_bss_no_tile
        )
        if w2 and w2.get("axis") == axis_obj:
            wname2 = w2.get("name", "")
            if wname2 not in added_wall_names:
                self.setgetwall(w2, wall_idx)
                added_wall_names.add(wname2)
            area, facing = w2.get("area"), w2.get("facingaxis")
            wall_width = (area[0] if area else 0) or 0
            if wall_width == 0:
                verts = w2.get("vertices")
            if isinstance(verts, np.ndarray) and verts.size > 0:
                wall_width = float(verts[:, 0].max() - verts[:, 0].min())
            sweep_axis = "x" if str(facing).endswith("X") else "y"
            sign = 1 if str(facing).startswith("+") else -1
            base = w2.get(sweep_axis, 0)
            start, end = sorted((base, base + sign * wall_width))
            key = "SGX" if sweep_axis == "x" else "SGY"
            endkey = "EGX" if sweep_axis == "x" else "EGY"
            seen_vals, tiles = set(), []
            for r in model_lines:
                v = r.get(key, 0)
                vend = r.get(endkey, 0)
                if v in seen_vals:
                    continue
                seen_vals.add(v)
                inside = (
                    (start < v < end)
                    if sweep_axis == "x"
                    else (start <= v < end - self.thickness)
                )
                insideend = (
                    (start < vend - self.thickness <= end)
                    if sweep_axis == "x"
                    else (start <= vend < end - self.thickness)
                )
                if inside:
                    tiles.append(
                        {"x": r.get("SGX", 0), "y": r.get("SGY", 0), "z": z_ref}
                    )
                    if round((end - start) / self.width) <= 1 and sweep_axis == "y":
                        shape_type = 4
                    if insideend:
                        if round((end - start) / self.width) > 1:
                            tiles.append(
                                {
                                    "x": r.get("EGX", 0),
                                    "y": r.get("EGY", 0),
                                    "z": z_ref,
                                }
                            )
            tiles.sort(key=lambda t: t[sweep_axis])
            vals_sorted = [t[sweep_axis] for t in tiles]
            vals_sorted = [v for v in vals_sorted if v > self.EPS]
            pos_list = poscheckPBU._unique_in_order(vals_sorted, tol=0)
            pos_list = [
                p
                for p in pos_list
                if not poscheckPBU._is_in_edge_band(
                    p, edge_max=edge_max, thickness=self.thickness, origin=origin
                )
            ]
            if pos_list:
                anchor_x = tiles[0]["x"] if tiles else 0
                anchor_y = tiles[0]["y"] if tiles else 0
                z_base = z_ref
                repeatcount = (
                    int((self.storey_min_height - z_ref) / self.height) + 1
                )
                openingcheckpos = []
                for col_i, pos in enumerate(pos_list):
                    alpha = self.returnalpha(col_i)
                    if pos > w2.get("x", 0) and sweep_axis == "x":
                        shape_type = 4
                    for r in range(r_max + 1):
                        z = z_base + self.height * r
                        if (
                            opening
                            and a_min is not None
                            and a_min <= pos <= a_max
                            and z_min <= z <= z_max
                        ):
                            openingcheckpos.append(
                                {
                                    "x": pos if axis_obj == "X" else anchor_x,
                                    "y": anchor_y if axis_obj == "X" else pos,
                                    "z": z,
                                }
                            )
                            continue
                        row = {
                            "Marking Type": "Tiles Point",
                            "Name": f"TW{wall_idx + 1}MP{alpha}{r+1}",
                            "GX": pos if axis_obj == "X" else anchor_x,
                            "GY": anchor_y if axis_obj == "X" else pos,
                            "GZ": z,
                            "Wall Number": wall_idx + 1,
                            "Shape Type": shape_type,
                            "Status": "blank",
                            "Quadrant": 1,
                            "Unnamed": "",
                        }
                        self._append_unique_point(row)
                if openingcheckpos and opening["opening_type"] == "window":
                    ymax_val = max(p["y"] for p in openingcheckpos)
                    windowy_vals = [
                        p for p in openingcheckpos if p["y"] == ymax_val
                    ]
                    alpha_last = (
                        self.returnalpha(len(pos_list)) if pos_list else "a"
                    )
                    for i, p in enumerate(windowy_vals):
                        if ymax_val > w2.get("y", 0) and facing == "-Y":
                            continue
                        elif (
                            ymax_val > w2.get("y", 0) + wall_width
                            and facing == "+Y"
                        ):
                            continue
                        row = {
                            "Marking Type": "Tiles Point",
                            "Wall Number": wall_idx + 1,
                            "Name": f"TW{wall_idx + 1}MP{alpha_last}{i+1}",
                            "GX": (
                                (p["x"] + w2.get("x", 0)) / 2
                                if axis_obj == "X"
                                else p["x"]
                            ),
                            "GY": (
                                p["y"]
                                if axis_obj == "X"
                                else (p["y"] + w2.get("y", 0)) / 2
                            ),
                            "GZ": p["z"],
                            "Shape Type": 6,
                            "Status": "blank",
                            "Quadrant": 1,
                            "Unnamed": "",
                        }
                        self._append_unique_point(row)

    def getTMPFloor(self):
        floor_finishes = sorted(
            [
                obj
                for obj in self.floor
                if "floor finishes" in obj["name"].lower()
                and obj.get("area") != (0, 0, 0)
                and obj.get("z", 0) < 0
            ],
            key=lambda obj: obj["x"],
        )
        counter = 0
        for i, floor in enumerate(floor_finishes):
            xs, ys = [], []
            for wall in self.model_lines_walls:
                wn = wall.get("Wall Number", "")
                if str(wn).strip().upper() == "F":
                    if wall["SGZ"] == floor.get("z", 0):
                        xs.append(wall.get("SGX"))
                        xs.append(wall.get("EGX"))
                        ys.append(wall.get("SGY"))
                        ys.append(wall.get("EGY"))
            xs = [v for v in xs if v > self.EPS]
            ys = [v for v in ys if v > self.EPS]
            xs = poscheckPBU.unique_numbers(xs)
            ys = poscheckPBU.unique_numbers(ys)
            xs.sort()
            ys.sort()
            main_alpha = self.returnalpha(i)
            minx, miny, maxx, maxy = poscheckPBU.bbox_xy(floor.get("vertices", []))
            if (self.lowest_z + self.height20) == floor.get("z", 0):
                shape_type = 3
                for x in xs:
                    count = 0
                    appended = False
                    alpha = self.returnalpha(counter)
                    for y in ys:
                        if not (minx < x < maxx) or not (miny < y < maxy):
                            continue
                        self.tmptemp.append(
                            {
                                "Marking Type": "Tiles Point",
                                "Name": f"TW{len(self.walls) + 1}{main_alpha}MP{alpha}{count+1}",
                                "GX": x,
                                "GY": y,
                                "GZ": floor.get("z", 0),
                                "Wall Number": "F",
                                "Shape Type": shape_type,
                                "Status": "blank",
                                "Quadrant": 1,
                                "Unnamed": "",
                            }
                        )
                        count += 1
                        appended = True
                    if appended:
                        shape_type +=1
                        counter += 1
            else:
                repeatcount = int((max(ys) - min(ys)) / self.height)
                for x in xs:
                    alpha = self.returnalpha(counter)
                    if x < floor.get("x", 0) or x >= maxx:
                        continue
                    for i in range(repeatcount):
                        y = min(ys) + self.height * (i + 1)
                        self.tmptemp.append(
                            {
                                "Marking Type": "Tiles Point",
                                "Name": f"TW{len(self.walls) + 1}{main_alpha}MP{alpha}{i+1}",
                                "GX": x,
                                "GY": y,
                                "GZ": floor.get("z", 0),
                                "Wall Number": "F",
                                "Shape Type": 1,
                                "Status": "blank",
                                "Quadrant": 1,
                                "Unnamed": "",
                            }
                        )
                    counter += 1
        self.returnalltmps()

    def returntmp(self):
        return self.tmptemp + self.floor_tmps

    def get_width_heights_intervals(self, next_w):
        name = next_w["name"]
        match = re.search(r"(\d+)\s*[xX]\s*(\d+)\s*MM", name, re.IGNORECASE)
        if match:
            width, height = int(match.group(1)), int(match.group(2))
            return width, height

