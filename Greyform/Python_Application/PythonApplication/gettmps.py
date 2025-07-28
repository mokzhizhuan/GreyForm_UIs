import re
import methodifcfindings as ifc_findings
import string
import math


class getTMP(object):
    def __init__(
        self,
        all_objs,
        stage2_rows,
        walls,
        wall_bss20,
        origin_x,
        origin_y,
        floor,
        centerpoint_rows,
        storeys,
        box_up,
        externalxmax_width,
        door,
    ):
        self.all_objs = all_objs
        self.stage2_rows = stage2_rows
        self.walls = walls
        self.centerpoint_rows = centerpoint_rows
        self.wall_bss20 = wall_bss20
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.floor = floor
        self.boxup = box_up
        min_thickness = min(
            wall_data["area"][1]
            for wall_dict in self.walls
            for wall_data in wall_dict.values()
        )
        min_thickness20 = min(wall["area"][1] for wall in self.wall_bss20)
        self.thickness = min_thickness + min_thickness20
        self.externalxmax_width = externalxmax_width
        self.door = door
        self.index = 0
        self.storeys = storeys
        self.storey_min_height = min(
            storeys, key=lambda s: s["elevation"], default={"elevation": 0}
        )["elevation"]
        self.tmptemp = []
        self.dist_neededarray = []
        self.maxwidths = []
        self.getTMP1()

    def getTMP1(self):
        for i, wall_dict in enumerate(self.walls):
            if i == self.index:
                maxheight, maxwidth = 0, 0
                for wallsmax in self.stage2_rows:
                    if self.index + 1 == wallsmax["Wall Number"]:
                        maxwidth = wallsmax["Width"]
                        maxheight = wallsmax["Height"]
                ceilingzstart = self.storey_min_height
                next_w, _ = ifc_findings.find_closest_wall_rotation(
                    list(wall_dict.values())[0], self.wall_bss20
                )
                width, height = self.get_width_heights_intervals(next_w)
                x_val = self.externalxmax_width - height + self.thickness
                tiles = []
                tiles.append(x_val)
                while x_val - height > 0:
                    x_val -= height
                    if x_val > self.thickness:
                        tiles.append(x_val)
                tiles.sort()
                repeatcount = int((ceilingzstart - width) / width) + 1
                dist_needed = 0 - (list(wall_dict.values())[0]["y"] + self.origin_y)
                y_wallsurface = (
                    list(wall_dict.values())[0]["y"] + self.origin_y
                ) + dist_needed
                door = self.door[0] 
                x_origin = door["x"]
                vertices = door["vertices"]
                door_minx = x_origin + vertices[:, 0].min()
                door_maxx = x_origin + vertices[:, 0].max()
                count = 0
                for xpos in tiles:
                    alphabet_string = string.ascii_lowercase
                    alphabet_list = list(alphabet_string)
                    alpha = ""
                    for index, item in enumerate(alphabet_list):
                        if index == (count):
                            alpha = item
                    counter = 0
                    if door_minx <= xpos <= door_maxx:
                        continue
                    for i in range(repeatcount):
                        z = width + width * i
                        self.tmptemp.append(
                            {
                                "Wall Number": self.index + 1,
                                "Point Name": f"TMP{self.index + 1}S2{alpha}{counter+1}",
                                "Position X": int(xpos),
                                "Position Y": y_wallsurface,
                                "Position Z": z,
                                "Width": maxwidth,
                                "Height": maxheight,
                            }
                        )
                        counter += 1
                    count += 1
        self.index += 1
        self.getTMP2()

    def getTMP2(self):
        for i, wall_dict in enumerate(self.walls):
            if i == self.index:
                ceilingzstart = self.storey_min_height
                maxheight, maxwidth = 0, 0
                for wallsmax in self.stage2_rows:
                    if self.index + 1 == wallsmax["Wall Number"]:
                        maxwidth = wallsmax["Width"]
                        maxheight = wallsmax["Height"]
                next_w, _ = ifc_findings.find_closest_wall_rotation(
                    list(wall_dict.values())[0], self.wall_bss20
                )
                width, height = self.get_width_heights_intervals(next_w)
                wall_data = list(wall_dict.values())[0]
                axis = wall_data["axis"]
                tiles = []
                if axis == "X":
                    x_val = self.externalxmax_width - height + self.thickness
                    tiles.append(x_val)
                    while x_val - height > 0:
                        x_val -= height
                        if x_val > self.thickness:
                            tiles.append(x_val)
                elif wall_data["axis"] == "Y":
                    vertices = self.boxup[0]["vertices"]
                    y_values = vertices[:, 1]
                    unique_y = sorted(set(y for y in y_values if y != 0))
                    y_val = 0
                    if len(unique_y) >= 2:
                        y_val = (int(unique_y[1]) // 10) * 10 + self.thickness
                    while y_val - height > 0:
                        y_val -= height
                    while y_val < maxwidth:
                        if y_val > self.thickness:
                            tiles.append(y_val) 
                        y_val += height                  
                tiles.sort()
                repeatcount = int((ceilingzstart - width) / width) + 1
                x_or_y = wall_data["x"] if axis == "X" else wall_data["y"]
                dist_needed = 0 - (x_or_y + self.origin_x)
                wall_surface = x_or_y + self.origin_x + dist_needed
                for count, pos in enumerate(tiles):
                    alphabet_string = string.ascii_lowercase
                    alphabet_list = list(alphabet_string)
                    alpha = ""
                    for index, item in enumerate(alphabet_list):
                        if index == (count):
                            alpha = item
                    for i in range(repeatcount):
                        z = width + width * i
                        self.tmptemp.append(
                            {
                                "Wall Number": self.index + 1,
                                "Point Name": f"TMP{self.index + 1}S2{alpha}{i + 1}",
                                "Position X": wall_surface if axis == "X" else int(pos),
                                "Position Y": int(pos) if axis == "X" else wall_surface,
                                "Position Z": z,
                                "Width": maxwidth,
                                "Height": maxheight,
                            }
                        )
                self.index += 1
        self.getTMPFloor()

    def getTMPFloor(self):
        maxheight, maxwidth = 0, 0
        for wallsmax in self.stage2_rows:
            if wallsmax["Wall Number"] == "F":
                maxwidth = wallsmax["Width"]
                maxheight = wallsmax["Height"]
        self.floor_tmps = []
        floorbss20 = [
            obj for obj in self.floor if "floor:bss.80" not in obj["name"].lower()
        ]
        width, height = self.get_width_heights_intervals(floorbss20[0])
        x_val = self.externalxmax_width - height + self.thickness
        tiles_x, tiles_y = [] , []
        tiles_x.append(x_val)
        while x_val - height > 0:
            x_val -= height
            if x_val > self.thickness:
                tiles_x.append(x_val)
        vertices = self.boxup[0]["vertices"]
        y_values = vertices[:, 1]
        unique_y = sorted(set(y for y in y_values if y != 0))
        y_val = 0
        if len(unique_y) >= 2:
            y_val = (int(unique_y[1]) // 10) * 10 + self.thickness
            while y_val - width > 0:
                y_val -= width 
            while y_val < maxheight:
                if y_val > self.thickness:
                    tiles_y.append(y_val) 
                y_val += width
        tiles_x.sort()
        tiles_y.sort()
        count = 0
        for xpos in tiles_x:
            alphabet_string = string.ascii_lowercase
            alphabet_list = list(alphabet_string)
            alpha = ""
            for index, item in enumerate(alphabet_list):
                if index == (count):
                    alpha = item
            counter = 0
            for ypos in tiles_y:
                self.floor_tmps.append(
                    {
                        "Wall Number": "F",
                        "Point Name": f"TMP{self.index + 1}S2{alpha}{counter+1}",
                        "Position X": int(xpos),
                        "Position Y": int(ypos),
                        "Position Z": floorbss20[0]["z"],
                        "Width": maxwidth,
                        "Height": maxheight,
                    }
                )
                counter += 1
            if self.floor_tmps:
                count += 1
        self.returntmp()

    def returntmp(self):
        return self.tmptemp + self.floor_tmps

    def get_width_heights_intervals(self, next_w):
        name = next_w["name"]
        match = re.search(r"(\d+)\s*[xX]\s*(\d+)\s*MM", name, re.IGNORECASE)
        if match:
            width, height = int(match.group(1)), int(match.group(2))
            return width, height
