import string
import pandas as pd
from openpyxl.utils import get_column_letter
import numpy as np
import ifcopenshell
import ifcopenshell.util.element as Element
from ifcopenshell.util.placement import get_local_placement
import math
import re
from collections import defaultdict
import PythonApplication.loadtmp as tmpinserter
import PythonApplication.loadtmpFloor as FloorTMP


class loadTMP2:
    def __init__(
        self,
        data,
        verts_data,
        Cellingstorey,
        thickness,
        wall_height,
        meterline,
        label_map,
        wall_finishes_height,
        small_wall_finishes_height,
        wall_format,
        axis_widths,
        count_minus_y,
        count_plus_y
    ):
        self.data = data
        self.verts_data = verts_data
        self.Cellingstorey = Cellingstorey
        self.Cellingstoreyz = Cellingstorey[2]
        self.thickness = thickness
        self.wall_height = wall_height
        self.meterline = meterline
        self.label_map = label_map
        self.wall_finishes_height = wall_finishes_height
        self.small_wall_finishes_height = small_wall_finishes_height
        self.wall_format = wall_format
        self.axis_widths = axis_widths
        self.count_minus_y = count_minus_y
        self.count_plus_y = count_plus_y
        self.x_min, self.x_max = min(self.axis_widths["x"]), max(self.axis_widths["x"])
        self.y_min, self.y_max = min(self.axis_widths["y"]), max(self.axis_widths["y"])
        if self.count_plus_y == 2:
            self.addTMP4()
        elif self.count_minus_y == 2:
            self.addTMP6()

    def get_tmp_label_from_excel(
        self, name: str, z_ref: int = 225, tolerance: int = 5, default="TMP??"
    ) -> str:
        df = pd.read_excel(
            "PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl"
        )
        df = df[df["Stage 2"].notna()]
        df["Name_clean"] = (
            df["Penetration/Fitting/Reference Point Name"].astype(str).str.strip()
        )
        for _, row in df.iterrows():
            if name.strip() in row["Name_clean"]:
                pin_id = str(row["Pin ID"]).strip()
                if pin_id and pin_id[-1].isdigit():
                    return pin_id[:-1]
                return pin_id
        return default

    def find_first_z_reference(self, z_target=225, tolerance=0):
        for obj in self.verts_data:
            name = obj.get("Point number/name", "")
            pos_z = obj.get("Position Z (mm)", 0)
            vertices = obj.get("verticles", [])
            if len(vertices) > 0:
                z_vals = vertices[:, 2]
                for z in z_vals:
                    if abs(z - z_target) <= tolerance:
                        return int(z)
        return z_target

    def get_wall_alias_from_excel(self, pin_id: str) -> str:
        df = pd.read_excel(
            "PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl"
        )
        df = df[df["Stage 2"].notna()]
        df["Pin ID"] = df["Pin ID"].astype(str)
        df["Pin Base"] = df["Pin ID"].str.extract(r"(TMP\\d+S\\d+[a-z])")
        # Find matching row by full Pin ID
        match = df[df["Pin ID"] == pin_id]
        if not match.empty:
            wall = match.iloc[0]["Wall"]
            return str(wall).strip() if pd.notna(wall) else "Unknown"
        return "Unknown"

    def get_width_heights_intervals(self, row):
        name = str(row["Penetration/Fitting/Reference Point Name"])
        match = re.search(r"\((\d+)[xX](\d+)mm\)", name)
        if match:
            try:
                width, height = int(match.group(1)), int(match.group(2))
                return width, height
            except:
                pass
        return 600, 600  # fallback if parsing fails

    def is_near_wall(self, obj, wall_entry, threshold=300):
        wall_data = wall_entry[1]
        wall_position = None
        for objs in self.verts_data:
            if objs.get("Point number/name", "") == wall_data["name"]:
                wall_position = (objs["Position X (mm)"], objs["Position Y (mm)"])
                break
        ox, oy = obj["Position X (mm)"], obj["Position Y (mm)"]
        wx, wy = wall_position
        distance = math.sqrt((ox - wx) ** 2 + (oy - wy) ** 2)
        return distance < threshold

    def get_interval(self, row):
        name = str(row["Penetration/Fitting/Reference Point Name"])
        match = re.search(r"\\((\\d+)[xX](\\d+)\\)", name)
        if match:
            _, height = match.groups()
            return int(height)
        return 600  # default fallback

    def get_next_tmp_base(self, current_base: str, index_offset: int = 0):
        prefix = current_base[:-1]
        last_letter = current_base[-1].lower()
        next_index = string.ascii_lowercase.index(last_letter) + index_offset
        next_letter = string.ascii_lowercase[next_index]
        return f"{prefix}{next_letter}"

    def addTMP4(self):
        ceiling = int(self.Cellingstoreyz)
        self.zreference = self.find_first_z_reference(225)
        df = pd.read_excel(
            "PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl"
        )
        df = df[df["Stage 2"].notna()]
        df = df[df["Pin ID"].astype(str).str.startswith("TMP4S2")]
        df["Z Interval (mm)"] = df.apply(self.get_interval, axis=1)
        df["Base ID"] = df["Pin ID"].str.extract(r"(TMP4S2[a-z])")
        grouped = df.groupby("Base ID").first().reset_index()
        wall_entry = None
        wallname = ""
        for entry in self.label_map:
            letter, wall, direction, axis, wall_alias = entry
            if letter == "D":
                wall_entry = entry
                wallname = wall["name"]
                break
        matched_obj = next(
            (
                obj
                for obj in self.verts_data
                if wallname in obj.get("Point number/name", "")
            ),
            None,
        )
        verts = matched_obj.get("verticles", [])
        x_values = verts[:, 0]
        x_max = int(np.max(x_values))
        xpos = matched_obj["Position X (mm)"]
        ypos = int(matched_obj["Position Y (mm)"])
        startingypos = ypos - self.wall_finishes_height - x_max
        x_array = [startingypos]
        for i, xpos in enumerate(x_array):
            tmp_base = self.get_next_tmp_base("TMP4S2a", i)
            match = grouped[grouped["Base ID"] == tmp_base]
            interval = int(match["Z Interval (mm)"].values[0])
            z_positions = range(self.zreference, ceiling, interval) 
            for counter, z in enumerate(z_positions, start=1):
                self.data.append(
                    {
                        "Stage": "Stage 2",
                        "Marking type": "Tile",
                        "Point number/name": f"{tmp_base}{counter}",
                        "Position X (mm)": (self.x_max - self.thickness)
                        - ((self.x_max - self.thickness * 2) - self.x_min),
                        "Position Y (mm)": xpos,
                        "Position Z (mm)": z,
                        "Wall Number": wallname,
                        "Shape type": "",
                        "Status": "blank",
                        "Quadrant": 1,
                        "Unnamed : 9": "",
                        "Width": "",
                        "Height": "",
                        "Orientation": "",
                        "Diameter": "",
                    }
                )
                counter += 1
        if self.count_plus_y == 2:
            self.addTMP5()
        else:
            datainseter = tmpinserter.loadTMP(
                self.data,
                self.verts_data,
                self.Cellingstorey,
                self.thickness,
                self.wall_height,
                self.meterline,
                self.label_map,
                self.wall_finishes_height,
                self.small_wall_finishes_height,
                self.wall_format,
                self.axis_widths,
                self.count_minus_y,
                self.count_plus_y
            )
            datainseter.addTMP3()

    def addTMP5(self):
        df = pd.read_excel(
            "PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl"
        )
        df = df[df["Stage 2"].notna()]
        if self.count_plus_y == 2:
            df = df[df["Pin ID"].astype(str).str.startswith("TMP5S2")]
            df["Base ID"] = df["Pin ID"].str.extract(r"(TMP5S2[a-z])")
        else:
            df = df[df["Pin ID"].astype(str).str.startswith("TMP2S2")]
            df["Base ID"] = df["Pin ID"].str.extract(r"(TMP2S2[a-z])")
        for base_id in df["Base ID"].dropna().unique():
            if base_id.endswith("a"):
                self.add_TMP5_by_base(base_id, flat=True)
            else:
                self.add_TMP5_by_base(base_id, flat=False)
        self.addTMP6()

    def add_TMP5_by_base(self, tmp_base: str, flat: bool):
        ceiling = int(self.Cellingstoreyz)
        self.zreference = self.find_first_z_reference(225)
        df = pd.read_excel("PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl")
        df = df[df["Stage 2"].notna()]
        if self.count_plus_y == 2:
            df = df[df["Pin ID"].astype(str).str.startswith("TMP5S2")]
            df["Base ID"] = df["Pin ID"].str.extract(r"(TMP5S2[a-z])")
        else:
            df = df[df["Pin ID"].astype(str).str.startswith("TMP2S2")]
            df["Base ID"] = df["Pin ID"].str.extract(r"(TMP2S2[a-z])")
        grouped = df[df["Base ID"] == tmp_base]
        row = grouped.iloc[0]
        label_name = str(row.get("Penetration/Fitting/Reference Point Name", "")).strip().lower()
        matched_obj = next(
            (obj for obj in self.verts_data if label_name in str(obj.get("Point number/name", "")).lower()),
            None,
        )
        if not matched_obj:
            print(f"[WARN] No matched object for label: {label_name}")
            return
        xpos_offset = matched_obj.get("Position X (mm)", 0)
        verts = matched_obj.get("verticles", [])
        x_values = verts[:, 0]
        filtered_x = x_values[(x_values > 0) & (x_values % 10 == 0)]
        unique_x = np.unique(filtered_x)
        tile_width = unique_x[0] if len(unique_x) > 0 else 450
        trimmed_x = unique_x[:-1] if len(unique_x) >= 2 else unique_x
        third_x = trimmed_x[-1] + tile_width
        extra_x = third_x + (tile_width / 2)
        new_x = np.append(trimmed_x, third_x)
        pin_ids = grouped["Pin ID"].dropna().astype(str)
        marker_numbers = sorted(
            int(re.search(rf"{tmp_base}(\d+)", pid.strip()).group(1))
            for pid in pin_ids if re.search(rf"{tmp_base}(\d+)", pid.strip())
        )
        if flat:
            for x, num in zip(reversed(new_x), marker_numbers[:3]):
                self.data.append({
                    "Stage": "Stage 2",
                    "Marking type": "Tile",
                    "Point number/name": f"{tmp_base}{num}",
                    "Position X (mm)": x + xpos_offset,
                    "Position Y (mm)": self.y_max - self.small_wall_finishes_height - self.wall_height,
                    "Position Z (mm)": self.zreference,
                    "Wall Number": "",
                    "Shape type": "",
                    "Status": "blank",
                    "Quadrant": 1,
                    "Unnamed : 9": "",
                    "Width": "",
                    "Height": "",
                    "Orientation": "",
                    "Diameter": "",
                })
        else:
            interval = self.get_interval(row)
            z_positions = list(range(self.zreference, ceiling, interval))
            for z, num in zip(z_positions, marker_numbers):
                self.data.append({
                    "Stage": "Stage 2",
                    "Marking type": "Tile",
                    "Point number/name": f"{tmp_base}{num}",
                    "Position X (mm)": extra_x + xpos_offset,
                    "Position Y (mm)": self.y_max - self.small_wall_finishes_height - self.wall_height,
                    "Position Z (mm)": z,
                    "Wall Number": "",
                    "Shape type": "",
                    "Status": "blank",
                    "Quadrant": 1,
                    "Unnamed : 9": "",
                    "Width": "",
                    "Height": "",
                    "Orientation": "",
                    "Diameter": "",
                })


    def addTMP6(self):
        ceiling = int(self.Cellingstoreyz)
        self.zreference = self.find_first_z_reference(225)
        df = pd.read_excel(
            "PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl"
        )
        df = df[df["Stage 2"].notna()]
        target_letter = ""
        if self.count_plus_y == 2:
            df = df[df["Pin ID"].astype(str).str.startswith("TMP6S2")]
            df["Z Interval (mm)"] = df.apply(self.get_interval, axis=1)
            df["Base ID"] = df["Pin ID"].str.extract(r"(TMP6S2[a-z])")
            target_letter = "F"
        else:
            df = df[df["Pin ID"].astype(str).str.startswith("TMP2S2")]
            df["Z Interval (mm)"] = df.apply(self.get_interval, axis=1)
            df["Base ID"] = df["Pin ID"].str.extract(r"(TMP2S2[a-z])")
            target_letter = "B"
        grouped = df.groupby("Base ID").first().reset_index()
        wall_entry = None
        wallname = ""
        for entry in self.label_map:
            letter, wall, *_ = entry
            if letter == target_letter:
                wall_entry = entry
                wallname = wall["name"]
                break
        matched_wall_obj = next(
            (
                obj
                for obj in self.verts_data
                if wallname in obj.get("Point number/name", "")
            ),
            None,
        )
        xpos = matched_wall_obj.get("Position X (mm)", 0)
        x_values = (
            matched_wall_obj.get("verticles", [])[:, 0]
            if len(matched_wall_obj.get("verticles", []))
            else []
        )
        x_max = np.max(x_values) - self.wall_height - self.small_wall_finishes_height
        wall_finish_obj = next(
            (
                obj
                for obj in self.verts_data
                if "Wall Finishes" in obj.get("Point number/name", "")
                and self.is_near_wall(obj, wall_entry, threshold=100)
            ),
            None,
        )
        width = self.get_interval(
            {
                "Penetration/Fitting/Reference Point Name": wall_finish_obj[
                    "Point number/name"
                ]
            }
        )
        x_array = [x_max - width, x_max - (width * 2)]
        for i, xpos in enumerate(x_array):
            if self.count_plus_y == 2:
                tmp_base = self.get_next_tmp_base("TMP6S2a", i)
            else:
                tmp_base = self.get_next_tmp_base("TMP2S2a", i)
            match = grouped[grouped["Base ID"] == tmp_base]
            interval = int(match.iloc[0]["Z Interval (mm)"]) if not match.empty else 600
            counter = 1
            for z in range(self.zreference, ceiling, interval):
                self.data.append(
                    {
                        "Stage": "Stage 2",
                        "Marking type": "Tile",
                        "Point number/name": f"{tmp_base}{counter}",
                        "Position X (mm)": self.x_max - self.thickness,
                        "Position Y (mm)": xpos,
                        "Position Z (mm)": z,
                        "Wall Number": wallname,
                        "Shape type": "",
                        "Status": "blank",
                        "Quadrant": 1,
                        "Unnamed : 9": "",
                        "Width": "",
                        "Height": "",
                        "Orientation": "",
                        "Diameter": "",
                    }
                )
                counter += 1
        if self.count_plus_y == 2:
            FloorTMP.loadTMPFloor(
                self.data,
                self.verts_data,
                self.Cellingstorey,
                self.thickness,
                self.wall_height,
                self.meterline,
                self.label_map,
                self.wall_finishes_height,
                self.small_wall_finishes_height,
                self.wall_format,
                self.axis_widths,
            )
        elif self.count_minus_y == 2:
            self.addTMP5()

