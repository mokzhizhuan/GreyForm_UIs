import re
import PythonApplication.methodifcfindings as ifc_findings
import string
import numpy as np


class loadmainTMP:
    def __init__(
        self,
        all_objs,
        dooropening,
        stage2_rows,
        df,
        walls,
        stage3_results,
        wall_bss20,
        wall_bss12,
        origin_x,
        origin_y,
        floor,
        storeys,
        centerpoint_rows,
    ):
        self.all_objs = all_objs
        self.dooropening = dooropening
        self.stage2_rows = stage2_rows
        self.df = df
        self.walls = walls
        self.stage3_results = stage3_results
        self.wall_bss20 = wall_bss20
        self.height20 = self.wall_bss20[0]["area"][1]
        self.wall_bss12 = wall_bss12
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.floor = floor
        self.centerpoint_rows = centerpoint_rows
        x_widths = [
            w["centerpointwidth"]
            for w in self.centerpoint_rows
            if w.get("AxisDirection", "").upper().endswith("X") and w.get("Wall Number") != "F"
        ]
        y_widths = [
            w["centerpointwidth"]
            for w in self.centerpoint_rows
            if w.get("AxisDirection", "").upper().endswith("Y") and w.get("Wall Number") != "F"
        ]
        self.x_internal_width = (sum(x_widths) // len(x_widths) if x_widths else 0) * 2
        self.y_internal_width = (sum(y_widths) // len(y_widths) if y_widths else 0) * 2
        self.x_longest_surface_width, self.y_longest_surface_width = (
            self.getlongerwidthsurface()
        )
        self.storey_min_height = min(
            storeys, key=lambda s: s["elevation"], default={"elevation": 0}
        )["elevation"]
        self.dist_neededarray = []
        self.index = 0
        self.tmptemp = []
        self.addTMP1()

    def getlongerwidthsurface(self):
        x_widths = []
        y_widths = []
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
        name = next_w["name"]
        match = re.search(r"\((\d+)[xX](\d+)mm\)", name)
        if match:
            width, height = int(match.group(1)), int(match.group(2))
            return width, height

    def addTMP1(self):
        for i, wall_dict in enumerate(self.walls):
            if i == self.index:
                first_w, _ = ifc_findings.find_closest_wall(
                    list(wall_dict.values())[0], self.wall_bss20
                )
                second_w, _ = ifc_findings.find_closest_wall(first_w, self.wall_bss20)
                width, height = self.get_width_heights_intervals(first_w)
                geeshi = [
                    obj for obj in self.all_objs if "gessi.sh" in obj["name"].lower()
                ]
                flushplate = [
                    obj for obj in self.all_objs if "flush plate" in obj["name"].lower()
                ]
                first_w_x = first_w["x"]
                second_w_x = second_w["x"]
                geeshi_x = geeshi[0]["x"]
                flushplate_x = flushplate[0]["x"]
                tiles = [geeshi_x, first_w_x, second_w_x, flushplate_x]
                repeatcount = (
                    int(
                        (self.storey_min_height - (self.wall_bss12[0]["z"] - height))
                        / height
                    )
                    + 1
                )
                dist_needed = 0 - list(wall_dict.values())[0]["y"]
                y_wallsurface = list(wall_dict.values())[0]["y"] + dist_needed
                self.dist_neededarray.append(
                    {
                        "Wall Number": self.index + 1,
                        "Distance": dist_needed,
                        "Axis": list(wall_dict.values())[0]["axis"],
                        "Max_Width": list(wall_dict.values())[0]["area"][0]
                        + (list(wall_dict.values())[0]["area"][1] * 2),
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
                        z = (self.wall_bss12[0]["z"] - height) + height * i
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
        self.addTMP2()

    def addTMP2(self):
        for i, wall_dict in enumerate(self.walls):
            if i == self.index:
                next_w, _ = ifc_findings.find_closest_wall(
                    list(wall_dict.values())[0], self.wall_bss20
                )
                width, height = self.get_width_heights_intervals(next_w)
                verts = next_w["vertices"]
                x_values = verts[:, 0]
                z_values = verts[:, 2]
                non_zero_x = x_values[x_values > 0]
                lowest_x = int(np.min(non_zero_x)) if non_zero_x.size else 0
                highest_x = int(np.max(non_zero_x)) if non_zero_x.size else 0
                tiles = [
                    (highest_x - next_w["area"][1] - lowest_x - width),
                    (highest_x - next_w["area"][1] - lowest_x),
                ]
                repeatcount = (
                    int(
                        (self.storey_min_height - (self.wall_bss12[0]["z"] - height))
                        / height
                    )
                    + 1
                )
                dist_needed = 0 - list(wall_dict.values())[0]["x"]
                x_wallsurface = list(wall_dict.values())[0]["x"] + dist_needed
                self.dist_neededarray.append(
                    {
                        "Wall Number": self.index + 1,
                        "Distance": dist_needed,
                        "Axis": list(wall_dict.values())[0]["axis"],
                        "Max_Width": list(wall_dict.values())[0]["area"][0]
                        + list(wall_dict.values())[0]["area"][1],
                    }
                )
                for count, ypos in enumerate(tiles):
                    alphabet_string = string.ascii_lowercase
                    alphabet_list = list(alphabet_string)
                    alpha = ""
                    for index, item in enumerate(alphabet_list):
                        if index == (count):
                            alpha = item
                    for i in range(repeatcount):
                        z = (self.wall_bss12[0]["z"] - height) + height * i
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
        self.addTMP3()

    def addTMP3(self):
        for i, wall_dict in enumerate(self.walls):
            if i == self.index:
                next_w, _ = ifc_findings.find_closest_wall(
                    list(wall_dict.values())[0], self.wall_bss20
                )
                width, height = self.get_width_heights_intervals(next_w)
                geeshi = [
                    obj for obj in self.all_objs if "gessi.sh" in obj["name"].lower()
                ]
                tiles = [geeshi[0]["x"]]
                repeatcount = (
                    int(
                        (self.storey_min_height - (self.wall_bss12[0]["z"] - height))
                        / height
                    )
                    + 1
                )
                dist_needed = 0 - list(wall_dict.values())[0]["y"]
                longest_width = self.y_internal_width + (
                    (list(wall_dict.values())[0]["area"][1] + self.height20) * 2
                )
                y_wallsurface = -abs(longest_width - self.y_longest_surface_width)
                self.dist_neededarray.append(
                    {
                        "Wall Number": self.index + 1,
                        "Distance": dist_needed,
                        "Axis": list(wall_dict.values())[0]["axis"],
                        "Max_Width": list(wall_dict.values())[0]["area"][0],
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
                        z = (self.wall_bss12[0]["z"] - height) + height * i
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
        self.addTMP4()

    def addTMP4(self):
        for i, wall_dict in enumerate(self.walls):
            if i == self.index:
                next_w, _ = ifc_findings.find_closest_wall(
                    list(wall_dict.values())[0], self.wall_bss20
                )
                width, height = self.get_width_heights_intervals(next_w)
                tiles = [next_w["y"] - next_w["area"][0]]
                repeatcount = (
                    int(
                        (self.storey_min_height - (self.wall_bss12[0]["z"] - height))
                        / height
                    )
                    + 1
                )
                dist_needed = 0 - list(wall_dict.values())[0]["x"]
                longest_width = self.x_internal_width + (
                    (list(wall_dict.values())[0]["area"][1] + self.height20) * 2
                )
                x_wallsurface = -abs(longest_width - self.x_longest_surface_width)
                self.dist_neededarray.append(
                    {
                        "Wall Number": self.index + 1,
                        "Distance": dist_needed,
                        "Axis": list(wall_dict.values())[0]["axis"],
                        "Max_Width": list(wall_dict.values())[0]["area"][0]
                        + list(wall_dict.values())[0]["area"][1],
                    }
                )
                for count, ypos in enumerate(tiles):
                    alphabet_string = string.ascii_lowercase
                    alphabet_list = list(alphabet_string)
                    alpha = ""
                    for index, item in enumerate(alphabet_list):
                        if index == (count):
                            alpha = item
                    for i in range(repeatcount):
                        z = (self.wall_bss12[0]["z"] - height) + height * i
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
        self.addTMP5()

    def addTMP5(self):
        for i, wall_dict in enumerate(self.walls):
            if i == self.index:
                next_w, _ = ifc_findings.find_closest_wall(
                    list(wall_dict.values())[0], self.wall_bss20
                )
                width, height = self.get_width_heights_intervals(next_w)
                flushplate = [
                    obj for obj in self.all_objs if "flush plate" in obj["name"].lower()
                ]
                flushplate_x = flushplate[0]["x"]
                repeatcount = (
                    int((list(wall_dict.values())[0]["x"] - flushplate_x) / width) + 1
                )
                dist_needed = 0 - (list(wall_dict.values())[0]["y"])
                y_wallsurface = (list(wall_dict.values())[0]["y"]) + dist_needed
                self.dist_neededarray.append(
                    {
                        "Wall Number": self.index + 1,
                        "Distance": dist_needed,
                        "Axis": list(wall_dict.values())[0]["axis"],
                        "Max_Width": list(wall_dict.values())[0]["area"][0]
                        + list(wall_dict.values())[0]["area"][1],
                    }
                )
                for i in range(repeatcount):
                    x = flushplate_x + width * i
                    self.tmptemp.append(
                        {
                            "Wall Number": self.index + 1,
                            "Point Name": f"TMP{self.index + 1}S2a{i+1}",
                            "Position X": x,
                            "Position Y": y_wallsurface,
                            "Position Z": self.wall_bss12[0]["z"] - height,
                        }
                    )
        self.index += 1
        self.addTMP6()

    def addTMP6(self):
        for i, wall_dict in enumerate(self.walls):
            if i == self.index:
                next_w, _ = ifc_findings.find_closest_wall(
                    list(wall_dict.values())[0], self.wall_bss20
                )
                width, height = self.get_width_heights_intervals(next_w)
                tiles = [
                    (next_w["y"] + next_w["area"][1] + width),
                    (next_w["y"] + next_w["area"][1] + (width * 2)),
                ]
                repeatcount = (
                    int(
                        (self.storey_min_height - (self.wall_bss12[0]["z"] - height))
                        / height
                    )
                    + 1
                )
                dist_needed = 0 - list(wall_dict.values())[0]["x"]
                x_wallsurface = list(wall_dict.values())[0]["x"] + dist_needed
                self.dist_neededarray.append(
                    {
                        "Wall Number": self.index + 1,
                        "Distance": dist_needed,
                        "Axis": list(wall_dict.values())[0]["axis"],
                        "Max_Width": list(wall_dict.values())[0]["area"][0],
                    }
                )
                for count, ypos in enumerate(tiles):
                    alphabet_string = string.ascii_lowercase
                    alphabet_list = list(alphabet_string)
                    alpha = ""
                    for index, item in enumerate(alphabet_list):
                        if index == (count):
                            alpha = item
                    for i in range(repeatcount):
                        z = (self.wall_bss12[0]["z"] - height) + height * i
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
        floor_area = {}
        for floor in floor_finishes:
            width, height = self.get_width_heights_intervals(floor)
            floor_area[floor["name"]] = {"Width": width, "Height": height}
        flushplate = [
            obj for obj in self.all_objs if "flush plate" in obj["name"].lower()
        ]
        drain = [obj for obj in self.all_objs if "drain_150" in obj["name"].lower()]
        floor600, _ = ifc_findings.find_closest_wall(flushplate[0], floor_finishes)
        floor150, _ = ifc_findings.find_closest_wall(drain[0], floor_finishes)
        counter = 0
        for floor in floor_finishes:
            if floor["name"] == floor150["name"]:
                area_info = floor_area[floor150["name"]]
                floortiles = [
                    floor150["x"] - (area_info["Width"] / 2),
                    floor150["x"] + (area_info["Width"] / 2),
                ]
                repeatcount = int(
                    (floor["vertices"][:, 1].max() - floor["vertices"][:, 1].min())
                    / area_info["Height"]
                )
                for count, xpos in enumerate(floortiles):
                    alphabet_string = string.ascii_lowercase
                    alphabet_list = list(alphabet_string)
                    alpha = ""
                    for index, item in enumerate(alphabet_list):
                        if index == (count):
                            alpha = item
                    for i in range(repeatcount):
                        ypos = floor["vertices"][:, 1].min() + area_info["Height"] * (
                            i + 1
                        )
                        self.tmptemp.append(
                            {
                                "Wall Number": self.index + 1,
                                "Point Name": f"TMP{self.index + 1}S2{alpha}{i+1}",
                                "Position X": xpos,
                                "Position Y": ypos,
                                "Position Z": floor["z"] - 1000,
                            }
                        )
                    counter += 1
            else:
                area_info = floor_area[floor600["name"]]
                max_width_repeat_count = (
                    int(
                        (floor["vertices"][:, 0].max() - flushplate[0]["x"])
                        / area_info["Width"]
                    )
                    + 1
                )
                repeatcount = int(
                    (floor["vertices"][:, 1].max() - floor["vertices"][:, 1].min())
                    / area_info["Height"]
                )
                floor90 = [
                    obj for obj in self.floor if "floor:bss.90" in obj["name"].lower()
                ]
                for count in range(max_width_repeat_count):
                    alphabet_string = string.ascii_lowercase
                    alphabet_list = list(alphabet_string)
                    alpha = ""
                    xpos = flushplate[0]["x"] + (area_info["Width"] * count)
                    for index, item in enumerate(alphabet_list):
                        if index == (count + counter):
                            alpha = item
                    for i in range(repeatcount):
                        ypos = floor90[0]["y"] + area_info["Height"] * i
                        self.tmptemp.append(
                            {
                                "Wall Number": self.index + 1,
                                "Point Name": f"TMP{self.index + 1}S2{alpha}{i+1}",
                                "Position X": xpos,
                                "Position Y": ypos,
                                "Position Z": floor["z"] - 1000,
                            }
                        )
                    counter += 1
        return self.tmptemp, self.dist_neededarray

    def log(self, message):
        with open("log.txt", "a") as log_file:
            log_file.write(message + "\n")
