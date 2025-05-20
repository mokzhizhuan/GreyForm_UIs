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


class loadTMPFloor:
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
        flooroffset,
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
        self.floor_offset = flooroffset
        self.axis_widths = axis_widths
        self.x_min, self.x_max = min(self.axis_widths["x"]), max(self.axis_widths["x"])
        self.y_min, self.y_max = min(self.axis_widths["y"]), max(self.axis_widths["y"])
        self.addTMP7()

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

    def addTMP7(self):
        df = pd.read_excel(
            "PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl"
        )
        df = df[df["Stage 2"].notna()]
        df = df[df["Pin ID"].astype(str).str.startswith("TMP7S2")]
        base_groups = defaultdict(list)
        for pid in df["Pin ID"].dropna().astype(str):
            match = re.fullmatch(r"TMP7S2([a-z])(\d+)", pid)
            if match:
                letter, number = match.groups()
                base = f"TMP7S2{letter}"
                base_groups[base].append(int(number))
        ref_names = (
            df["Penetration/Fitting/Reference Point Name"].dropna().astype(str).unique()
        )
        target_name_keyword150 = next(
            (n for n in ref_names if "150mm" in n.lower() and "floor" in n.lower()),
            None,
        )
        target_name_keyword600 = next(
            (n for n in ref_names if "600mm" in n.lower() and "floor" in n.lower()),
            None,
        )
        tece_label = next((n for n in ref_names if "tece" in n.lower()), None)
        drain_label = next((n for n in ref_names if "drain" in n.lower()), None)
        found_tece = found_floor150 = found_floor = found_drain = False
        unique_y = []
        width = width150 = height150 = max_z_floor_150 = 0
        max_z_floor_600 = min_z_floor_600 = 0
        for obj in self.verts_data:
            name = obj.get("Point number/name", "")
            prefinedType = obj.get("PredefinedType", "")
            level = obj.get("Level", "")
            if tece_label and tece_label in name:
                xpostece = obj["Position X (mm)"]
                found_tece = True
            if (
                "floor" in name.lower()
                and "floor" in prefinedType.lower()
                and "bedroom" in level.lower()
            ):
                vertices = np.array(obj.get("verticles", []))
                if target_name_keyword150 and target_name_keyword150 in name:
                    y_values = vertices[:, 1]
                    z_values = vertices[:, 2]
                    unique_z = np.unique(z_values.astype(int))
                    max_z_floor_150 = max(unique_z)
                    rounded_y = np.ceil(y_values / 10) * 10
                    unique_y = np.unique(rounded_y.astype(int))
                    match = re.search(r"\((\d+)[xX](\d+)mm\)", name)
                    if match:
                        width150 = int(match.group(1))
                        height150 = int(match.group(2))
                    found_floor150 = True
                if target_name_keyword600 and target_name_keyword600 in name:
                    match = re.search(r"\((\d+)[xX](\d+)mm\)", name)
                    z_values = vertices[:, 2]
                    unique_z = np.unique(z_values.astype(int))
                    max_z_floor_600 = max(unique_z)
                    min_z_floor_600 = min(unique_z)
                    if match:
                        width = int(match.group(1))
                    found_floor = True
            if drain_label and drain_label in name:
                xposdrain = obj["Position X (mm)"]
                vertices = np.array(obj.get("verticles", []))
                x_max = np.max(vertices[:, 0])
                xposdrain += x_max
                found_drain = True
            if (
                all([found_tece, found_drain, found_floor150, found_floor])
                and len(unique_y) >= 2
            ):
                floor_small_x = [xposdrain - width150, xposdrain]
                floor_large_x = [xpostece, xpostece + width, xpostece + (width * 2)]
                min_step = min(height150, width)
                max_required_rows = (unique_y[-1] - unique_y[0]) // min_step
                base_keys = sorted(base_groups.keys())
                for base in base_keys:
                    max_counter = max(base_groups[base], default=0)
                    if max_counter < max_required_rows:
                        additional = list(range(max_counter + 1, max_required_rows + 1))
                        base_groups[base].extend(additional)
                all_x_positions = floor_small_x + floor_large_x
                tile_steps = [height150] * len(floor_small_x) + [width] * len(
                    floor_large_x
                )
                base_list = sorted(base_groups.keys())
                for i, base in enumerate(base_list):
                    x = all_x_positions[i]
                    step = tile_steps[i]
                    if step == height150:
                        y_start = unique_y[0] + height150
                        y_end = unique_y[-1]
                        z_max = min_z_floor_600
                    elif step == width:
                        y_start = unique_y[0] + width
                        y_end = unique_y[-1] + width
                        z_max = max_z_floor_600
                    y_positions = list(range(y_start, y_end, step))
                    for counter, y_pos in enumerate(y_positions, start=1):
                        label = f"{base}{counter}"
                        if not any(d["Point number/name"] == label for d in self.data):
                            depth = z_max + self.floor_offset
                            self.data.append(
                                {
                                    "Stage": "Stage 2",
                                    "Marking type": "Tile",
                                    "Point number/name": label,
                                    "Position X (mm)": x,
                                    "Position Y (mm)": y_pos,
                                    "Position Z (mm)": depth,
                                    "Wall Number": "7",
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
        return self.data
