import re
import methodifcfindings as ifc_findings
import string
import numpy as np
import math


class loadmainTMP:
    def __init__(
        self,
        all_objs,
        stage2_rows,
        walls,
        stage3_results,
        wall_bss20,
        wall_bss12,
        origin_x,
        origin_y,
        floor,
        storeys,
        centerpoint_rows,
        opening,
        boxup,
        glass_walls,
    ):
        self.all_objs = all_objs
        self.stage2_rows = stage2_rows
        self.walls = walls
        self.stage3_results = stage3_results
        self.wall_bss20 = wall_bss20
        self.wall_bss20 = self.extract_tile_sizes(self.wall_bss20)
        self.opening = opening
        self.glass_walls = glass_walls
        self.glass_walls = min(self.glass_walls, key=lambda d: d.get("z", float("inf")))
        self.height20 = self.wall_bss20[0]["area"][1]
        first_wall = list(self.walls[0].values())[0]
        self.wallsheight50 = first_wall["area"][1]
        self.thickness = self.height20 + self.wallsheight50
        self.wall_bss12 = wall_bss12
        self.boxup = boxup
        self.alphabet_string = string.ascii_lowercase
        wall12 = self.wall_bss12[0]
        for wall in self.wall_bss20:
            tile_size = self.extract_tile_size(wall["name"])
            if tile_size:
                wall12["tile_size"] = tile_size
                break
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.floor = floor
        self.centerpoint_rows = centerpoint_rows
        x_widths = [
            w["centerpointwidth"]
            for w in self.centerpoint_rows
            if "X" in w["AxisDirection"]
        ]
        y_widths = [
            w["centerpointwidth"]
            for w in self.centerpoint_rows
            if "Y" in w["AxisDirection"]
        ]
        self.x_maxinternalwidth = (max(x_widths) + self.wallsheight50) * 2
        self.y_maxinternalwidth = (max(y_widths)) * 2
        self.storey_min_height = min(
            storeys, key=lambda s: s["elevation"], default={"elevation": 0}
        )["elevation"]
        self.index = 0
        self.tmptemp = []
        self.addTMP1()

    def extract_wall_id(self, name):
        match = re.search(r":(\d+)$", name)
        return match.group(1) if match else None

    def extract_tile_size(self, name):
        # Accept formats like: (600x600mm), 600x600mm, 600 x 600 mm, 600X600MM
        match = re.search(r"\(?\s*(\d+)\s*[xX]\s*(\d+)\s*mm\)?", name)
        if match:
            width = int(match.group(1))
            height = int(match.group(2))
            return f"({width}x{height}mm)"
        return None

    def extract_tile_sizes(self, walls):
        for wall in walls:
            name = wall.get("name", "")
            match = re.search(r"\(\d+x\d+mm\)", name)
            if match:
                wall["tile_size"] = match.group()  # e.g., (600x600mm)
            else:
                wall["tile_size"] = None
        return walls

    def getlongerwidthsurface(self):
        x_widths, y_widths = [], []
        height = 0
        for wall_dict in self.walls:
            for wall_name, data in wall_dict.items():
                axis = data.get("axis")
                width = data["area"][0]
                height = data["area"][1]
                if axis == "X":
                    x_widths.append((width, wall_name))
                elif axis == "Y":
                    y_widths.append((width, wall_name))
        x_sorted = sorted(x_widths, key=lambda x: x[0], reverse=True)
        y_sorted = sorted(y_widths, key=lambda x: x[0], reverse=True)
        if len(x_sorted) >= 2:
            second_x = int(x_sorted[1][0]) + height
        if len(y_sorted) >= 2:
            second_y = int(y_sorted[1][0]) + height
        return second_x, second_y

    def get_width_heights_intervals(self, next_w):
        tile_size = next_w.get("tile_size", "")
        match = re.search(r"\((\d+)x(\d+)mm\)", tile_size)
        width, height = 0, 0
        if match:
            width = int(match.group(1))
            height = int(match.group(2))
        return width, height

    def get_width_heights_interval(self, next_w):
        match = re.search(r"\((\d+)x(\d+)mm\)", next_w["name"])
        width, height = 0, 0
        if match:
            width = int(match.group(1))  # 600
            height = int(match.group(2))  # 150
        return width, height

    def find_opening_by_name(self, wall_name):
        return next((o for o in self.opening if o["name"] == wall_name), None)

    def addTMP1(self):
        wall_finishes_lowest_height = min(
            self.wall_bss20, key=lambda s: s["z"], default={"z": 0}
        )["z"]
        combined_walls = self.wall_bss20 + self.wall_bss12
        self.shower_walls = [
            wall
            for wall in combined_walls
            if wall.get("z", 0) - wall_finishes_lowest_height == 0
        ]
        for i, wall_dict in enumerate(self.walls):
            if i == self.index:
                wall_obj = list(wall_dict.values())[0]
                opening_match = self.find_opening_by_name(wall_obj["name"])
                first_w, _ = ifc_findings.find_closest_wall(wall_obj, self.wall_bss20)
                second_w, _ = ifc_findings.find_closest_wall(first_w, self.wall_bss20)
                width, height = self.get_width_heights_intervals(first_w)
                tiles_x, tiles_y, dist_needed = [], [], []
                x_min_limit = 0
                for w in [first_w, second_w]:
                    if opening_match:
                        vertices = opening_match.get("vertices")
                        if vertices is not None and len(vertices) > 0:
                            x_coords = np.array(vertices)[:, 0]  # get all X values
                            x_min_limit = x_coords.min()
                            x_max_limit = x_coords.max()
                    if not w:
                        continue  # Skip if None
                    x_val, y_val = w.get("x", 0), w.get("y", 0)
                    z_val = self.wall_bss12[0]["z"] - height
                    while z_val - height > 0:
                        z_val -= height
                    axis = w.get("axis")
                    if axis in "X":
                        tiles_x.append({"x": x_val, "z": z_val})
                    else:
                        tiles_y.append({"x": x_val, "z": z_val})
                    if w in self.shower_walls:
                        axis = w.get("axis")
                        facing_axis = w.get("facingaxis")
                        distance = 0
                        if axis in "X":
                            next_w_x = w.get("x", 0)
                            distance = next_w_x - self.thickness
                        else:
                            next_w_y = w.get("y", 0)
                            distance = next_w_y - self.thickness
                        if distance % width != 0:
                            area = w.get("area")
                            if axis in "X":
                                if area[0] % width != 0:
                                    if "-X" in facing_axis:
                                        x_val = (
                                            area[0] - self.thickness
                                        ) / 2 + self.thickness
                                    else:
                                        x_val = (
                                            x_val
                                            + ((area[0] - self.thickness) / 2)
                                            + self.thickness
                                        )
                                    tiles_x.append({"x": x_val, "z": z_val})
                            else:
                                if area[0] % width != 0:
                                    if "-Y" in facing_axis:
                                        y_val = (
                                            area[0] - self.thickness
                                        ) / 2 + self.thickness
                                    else:
                                        y_val = (
                                            y_val
                                            + ((area[0] - self.thickness) / 2)
                                            + self.thickness
                                        )
                                    tiles_y.append({"y": y_val, "z": z_val})
                    else:
                        vertices = self.boxup[0]["vertices"]
                        x_values = vertices[:, 0]
                        max_x = int(np.max(x_values))
                        factors = self.get_factors(max_x, x_values)
                        tile_width = min(factors)
                        x_val = self.boxup[0]["Position X"] + tile_width
                        tiles_x.append({"x": x_val, "z": z_val})
                tiles_x_structured = [t for t in tiles_x if isinstance(t, dict)]
                tiles_y_structured = [t for t in tiles_y if isinstance(t, dict)]
                tiles_x_structured.sort(key=lambda x: x["x"])
                tiles_y_structured.sort(key=lambda y: y["y"])
                axis = list(wall_dict.values())[0]["axis"]
                tile_list = (
                    [t["x"] for t in tiles_x_structured]
                    if axis == "X"
                    else [t["y"] for t in tiles_y_structured]
                )
                z_base = (
                    tiles_x_structured[0]["z"]
                    if axis == "X"
                    else tiles_y_structured[0]["z"]
                )
                repeatcount = int((self.storey_min_height - z_val) / height) + 1
                x_wallsurface, y_wallsurface = 0, 0
                if axis == "X":
                    dist_needed = 0 - wall_obj["y"]
                    y_wallsurface = wall_obj["y"] + dist_needed
                else:
                    dist_needed = 0 - wall_obj["x"]
                    x_wallsurface = wall_obj["x"] + dist_needed
                alphabet_list = list(self.alphabet_string)
                counter = 0
                for count, pos in enumerate(tile_list):
                    alpha = ""
                    for index, item in enumerate(alphabet_list):
                        if index == (count):
                            alpha = item
                    for i in range(repeatcount):
                        z = z_base + height * i
                        self.tmptemp.append(
                            {
                                "Wall Number": self.index + 1,
                                "Name": f"TMP{self.index + 1}S2{alpha}{i+1}",
                                "Position X": pos if axis == "X" else x_wallsurface,
                                "Position Y": y_wallsurface if axis == "X" else pos,
                                "Position Z": z,
                            }
                        )
                    counter += 1
                alpha = ""
                for index, item in enumerate(alphabet_list):
                    if index == (counter):
                        alpha = item
                for i in range(repeatcount):
                    z = z_base + height * i
                    self.tmptemp.append(
                        {
                            "Wall Number": self.index + 1,
                            "Name": f"TMP{self.index + 1}S2{alpha}{i+1}",
                            "Position X": x_min_limit if axis == "X" else x_wallsurface,
                            "Position Y": y_wallsurface if axis == "X" else x_min_limit,
                            "Position Z": z,
                        }
                    )
                counter += 1
                for index, item in enumerate(alphabet_list):
                    if index == (counter):
                        alpha = item
                for i in range(repeatcount):
                    z = z_base + height * i
                    self.tmptemp.append(
                        {
                            "Wall Number": self.index + 1,
                            "Name": f"TMP{self.index + 1}S2{alpha}{i+1}",
                            "Position X": x_max_limit if axis == "X" else x_wallsurface,
                            "Position Y": y_wallsurface if axis == "X" else x_max_limit,
                            "Position Z": z,
                        }
                    )
        self.index += 1
        self.addTMP2()

    def get_factors(self, n, x_value):
        return [i for i in x_value if i != 0 and n % i == 0 and i % 10 == 0]

    def addTMP2(self):
        for i, wall_dict in enumerate(self.walls):
            if i == self.index:
                wall_obj = list(wall_dict.values())[0]
                next_w, _ = ifc_findings.find_closest_wall_rotation(
                    wall_obj, self.wall_bss20 + self.wall_bss12
                )
                opening_match = self.find_opening_by_name(wall_obj["name"])
                width, height = self.get_width_heights_intervals(next_w)
                tiles_x, tiles_y, factors = [], [], []
                w = next_w
                x_val, y_val, area = w.get("x", 0), w.get("y", 0), w.get("area")
                wall_width, z_val = area[0], self.wall_bss12[0]["z"]
                z_max ,distance = 0 , 0
                if next_w in self.shower_walls:
                    axis = next_w.get("axis")
                    facing_axis = next_w.get("facingaxis")
                    if axis in "X":
                        next_w_x = next_w.get("x", 0)
                        distance = next_w_x - self.thickness
                    else:
                        next_w_y = next_w.get("y", 0)
                        distance = next_w_y - self.thickness
                    if distance % width != 0:
                        area = next_w.get("area")
                        if axis in "X":
                            if area[0] % width != 0:
                                if "-X" in facing_axis:
                                    x_val = (
                                        (area[0] - self.thickness) / 2
                                    ) + self.thickness
                                else:
                                    x_val = (
                                        x_val
                                        + ((area[0] - self.thickness) / 2)
                                        + self.thickness
                                    )
                        else:
                            if area[0] % width != 0:
                                if "-Y" in facing_axis:
                                    y_val = (
                                        area[0] - self.thickness
                                    ) / 2 + self.thickness
                                else:
                                    y_val = (
                                        y_val
                                        + ((area[0] - self.thickness) / 2)
                                        + self.thickness
                                    )
                if self.index + 1 == self.boxup[0]["Wall Number"]:
                    x_val = self.boxup[0]["Position X"]
                    vertices = self.boxup[0]["vertices"]
                    x_values, z_values = vertices[:, 0], vertices[:, 2]
                    max_x, max_z = int(np.max(x_values)), int(np.max(z_values))
                    factors = self.get_factors(max_x, x_values)
                    tiles_width = min(factors)
                    if self.boxup[0]["Position X"] <= self.thickness:
                        tiles_width = width - tiles_width
                    z_val = self.wall_bss12[0]["z"] - height
                    while z_val - height > 0:
                        z_val -= height
                    x_val += tiles_width
                    z_max = self.boxup[0]["Position Z"] + max_z
                elif next_w in self.shower_walls or self.index + 1 == len(self.walls):
                    z_val = self.wall_bss12[0]["z"] - height
                    while z_val - height > 0:
                        z_val -= height
                facing = w.get("facingaxis")
                if facing in ["+X", "-X"]:
                    current = x_val
                    if facing == "+X":
                        end = w.get("x", 0) + wall_width
                        if (
                            w in self.shower_walls
                            or self.index + 1 == self.boxup[0]["Wall Number"]
                        ):
                            end = w.get("x", 0)
                        while current < end:
                            if (
                                current > self.thickness
                                and current < self.x_maxinternalwidth
                            ):
                                tiles_x.append({"x": current, "z": z_val})
                            current += width
                    elif facing == "-X":
                        end = current - wall_width
                        if (
                            w in self.shower_walls
                            or self.index + 1 == self.boxup[0]["Wall Number"]
                        ):
                            end = w.get("x", 0)
                        while current < end:
                            if (
                                current > self.thickness
                                and current < self.x_maxinternalwidth
                            ):
                                tiles_x.append({"x": current, "z": z_val})
                            current += width
                elif facing in ["+Y", "-Y"]:
                    if facing == "+Y":
                        current = y_val
                        if current < self.glass_walls["y"]:
                            current = self.glass_walls["y"]
                        end = y_val + wall_width
                        while current < end:
                            if (
                                current > self.thickness
                                and current < self.y_maxinternalwidth
                            ):
                                tiles_y.append({"y": current, "z": z_val})
                            current += width
                    elif facing == "-Y":
                        current = y_val
                        end = y_val - wall_width
                        if end < self.glass_walls["y"]:
                            vertices = w.get("vertices")
                            x_values = vertices[:, 0]
                            unique_x = np.unique(x_values)
                            unique_x = unique_x[unique_x != 0]
                            min_x, max_x = min(unique_x), max(unique_x)
                            current = y_val - min_x
                            end = y_val - max_x
                            while current > end:
                                if (
                                    current > self.thickness
                                    and current < self.y_maxinternalwidth
                                ):
                                    tiles_y.append({"y": current, "z": z_val})
                                current -= width
                        else:
                            tiles_y.append({"y": end, "z": z_val})
                tiles_x_structured = [t for t in tiles_x if isinstance(t, dict)]
                tiles_y_structured = [t for t in tiles_y if isinstance(t, dict)]
                tiles_x_structured.sort(key=lambda x: x["x"])
                tiles_y_structured.sort(key=lambda y: y["y"])
                axis = list(wall_dict.values())[0]["axis"]
                tile_list = (
                    [t["x"] for t in tiles_x_structured]
                    if axis == "X"
                    else [t["y"] for t in tiles_y_structured]
                )
                z_base = (
                    tiles_x_structured[0]["z"]
                    if axis == "X"
                    else tiles_y_structured[0]["z"]
                )
                axis = list(wall_dict.values())[0]["axis"]
                x_wallsurface, y_wallsurface = 0, 0
                if axis == "X":
                    dist_needed = 0 - wall_obj["y"]
                    y_wallsurface = wall_obj["y"] + dist_needed
                else:
                    dist_needed = 0 - wall_obj["x"]
                    x_wallsurface = wall_obj["x"] + dist_needed
                alphabet_list = list(self.alphabet_string)
                z_min_limit, z_max_limit = 0, 0
                y_min_limit, y_max_limit = 0, 0
                if opening_match:
                    vertices = opening_match.get("vertices")
                    if vertices is not None and len(vertices) > 0:
                        y_coords = np.array(vertices)[:, 1]  # get all Y values
                        z_coords = np.array(vertices)[:, 2]  # get all Z values
                        y_min_limit, y_max_limit = y_coords.min(), y_coords.max()
                        z_min_limit, z_max_limit = z_coords.min(), z_coords.max()
                repeatcount = int((self.storey_min_height - z_val) / height) + 1
                for count, pos in enumerate(tile_list):
                    alpha = ""
                    for index, item in enumerate(alphabet_list):
                        if index == (count):
                            alpha = item
                    for i in range(repeatcount):
                        z = z_base + height * i
                        if opening_match:
                            if (
                                y_min_limit <= pos <= y_max_limit
                                and z_min_limit <= z <= z_max_limit
                            ):
                                continue
                        if self.index + 1 == self.boxup[0]["Wall Number"]:
                            if (
                                z_max <= z
                                and self.boxup[0]["Position X"]
                                <= pos
                                <= self.boxup[0]["Position X"] + factors[1]
                            ):
                                continue
                            elif z_base < z:
                                continue
                        self.tmptemp.append(
                            {
                                "Wall Number": self.index + 1,
                                "Name": f"TMP{self.index + 1}S2{alpha}{i+1}",
                                "Position X": pos if axis == "X" else x_wallsurface,
                                "Position Y": y_wallsurface if axis == "X" else pos,
                                "Position Z": z,
                            }
                        )
                self.index += 1
        self.getTMPFloor()

    def getTMPFloor(self):
        floor_finishes = sorted(
            [
                obj
                for obj in self.floor
                if "floor finishes" in obj["name"].lower()
                and obj.get("area") != (0, 0, 0)
            ],
            key=lambda obj: obj["x"],
        )
        lowest_floor_y = min(floor_finishes, key=lambda s: s["y"], default={"y": 0})[
            "y"
        ]
        counters = 0  # global X-letter index
        tmpfloor, distance_needed = [], []
        for floor in floor_finishes:
            distance_needed.append(
                {
                    "name": floor["name"],
                    "remaining_distance": self.boxup[0]["Position X"] - floor["x"],
                }
            )
        min_item = min(distance_needed, key=lambda d: d["remaining_distance"])
        for floor in floor_finishes:
            width, height = self.get_width_heights_interval(floor)
            vertices = floor["vertices"]
            min_x = math.ceil(np.min(vertices[:, 0]) / 10) * 10
            max_x = math.ceil(np.max(vertices[:, 0]) / 10) * 10
            min_y = math.ceil(np.min(vertices[:, 1]) / 10) * 10
            max_y = math.ceil(np.max(vertices[:, 1]) / 10) * 10
            tiles_x, tiles_y = [], []
            # X tiles
            if floor["x"] == min_x + (max_x - min_x) / 2:
                current = floor["x"] - (width / 2)
                end = floor["x"] + (width / 2)
            elif floor["x"] < min_y + (max_y - min_y) / 2:
                current = floor["x"] - width
            else:
                current = floor["x"]
                end = max_x
            if min_item["name"] in floor["name"]:
                current = self.boxup[0]["Position X"]
                vertices = self.boxup[0]["vertices"]
                x_values = vertices[:, 0]
                max_x = int(np.max(x_values))
                factors = self.get_factors(max_x, x_values)
                tiles_width = min(factors)
                if self.boxup[0]["Position X"] <= self.thickness:
                    tiles_width = width - tiles_width
                current += tiles_width
            while current <= end:
                if current >= self.thickness and current <= self.x_maxinternalwidth:
                    tiles_x.append({"x": current, "z": floor["z"]})
                current += width
            # Y tiles
            if floor["y"] == min_y + (max_y - min_y) / 2:
                current = floor["y"] - ((max_y - min_y) / 2)
            elif floor["y"] < min_y + (max_y - min_y) / 2:
                current = floor["y"] - width
                while current < min_y:
                    current -= width
                if current != lowest_floor_y:
                    current = lowest_floor_y
            else:
                current = floor["y"]
            end = max_y
            while current < end:
                if current > self.thickness and current < self.y_maxinternalwidth:
                    tiles_y.append({"y": current, "z": floor["z"]})
                current += height
            for xpos in tiles_x:
                alpha = (
                    self.alphabet_string[counters]
                    if counters < len(self.alphabet_string)
                    else f"z{counters}"
                )
                for count_y, ypos in enumerate(tiles_y):
                    tmpfloor.append(
                        {
                            "Wall Number": "F",
                            "Name": f"TMP{self.index + 1}S2{alpha}{count_y+1}",
                            "Position X": xpos["x"],
                            "Position Y": ypos["y"],
                            "Position Z": floor["z"],
                        }
                    )
                counters += 1  # ✅ moved here (once per X-column)
        self.tmptemp.extend(tmpfloor)
        self.returnalltmps()

    def returnalltmps(self):
        return self.tmptemp
