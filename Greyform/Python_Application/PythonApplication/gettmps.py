import re
import PythonApplication.methodifcfindings as ifc_findings
import string


class getTMP(object):
    def __init__(
        self,
        all_objs,
        stage2_rows,
        df,
        walls,
        stage3_results,
        wall_bss20,
        origin_x,
        origin_y,
        floor,
        centerpoint_rows
    ):
        self.all_objs = all_objs
        self.stage2_rows = stage2_rows
        self.df = df
        self.walls = walls
        self.stage3_results = stage3_results
        self.centerpoint_rows = centerpoint_rows
        self.wall_bss20 = wall_bss20
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.floor = floor
        self.index = 0
        self.tmptemp = []
        self.dist_neededarray = []
        self.maxwidths = []
        self.getTMP1()

    def getTMP1(self):
        for i, wall_dict in enumerate(self.walls):
            if i == self.index:
                ceilingzstart = (
                    list(wall_dict.values())[0]["vertices"][:, 2].max()
                    + list(wall_dict.values())[0]["z"]
                )
                next_w, _ = ifc_findings.find_closest_wall(
                    list(wall_dict.values())[0], self.wall_bss20
                )
                width, height = self.get_width_heights_intervals(next_w)
                wc_paper_holder = [
                    obj
                    for obj in self.all_objs
                    if "paper holder" in obj["name"].lower()
                ]
                if wc_paper_holder:
                    wc_paper_holder_y = wc_paper_holder[0]["y"] + self.origin_y
                    wc_paper_holder_z = wc_paper_holder[0]["z"]
                repeatcount = int((ceilingzstart - wc_paper_holder_z) / width)
                wc_paper_holder_tiles = [
                    wc_paper_holder_y - width / 2,
                    wc_paper_holder_y + width / 2,
                ]
                dist_needed = 0 - (list(wall_dict.values())[0]["x"] + self.origin_x)
                x_wallsurface = (list(wall_dict.values())[0]["x"] + self.origin_x) + dist_needed
                self.dist_neededarray.append(
                    {
                        "Wall Number" : self.index + 1,
                        "Distance" : dist_needed ,
                        "Axis": list(wall_dict.values())[0]["axis"],
                        "Max_Width" : list(wall_dict.values())[0]["area"][0] + (list(wall_dict.values())[0]["area"][1]*2)
                    }
                )
                for count, ypos in enumerate(wc_paper_holder_tiles):
                    alphabet_string = string.ascii_lowercase
                    alphabet_list = list(alphabet_string)
                    alpha = ""
                    for index, item in enumerate(alphabet_list):
                        if index == (count):
                            alpha = item
                    for i in range(repeatcount):
                        z = (ceilingzstart - width) - width * i
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
        self.getTMP2()

    def getTMP2(self):
        for i, wall_dict in enumerate(self.walls):
            if i == self.index:
                ceilingzstart = (
                    list(wall_dict.values())[0]["vertices"][:, 2].max()
                    + list(wall_dict.values())[0]["z"]
                )
                next_w, _ = ifc_findings.find_closest_wall(
                    list(wall_dict.values())[0], self.wall_bss20
                )
                width, height = self.get_width_heights_intervals(next_w)
                wc = [
                    obj
                    for obj in self.stage3_results
                    if self.index + 1 == obj["Wall Number"]
                ]
                wc_name = wc[0]["Name"]
                wc_obj = [obj for obj in self.all_objs if wc_name == obj["name"]]
                wc_tiles = [
                    wc[0]["Position X"] - width / 2,
                    wc[0]["Position X"] + width / 2,
                ]
                wczheight = wc_obj[0]["z"] + wc_obj[0]["vertices"][:, 2].max()
                repeatcount = int((ceilingzstart - wczheight) / width)
                dist_needed = 0 - (list(wall_dict.values())[0]["y"] + self.origin_y)
                y_wallsurface = (list(wall_dict.values())[0]["y"] + self.origin_y) + dist_needed
                self.dist_neededarray.append(
                    {
                        "Wall Number" : self.index + 1,
                        "Distance" : dist_needed ,
                        "Axis": list(wall_dict.values())[0]["axis"],
                        "Max_Width" : list(wall_dict.values())[0]["area"][0]
                    }
                )
                for count, xpos in enumerate(wc_tiles):
                    alphabet_string = string.ascii_lowercase
                    alphabet_list = list(alphabet_string)
                    alpha = ""
                    for index, item in enumerate(alphabet_list):
                        if index == (count):
                            alpha = item
                    for i in range(repeatcount):
                        z = (ceilingzstart - width) - width * i
                        self.tmptemp.append(
                            {
                                "Wall Number": self.index + 1,
                                "Point Name": f"TMP{self.index + 1}S2{alpha}{i+1}",
                                "Position X": xpos,
                                "Position Y": y_wallsurface,
                                "Position Z": z,
                            }
                        )
        self.index += 1
        self.getTMP3()

    def getTMP3(self):
        for i, wall_dict in enumerate(self.walls):
            if i == self.index:
                ceilingzstart = (
                    list(wall_dict.values())[0]["vertices"][:, 2].max()
                    + list(wall_dict.values())[0]["z"]
                )
                wall_data = list(wall_dict.values())[0]
                wx = wall_data["x"]
                next_w = []
                min_dist = float("inf")
                dist = 0
                for wallbss20 in self.wall_bss20:
                    if wall_data["axis"] == "Y" and wallbss20["axis"] == "Y":
                        dist = abs(
                            (wx + self.origin_x) - (wallbss20["x"] + self.origin_x)
                        )
                    else:
                        continue
                    if dist < min_dist:
                        min_dist = dist
                        next_w = wallbss20
                width, height = self.get_width_heights_intervals(next_w)
                washdown_wc = [
                    obj for obj in self.all_objs if "washdown wc" in obj["name"].lower()
                ]
                fitting = [
                    obj
                    for obj in self.stage3_results
                    if self.index + 1 == obj["Wall Number"]
                ]
                wczheight = washdown_wc[0]["z"] + washdown_wc[0]["vertices"][:, 2].max()
                mirror = [
                    obj for obj in self.all_objs if "mirror" in obj["name"].lower()
                ]
                shower_hose = [
                    obj for obj in self.all_objs if "shower hose" in obj["name"].lower()
                ]
                mirror_y = mirror[0]["y"] + self.origin_y
                shower_hose_y = shower_hose[0]["y"] + self.origin_y
                min_y = min(obj["Position Y"] for obj in fitting)
                repeatcount = int((ceilingzstart - wczheight) / width)
                heightrange = []
                for i in range(repeatcount):
                    z = (ceilingzstart - width) - width * i
                    heightrange.append(z)
                max_width = next_w["y"] + self.origin_y + next_w["vertices"][:, 0].max()
                max_width_repeat_count = int((max_width - min_y) / width) + 1
                dist_needed = 0 - (list(wall_dict.values())[0]["x"] + self.origin_x)
                x_wallsurface = (list(wall_dict.values())[0]["x"] + self.origin_x) + dist_needed
                self.dist_neededarray.append(
                    {
                        "Wall Number" : self.index + 1,
                        "Distance" : dist_needed ,
                        "Axis": list(wall_dict.values())[0]["axis"],
                        "Max_Width" : list(wall_dict.values())[0]["area"][0] + list(wall_dict.values())[0]["area"][1]
                    }
                )
                for j, height in enumerate(heightrange):
                    alphabet_string = string.ascii_lowercase
                    alphabet_list = list(alphabet_string)
                    alpha = ""
                    for index, item in enumerate(alphabet_list):
                        if index == (j):
                            alpha = item
                    counter = 0
                    for i in range(max_width_repeat_count):
                        ypos = min_y + i * width
                        if mirror_y == ypos or shower_hose_y == ypos:
                            if (
                                mirror[0]["z"] + mirror[0]["vertices"][:, 2].max()
                                > height
                            ):
                                continue
                            elif (
                                shower_hose[0]["z"]
                                + shower_hose[0]["vertices"][:, 2].max()
                                > height
                            ):
                                continue
                        self.tmptemp.append(
                            {
                                "Wall Number": self.index + 1,
                                "Point Name": f"TMP{self.index + 1}S2{alpha}{counter+1}",
                                "Position X": x_wallsurface,
                                "Position Y": ypos,
                                "Position Z": height,
                            }
                        )
                        counter += 1
        self.index += 1
        self.getTMP4()

    def getTMP4(self):
        for i, wall_dict in enumerate(self.walls):
            if i == self.index:
                ceilingzstart = (
                    list(wall_dict.values())[0]["vertices"][:, 2].max()
                    + list(wall_dict.values())[0]["z"]
                )
                next_w, _ = ifc_findings.find_closest_wall(
                    list(wall_dict.values())[0], self.wall_bss20
                )
                width, height = self.get_width_heights_intervals(next_w)
                wc_basin = [
                    obj
                    for obj in self.all_objs
                    if "wc square basin" in obj["name"].lower()
                ]
                wc_basin_x = (
                    wc_basin[0]["x"]
                    + self.origin_x
                    + wc_basin[0]["vertices"][:, 0].max()
                )
                repeatcount = int((ceilingzstart) / width)
                tiles = [wc_basin_x, wc_basin_x + width]
                dist_needed = 0 - (list(wall_dict.values())[0]["y"] + self.origin_y)
                y_wallsurface = (list(wall_dict.values())[0]["y"] + self.origin_y) + dist_needed
                self.dist_neededarray.append(
                    {
                        "Wall Number" : self.index + 1,
                        "Distance" : dist_needed ,
                        "Axis": list(wall_dict.values())[0]["axis"],
                        "Max_Width" : list(wall_dict.values())[0]["area"][0] + list(wall_dict.values())[0]["area"][1]
                    }
                )
                for count, xpos in enumerate(tiles):
                    alphabet_string = string.ascii_lowercase
                    alphabet_list = list(alphabet_string)
                    alpha = ""
                    for index, item in enumerate(alphabet_list):
                        if index == (count):
                            alpha = item
                    for i in range(repeatcount):
                        z = (ceilingzstart - width) - width * i
                        self.tmptemp.append(
                            {
                                "Wall Number": self.index + 1,
                                "Point Name": f"TMP{self.index + 1}S2{alpha}{i+1}",
                                "Position X": xpos,
                                "Position Y": y_wallsurface,
                                "Position Z": z,
                            }
                        )
        self.index += 1
        self.getTMPFloor()

    def getTMPFloor(self):
        floormarker = [
            obj for obj in self.floor if "bss.70" in obj["name"].lower()
        ]
        floorbss20 = [
            obj for obj in self.floor if "bss.20" in obj["name"].lower()
        ]
        lowest_floor = max(f["z"] for f in self.floor) if self.floor else 0
        width, height = self.get_width_heights_intervals(floorbss20[0])
        floormarkermax_y = floormarker[0]["y"] + self.origin_y
        floormarkermax_x = floormarker[0]["x"] + self.origin_x + width/2
        wc_basin = [
                    obj
                    for obj in self.all_objs
                    if "wc square basin" in obj["name"].lower()
                ]
        wc_basin_y = wc_basin[0]["y"]+ self.origin_y
        repeatcount = int((floormarkermax_y-wc_basin_y) / width) + 1
        for i in range(repeatcount):
            ypos = wc_basin_y + width*i
            self.tmptemp.append(
                {
                    "Wall Number": "F",
                    "Point Name": f"TMP{self.index + 1}S2a{i+1}",
                    "Position X": floormarkermax_x,
                    "Position Y": ypos,
                    "Position Z": lowest_floor-1000,
                }
            )
        return self.tmptemp , self.dist_neededarray

    def get_width_heights_intervals(self, next_w):
        name = next_w["name"]
        match = re.search(r"\((\d+)[xX](\d+)mm\)", name)
        if match:
            width, height = int(match.group(1)), int(match.group(2))
            return width, height
