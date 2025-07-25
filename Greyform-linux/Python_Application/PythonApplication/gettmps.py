import re
import PythonApplication.methodifcfindings as ifc_findings
import string


class getTMP(object):
    def __init__(
        self,
        all_objs,
        stage2_rows,
        walls,
        stage3_results,
        wall_bss20,
        origin_x,
        origin_y,
        floor,
        centerpoint_rows,
        storeys,
        brep_z_data,
        furnishing_pos,
    ):
        self.all_objs = all_objs
        self.stage2_rows = stage2_rows
        self.walls = walls
        self.stage3_results = stage3_results
        self.centerpoint_rows = centerpoint_rows
        self.wall_bss20 = wall_bss20
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.floor = floor
        self.brep_z_data = brep_z_data
        self.furnishing_pos = furnishing_pos
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
                ceilingzstart = self.storey_min_height
                next_w, _ = ifc_findings.find_closest_wall_rotation(
                    list(wall_dict.values())[0], self.wall_bss20
                )
                width, height = self.get_width_heights_intervals(next_w)
                basin = [
                    obj for obj in self.stage3_results if "basin" in obj["Name"].lower()
                ]
                toilet_seat = [
                    obj for obj in self.all_objs if "toilet_wall" in obj["name"].lower()
                ]
                xtoilet = [
                    toilet_seat[0]["x"] + self.origin_x,
                    toilet_seat[0]["x"]
                    + self.origin_x
                    - (
                        toilet_seat[0]["vertices"][:, 1].max()
                        - toilet_seat[0]["vertices"][:, 1].min()
                    ),
                ]
                ztoilet = [
                    toilet_seat[0]["z"],
                    toilet_seat[0]["z"]
                    - (
                        toilet_seat[0]["vertices"][:, 2].max()
                        - toilet_seat[0]["vertices"][:, 2].min()
                    ),
                ]
                repeatcount = int((ceilingzstart - width) / width) + 1
                doors_tiles = [basin[0]["Position X"] + (height * 2)]
                dist_needed = 0 - (list(wall_dict.values())[0]["y"] + self.origin_y)
                y_wallsurface = (
                    list(wall_dict.values())[0]["y"] + self.origin_y
                ) + dist_needed
                for count, xpos in enumerate(doors_tiles):
                    alphabet_string = string.ascii_lowercase
                    alphabet_list = list(alphabet_string)
                    alpha = ""
                    for index, item in enumerate(alphabet_list):
                        if index == (count):
                            alpha = item
                    counter = 0
                    for i in range(repeatcount):
                        z = width + width * i
                        if (
                            xtoilet[1] <= xpos <= xtoilet[0]
                            and ztoilet[1] <= z <= ztoilet[0]
                        ):
                            continue
                        self.tmptemp.append(
                            {
                                "Wall Number": self.index + 1,
                                "Point Name": f"TMP{self.index + 1}S2{alpha}{counter+1}",
                                "Position X": xpos,
                                "Position Y": y_wallsurface,
                                "Position Z": z,
                            }
                        )
                        counter += 1
        self.index += 1
        self.getTMP2()

    def getTMP2(self):
        for i, wall_dict in enumerate(self.walls):
            if i == self.index:
                ceilingzstart = self.storey_min_height
                next_w, _ = ifc_findings.find_closest_wall_rotation(
                    list(wall_dict.values())[0], self.wall_bss20
                )
                width, height = self.get_width_heights_intervals(next_w)
                floor_drain = [
                    obj
                    for obj in self.all_objs
                    if "bss.floor trap" in obj["name"].lower()
                ]
                floordrainy = min(floor_drain, key=lambda s: s["y"], default={"y": 0})
                floordrain_y = (
                    floordrainy["y"]
                    + self.origin_y
                    + floordrainy["vertices"][:, 1].max()
                )
                fan = [
                    obj for obj in self.all_objs if "dd_wall fan" in obj["name"].lower()
                ]
                fan_y = [
                    fan[0]["y"] + self.origin_y + fan[0]["vertices"][:, 0].max(),
                    fan[0]["y"] + self.origin_y + fan[0]["vertices"][:, 0].min(),
                ]
                fan_z = [fan[0]["z"] + fan[0]["vertices"][:, 2].max(), fan[0]["z"]]
                tiles_repeatcount = (
                    int(
                        (
                            list(wall_dict.values())[0]["vertices"][:, 0].max()
                            - (floordrain_y + width)
                        )
                        / height
                    )
                    + 1
                )
                repeatcount = int((ceilingzstart - width) / width) + 1
                dist_needed = 0 - (list(wall_dict.values())[0]["x"] + self.origin_x)
                x_wallsurface = (
                    list(wall_dict.values())[0]["x"] + self.origin_x
                ) + dist_needed
                tiles = []
                for i in range(tiles_repeatcount):
                    tiles.append((floordrain_y + width) + (height * i))
                for count, ypos in enumerate(tiles):
                    alphabet_string = string.ascii_lowercase
                    alphabet_list = list(alphabet_string)
                    alpha = ""
                    for index, item in enumerate(alphabet_list):
                        if index == (count):
                            alpha = item
                    for i in range(repeatcount):
                        z = width + width * i
                        if fan_y[1] <= ypos <= fan_y[0] and fan_z[1] <= z <= fan_z[0]:
                            continue
                        self.tmptemp.append(
                            {
                                "Wall Number": self.index + 1,
                                "Point Name": f"TMP{self.index + 1}S2{alpha}{i+1}",
                                "Position X": x_wallsurface,
                                "Position Y": ypos,
                                "Position Z": z,
                            }
                        )
        self.index += 1
        self.getTMP3()

    def getTMP3(self):
        for i, wall_dict in enumerate(self.walls):
            if i == self.index:
                ceilingzstart = self.storey_min_height
                wall_data = list(wall_dict.values())[0]
                next_w, _ = ifc_findings.find_closest_wall_rotation(
                    list(wall_dict.values())[0], self.wall_bss20
                )
                width, height = self.get_width_heights_intervals(next_w)
                basin = [obj for obj in self.all_objs if "basin" in obj["name"].lower()]
                tap = [obj for obj in self.all_objs if "tap" in obj["name"].lower()]
                shower_z = [
                    obj for obj in self.brep_z_data if "shower" in obj["name"].lower()
                ]
                repeatcount = int((ceilingzstart - width) / width) + 1
                shower = [
                    obj
                    for obj in self.all_objs
                    if "plumb-shower" in obj["name"].lower()
                ]
                curtain_rail = [
                    obj
                    for obj in self.all_objs
                    if "curtain rail" in obj["name"].lower()
                ]
                curtain_rail_furnishing = [
                    obj
                    for obj in self.furnishing_pos
                    if "curtain rail" in obj["name"].lower()
                ]
                curtain_rail_x = [
                    curtain_rail[0]["x"] + self.origin_x,
                    curtain_rail[0]["x"]
                    + self.origin_x
                    - round(curtain_rail_furnishing[0]["width"]),
                ]
                shower_hand_x = [
                    shower[0]["x"] + self.origin_x,
                    shower[0]["x"]
                    + self.origin_x
                    - (
                        shower[0]["vertices"][:, 0].max()
                        - shower[0]["vertices"][:, 0].min()
                    ),
                ]
                mirror = [
                    obj for obj in self.all_objs if "mirror" in obj["name"].lower()
                ]
                mirror_max_z = mirror[0]["z"] + (
                    mirror[0]["vertices"][:, 2].max()
                    - mirror[0]["vertices"][:, 2].min()
                )
                heightrange = []
                for i in range(repeatcount):
                    z = (width) + width * i
                    heightrange.append(z)
                tiles_repeatcount = (
                    int((wall_data["area"][0] - basin[0]["x"]) / height) + 1
                )
                dist_needed = 0 - (list(wall_dict.values())[0]["y"] + self.origin_y)
                y_wallsurface = (
                    list(wall_dict.values())[0]["y"] + self.origin_y
                ) + dist_needed
                for count, heights in enumerate(heightrange):
                    alphabet_string = string.ascii_lowercase
                    alphabet_list = list(alphabet_string)
                    alpha = ""
                    for index, item in enumerate(alphabet_list):
                        if index == (count):
                            alpha = item
                    counter = 0
                    for j in range(tiles_repeatcount):
                        xpos = basin[0]["x"] + (height * j)
                        if (
                            curtain_rail_x[0] > xpos > curtain_rail_x[1]
                            and heights == curtain_rail[0]["z"]
                        ):
                            continue
                        if (
                            shower_hand_x[0] > xpos > shower_hand_x[1]
                            and shower_z[0]["z_min"] < heights < shower_z[0]["z_max"]
                        ):
                            continue
                        if (
                            xpos == mirror[0]["x"]
                            and tap[0]["z"] < heights < mirror_max_z
                        ):
                            continue
                        self.tmptemp.append(
                            {
                                "Wall Number": self.index + 1,
                                "Point Name": f"TMP{self.index + 1}S2{alpha}{counter+1}",
                                "Position X": xpos,
                                "Position Y": y_wallsurface,
                                "Position Z": heights,
                            }
                        )
                        counter += 1
        self.index += 1
        self.getTMP4()

    def getTMP4(self):
        for i, wall_dict in enumerate(self.walls):
            if i == self.index:
                ceilingzstart = self.storey_min_height
                next_w, _ = ifc_findings.find_closest_wall_rotation(
                    list(wall_dict.values())[0], self.wall_bss20
                )
                width, height = self.get_width_heights_intervals(next_w)
                floor_drain = [
                    obj
                    for obj in self.all_objs
                    if "bss.floor trap" in obj["name"].lower()
                ]
                floordrainy = min(floor_drain, key=lambda s: s["y"], default={"y": 0})
                floordrain_y = (
                    floordrainy["y"]
                    + self.origin_y
                    + floordrainy["vertices"][:, 1].max()
                )
                curtain = [
                    obj for obj in self.all_objs if "curtain" in obj["name"].lower()
                ]
                curtain_y = [
                    obj
                    for obj in self.furnishing_pos
                    if "curtain rail" in obj["name"].lower()
                ]
                toilet_seat = [
                    obj for obj in self.all_objs if "toilet_wall" in obj["name"].lower()
                ]
                ytoilet = [
                    toilet_seat[0]["y"]
                    + self.origin_y
                    + toilet_seat[0]["vertices"][:, 0].max(),
                    toilet_seat[0]["y"]
                    + self.origin_y
                    + toilet_seat[0]["vertices"][:, 0].min(),
                ]
                ztoilet = [
                    toilet_seat[0]["z"],
                    toilet_seat[0]["z"]
                    - (
                        toilet_seat[0]["vertices"][:, 2].max()
                        - toilet_seat[0]["vertices"][:, 2].min()
                    ),
                ]
                curtainmax_y, curtainmin_y = 0, 0
                curtain_z = 0
                for c in curtain:
                    if curtain_y[0]["name"].lower() in c["name"].lower():
                        curtainmax_y = c["y"] + curtain_y[0]["furnishing_y_pos"]
                        curtain_z = c["z"]
                    else:
                        curtainmin_y = c["y"]
                tiles_repeatcount = (
                    int(
                        (
                            list(wall_dict.values())[0]["vertices"][:, 0].max()
                            - (floordrain_y + width)
                        )
                        / height
                    )
                    + 1
                )
                repeatcount = int((ceilingzstart - width) / width) + 1
                dist_needed = 0 - (list(wall_dict.values())[0]["x"] + self.origin_x)
                x_wallsurface = (
                    list(wall_dict.values())[0]["x"] + self.origin_x
                ) + dist_needed
                tiles = []
                for i in range(tiles_repeatcount):
                    tiles.append((floordrain_y + width) + (height * i))
                for count, ypos in enumerate(tiles):
                    alphabet_string = string.ascii_lowercase
                    alphabet_list = list(alphabet_string)
                    alpha = ""
                    for index, item in enumerate(alphabet_list):
                        if index == (count):
                            alpha = item
                    counter = 0
                    for i in range(repeatcount):
                        z = width + width * i
                        if curtainmin_y < ypos < curtainmax_y and z <= curtain_z:
                            continue
                        if ytoilet[1] <= ypos <= ytoilet[0] and ztoilet[1] <= z <= ztoilet[0]:
                            continue
                        self.tmptemp.append(
                            {
                                "Wall Number": self.index + 1,
                                "Point Name": f"TMP{self.index + 1}S2{alpha}{counter+1}",
                                "Position X": x_wallsurface,
                                "Position Y": ypos,
                                "Position Z": z,
                            }
                        )
                        counter += 1
        self.index += 1
        self.getTMPFloor()

    def getTMPFloor(self):
        self.floor_tmps = []
        floorbss20 = [
            obj for obj in self.floor if "floor:bss.80" not in obj["name"].lower()
        ]
        width, height = self.get_width_heights_intervals(floorbss20[0])
        floor_drain = [
            obj for obj in self.all_objs if "bss.floor trap" in obj["name"].lower()
        ]
        floordrainy = min(floor_drain, key=lambda s: s["y"], default={"y": 0})
        floordrain_y = (
            floordrainy["y"] + self.origin_y + floordrainy["vertices"][:, 1].max()
        )
        tiles_repeatcount_y = int((floorbss20[0]["area"][1] - floordrain_y) / width) + 1
        tiles = []
        toilet_seat = [
            obj for obj in self.all_objs if "toilet_wall" in obj["name"].lower()
        ]
        xtoilet = [
            toilet_seat[0]["x"] + self.origin_x,
            toilet_seat[0]["x"]
            + self.origin_x
            - (
                toilet_seat[0]["vertices"][:, 1].max()
                - toilet_seat[0]["vertices"][:, 1].min()
            ),
        ]
        ytoilet = [
            toilet_seat[0]["y"]
            + self.origin_y
            + toilet_seat[0]["vertices"][:, 0].max(),
            toilet_seat[0]["y"]
            + self.origin_y
            + toilet_seat[0]["vertices"][:, 0].min(),
        ]
        for i in range(tiles_repeatcount_y):
            tiles.append(floordrain_y + (width * i))
        basin = [obj for obj in self.all_objs if "basin" in obj["name"].lower()]
        bin = [obj for obj in self.all_objs if "bin_linen" in obj["name"].lower()]
        biny = [
            bin[0]["y"] + self.origin_y + bin[0]["vertices"][:, 1].min(),
            bin[0]["y"] + self.origin_y + bin[0]["vertices"][:, 1].max(),
        ]
        binx = [
            bin[0]["x"] + self.origin_x + bin[0]["vertices"][:, 0].min(),
            bin[0]["x"] + self.origin_x + bin[0]["vertices"][:, 0].max(),
        ]
        tiles_repeatcount_x = (
            int((floorbss20[0]["area"][0] - basin[0]["x"]) / height) + 1
        )
        curtain = [
            obj for obj in self.all_objs if "curtain rail" in obj["name"].lower()
        ]
        curtain_furnishing = [
            obj for obj in self.furnishing_pos if "curtain rail" in obj["name"].lower()
        ]
        curtain_rail_x = [
            curtain[0]["x"] + self.origin_x,
            curtain[0]["x"] + self.origin_x - round(curtain_furnishing[0]["width"]),
        ]
        curtain_rail_y = [
            curtain[0]["y"] + self.origin_y,
            curtain[0]["y"] + self.origin_y + round(curtain_furnishing[0]["height"]),
        ]
        count = 0
        for ypos in tiles:
            alphabet_string = string.ascii_lowercase
            alphabet_list = list(alphabet_string)
            alpha = ""
            for index, item in enumerate(alphabet_list):
                if index == (count):
                    alpha = item
            counter = 0
            for i in range(tiles_repeatcount_x):
                x_pos = basin[0]["x"] + height * i
                if binx[0] < x_pos < binx[1] and biny[0] < ypos < biny[1]:
                    continue
                if (
                    curtain_rail_x[1] < x_pos < curtain_rail_x[0]
                    and curtain_rail_y[0] < ypos < curtain_rail_y[1]
                ):
                    continue
                if (
                    x_pos == basin[0]["x"]
                    and ypos
                    < basin[0]["y"] + self.origin_y + basin[0]["vertices"][:, 1].max()
                ):
                    continue
                if ytoilet[0] < ypos < ytoilet[1] and xtoilet[1] <= x_pos <= xtoilet[0]:
                    continue
                self.floor_tmps.append(
                    {
                        "Wall Number": "F",
                        "Point Name": f"TMP{self.index + 1}S2{alpha}{counter+1}",
                        "Position X": x_pos,
                        "Position Y": ypos,
                        "Position Z": floorbss20[0]["z"],
                    }
                )
                counter += 1
            if self.floor_tmps:
                count += 1
        return self.tmptemp + self.floor_tmps, self.dist_neededarray

    def get_width_heights_intervals(self, next_w):
        name = next_w["name"]
        match = re.search(r"(\d+)\s*[xX]\s*(\d+)\s*MM", name, re.IGNORECASE)
        if match:
            width, height = int(match.group(1)), int(match.group(2))
            return width, height
