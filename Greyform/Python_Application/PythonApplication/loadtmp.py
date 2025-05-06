import string
import pandas as pd
from openpyxl.utils import get_column_letter
import numpy as np
import ifcopenshell
import ifcopenshell.util.element as Element
from ifcopenshell.util.placement import get_local_placement
import math
import re
import PythonApplication.ifcextractfiles as extractor
from collections import defaultdict
import traceback

class loadTMP:
    def __init__(
        self,
        data,
        verts_data,
        Cellingstorey,
        thickness,
        wall_height,
        ifc_file,
        meterline,
        label_map,
        wall_finishes_height,
        small_wall_finishes_height,
        wall_format,
        axis_widths
    ):
        self.data = data
        self.verts_data = verts_data
        self.Cellingstoreyz = Cellingstorey[2]
        self.thickness = thickness
        self.wall_height = wall_height
        self.meterline = meterline
        self.wall_format = wall_format
        self.opening = ifc_file.by_type("IfcOpeningElement")
        self.dataopening = self.addobjects()
        self.label_map = label_map
        self.wall_finishes_height = wall_finishes_height
        self.small_wall_finishes_height = small_wall_finishes_height
        self.wall_format = wall_format
        self.index = 1
        self.axis_widths = axis_widths
        self.x_min, self.x_max = min(self.axis_widths["x"]), max(self.axis_widths["x"])
        self.y_min, self.y_max = min(self.axis_widths["y"]), max(self.axis_widths["y"])
        self.addTMP1()

    def get_tmp_label_from_excel(self, name: str, z_ref: int = 225, tolerance: int = 5, default="TMP??") -> str:
        df = pd.read_excel("PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl")
        df = df[df["Stage 2"].notna()]
        df["Name_clean"] = df["Penetration/Fitting/Reference Point Name"].astype(str).str.strip()
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
            if abs(pos_z - z_target) <= tolerance:
                print(f"[DEBUG] Found match in position: {name} with Z={pos_z}")
                return int(pos_z)
            vertices = obj.get("verticles", [])
            if len(vertices) > 0:
                try:
                    z_vals = vertices[:, 2]
                    for z in z_vals:
                        if abs(z - z_target) <= tolerance:
                            return int(z)
                except Exception as e:
                    print(f"[WARN] Error reading vertices from {name}: {e}")
        return z_target
    
    def get_wall_alias_from_excel(self, pin_id: str) -> str:
        df = pd.read_excel("PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl")
        # Clean and filter
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
        if not isinstance(current_base, str):
            raise TypeError(f"[FATAL] current_base is not a string: {type(current_base)}")
        if len(current_base) < 7:
            raise ValueError(f"[FATAL] Base ID too short: '{current_base}'")
        if not current_base.startswith("TMP"):
            raise ValueError(f"[FATAL] Base ID does not start with TMP: '{current_base}'")
        prefix = current_base[:-1]
        last_letter = current_base[-1].lower()
        if last_letter not in string.ascii_lowercase:
            raise ValueError(f"[FATAL] Invalid last letter in Base ID: '{last_letter}' from '{current_base}'")
        next_index = string.ascii_lowercase.index(last_letter) + index_offset
        if next_index >= len(string.ascii_lowercase):
            raise ValueError(f"[FATAL] Base ID overflow: {current_base} + {index_offset}")
        next_letter = string.ascii_lowercase[next_index]
        return f"{prefix}{next_letter}"

    def addTMP1(self):
        ceiling = int(self.Cellingstoreyz)
        self.zreference = self.find_first_z_reference(225)
        df = pd.read_excel("PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl")
        df = df[df["Stage 2"].notna()]
        df = df[df["Pin ID"].astype(str).str.startswith("TMP1S2")]
        df["Z Interval (mm)"] = df.apply(self.get_interval, axis=1)
        df["Base ID"] = df["Pin ID"].str.extract(r"(TMP1S2[a-z])", expand=False)
        grouped = df.groupby("Base ID").first().reset_index()
        candidate_objs = sorted(
            [
                obj for obj in self.verts_data
                 if "Wall Finishes" in obj.get("Point number/name", "")
                and self.wall_height < obj["Position Y (mm)"] < self.thickness
            ],
            key=lambda o: o["Position X (mm)"]
        )
        used_indices = set()
        for _, row in grouped.iterrows():
            tmp_base = row.get("Base ID", "")
            z_step = row["Z Interval (mm)"]
            label_name = str(row["Penetration/Fitting/Reference Point Name"])
            wall_name = self.get_wall_alias_from_excel(tmp_base)
            xpos = 0
            matched_obj = None
            if "Wall Finishes" in label_name:
                for idx, obj in enumerate(candidate_objs):
                    if idx in used_indices:
                        continue
                    raw_name = obj.get("Point number/name", "")
                    if label_name.lower() in raw_name.strip().lower():
                        matched_obj = obj
                        used_indices.add(idx)
                        break
            else:
                for obj in self.verts_data:
                    raw_name = obj.get("Point number/name", "")
                    if label_name.lower() in raw_name.strip().lower():
                        matched_obj = obj
                        break
            xpos = round(matched_obj.get("Position X (mm)", 0))
            repeat_count = int((ceiling - self.zreference) / z_step) + 1
            for i in range(repeat_count):
                z = self.zreference + i * z_step
                self.data.append({
                    "Stage": "Stage 2",
                    "Marking type": "Tile",
                    "Point number/name": f"{tmp_base}{i+1}",
                    "Position X (mm)": xpos,
                    "Position Y (mm)": self.thickness,
                    "Position Z (mm)": z,
                    "Wall Number": wall_name,
                    "Shape type": "",
                    "Status": "blank",
                    "Quadrant": 1,
                    "Unnamed : 9": "",
                    "Width": "",
                    "Height": "",
                    "Orientation": "",
                    "Diameter": "",
                })
        unique_x_vertices = {}
        for obj in self.dataopening:
            if "Wall Finishes" in obj.get("Name", ""):
                for x, y, z in obj["Vertices"]:
                    if x not in unique_x_vertices:
                        unique_x_vertices[x] = [x, y, z]
        x_keys = sorted(unique_x_vertices.keys())
        result_pairs = []
        for i in range(len(x_keys)):
            for j in range(i + 1, len(x_keys)):
                if abs(x_keys[i] - x_keys[j]) == self.meterline:
                    result_pairs.append([
                        unique_x_vertices[x_keys[i]][0],
                        unique_x_vertices[x_keys[i]][1],
                        unique_x_vertices[x_keys[j]][2],
                    ])
                    result_pairs.append([
                        unique_x_vertices[x_keys[j]][0],
                        unique_x_vertices[x_keys[j]][1],
                        unique_x_vertices[x_keys[i]][2],
                    ])
        for i, pair in enumerate(result_pairs):
            current_base = grouped.iloc[-1]["Base ID"]
            tmp_base = self.get_next_tmp_base(current_base, i + 1)
            interval = grouped.iloc[-1]["Z Interval (mm)"]
            xres, yres, zres = pair
            counter = 1
            for z in range(self.zreference, ceiling, interval):
                self.data.append({
                    "Stage": "Stage 2",
                    "Marking type": "Tile",
                    "Point number/name": f"{tmp_base}{counter}",
                    "Position X (mm)": xres,
                    "Position Y (mm)": self.thickness,
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
                counter += 1
        self.index += 1
        self.addTMP2()

    def addTMP2(self):
        wallname = ""
        wall_entry_for_b = None
        target_letter = "B"
        ceiling = int(self.Cellingstoreyz)
        df = pd.read_excel("PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl")
        df = df[df["Stage 2"].notna()]
        df = df[df["Pin ID"].astype(str).str.startswith("TMP2S2")]
        df["Z Interval (mm)"] = df.apply(self.get_interval, axis=1)
        df["Base ID"] = df["Pin ID"].str.extract(r"(TMP2S2[a-z])")
        grouped = df.groupby("Base ID").first().reset_index()
        for entry in self.label_map:
            letter, wall, *_ = entry
            if letter == target_letter:
                wallname = wall["name"]
                wall_entry_for_b = entry
                break
        candidate_objs = sorted(
            [obj for obj in self.verts_data
            if "Wall Finishes" in str(obj.get("Point number/name", ""))
            and self.is_near_wall(obj, wall_entry_for_b)],
            key=lambda o: o["Position X (mm)"]
        )
        for i, row in grouped.iterrows():
            tmp_base = row.get("Base ID", "")
            label_name = str(row.get("Penetration/Fitting/Reference Point Name", "")).strip().lower()
            interval = self.get_interval(row)
            matched_obj = None
            for idx, obj in enumerate(candidate_objs):
                if label_name in str(obj.get("Point number/name", "")).lower():
                    matched_obj = obj
                    break
                if matched_obj is None:
                    for objs in self.verts_data:
                        name = objs.get("Point number/name", "").lower()
                        if label_name in name:
                            x = objs["Position X (mm)"]
                            y = int(objs["Position Y (mm)"])
                            counter = 1
                            for z in range(self.zreference, ceiling, interval):
                                self.data.append({
                                    "Stage": "Stage 2",
                                    "Marking type": "Tile",
                                    "Point number/name": f"{tmp_base}{counter}",
                                    "Position X (mm)": self.thickness,
                                    "Position Y (mm)": y,
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
                                counter += 1
                    continue
                verts = matched_obj["verticles"]
                x_values = verts[:, 0]
                z_values = verts[:, 2]
                non_zero_x = x_values[x_values > 0]
                non_zero_z = z_values[z_values > 0]
                min_z = int(np.min(non_zero_z)) if non_zero_z.size else 0
                lowest_x = int(np.min(non_zero_x)) if non_zero_x.size else 0
                total_internal_wall = self.wall_format[self.index]["width"] - (self.thickness * 2)
                x_array = [total_internal_wall - lowest_x - interval, total_internal_wall - lowest_x]
                for idx, xpos in enumerate(x_array):
                    tmp_base = self.get_next_tmp_base("TMP2S2a", idx)
                    counter = 1
                    for z in range(self.zreference, min_z, interval):
                        self.data.append({
                            "Stage": "Stage 2",
                            "Marking type": "Tile",
                            "Point number/name": f"{tmp_base}{counter}",
                            "Position X (mm)": self.thickness,
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
                        })
                        counter += 1
        self.index += 1
        self.addTMP3()

    def addTMP3(self):
        ceiling = int(self.Cellingstoreyz)
        df = pd.read_excel("PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl")
        df = df[df["Stage 2"].notna()]
        df = df[df["Pin ID"].astype(str).str.startswith("TMP3S2")]
        df["Z Interval (mm)"] = df.apply(self.get_interval, axis=1)
        df["Base ID"] = df["Pin ID"].str.extract(r"(TMP3S2[a-z])")
        grouped = df.groupby("Base ID").first().reset_index()
        wallname = None
        for entry in self.label_map:
            letter, wall, direction, axis, wall_alias = entry
            if letter == "C":
                wallname = wall["name"]
                break
        target_obj = next((obj for obj in self.verts_data if wallname in obj.get("Point number/name", "")), None)
        verts = target_obj.get("verticles", [])
        x_values = verts[:, 0] if len(verts) else []
        x_max = int(np.max(x_values))
        half_x_max = (x_max - self.thickness) / 2
        x_array = [half_x_max + self.thickness, x_max]
        for i, x in enumerate(x_array):
            tmp_base = self.get_next_tmp_base("TMP3S2a", i)
            match = grouped[grouped["Base ID"] == tmp_base]
            interval = int(match["Z Interval (mm)"].values[0])
            counter = 1
            for z in range(self.zreference, ceiling, interval):
                self.data.append({
                    "Stage": "Stage 2",
                    "Marking type": "Tile",
                    "Point number/name": f"{tmp_base}{counter}",
                    "Position X (mm)": x,
                    "Position Y (mm)": self.y_max-self.y_min-self.thickness,
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
                })
                counter += 1
        self.index += 1
        self.addTMP4()

    def addTMP4(self):
        ceiling = int(self.Cellingstoreyz)
        df = pd.read_excel("PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl")
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
        matched_obj = next((obj for obj in self.verts_data if wallname in obj.get("Point number/name", "")), None)
        verts = matched_obj.get("verticles", [])
        x_values = verts[:, 0]
        x_max = int(np.max(x_values))
        xpos = matched_obj["Position X (mm)"]
        ypos = int(matched_obj["Position Y (mm)"])
        startingypos = ypos - self.wall_finishes_height - x_max
        wall_finish_obj = next(
            (
                obj for obj in self.verts_data
                if "Wall Finishes" in obj.get("Point number/name", "")
                and self.is_near_wall(obj, wall_entry)
            ),
            None
        )
        width = self.get_interval({"Penetration/Fitting/Reference Point Name": wall_finish_obj["Point number/name"]})
        x_array = [startingypos, startingypos + (width / 2)]
        for i, xpos in enumerate(x_array):
            tmp_base = self.get_next_tmp_base("TMP4S2a", i)
            match = grouped[grouped["Base ID"] == tmp_base]
            interval = int(match["Z Interval (mm)"].values[0])
            counter = 1
            for z in range(self.zreference, ceiling, interval):
                self.data.append({
                    "Stage": "Stage 2",
                    "Marking type": "Tile",
                    "Point number/name": f"{tmp_base}{counter}",
                    "Position X (mm)": (self.x_max-self.thickness)-self.x_min,
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
                })
                counter += 1
        self.index += 1
        self.addTMP5()

    def addTMP5(self):
        df = pd.read_excel("PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl")
        df = df[df["Stage 2"].notna()]
        df = df[df["Pin ID"].astype(str).str.startswith("TMP5S2")]
        df["Base ID"] = df["Pin ID"].str.extract(r"(TMP5S2[a-z])")
        grouped = df.groupby("Base ID").first().reset_index()
        for i, row in grouped.iterrows():
            tmp_base = row.get("Base ID", "")
            label_name = str(row.get("Penetration/Fitting/Reference Point Name", "")).strip().lower()
            if not label_name:
                continue
            matched_obj = next((obj for obj in self.verts_data
                                if label_name in str(obj.get("Point number/name", "")).lower()), None)
            xpos = matched_obj.get("Position X (mm)", 0)
            verts = matched_obj.get("verticles", [])
            x_values = verts[:, 0]
            filtered_x = x_values[(x_values > 0) & (x_values % 10 == 0)]
            unique_x = np.unique(filtered_x)
            if len(unique_x) >= 2:
                midpoint = unique_x[0] + unique_x[1]
                new_x = np.sort(np.append(unique_x, midpoint))
            else:
                new_x = np.sort(unique_x)
            counter = 1
            for x in new_x:
                self.data.append({
                    "Stage": "Stage 2",
                    "Marking type": "Tile",
                    "Point number/name": f"{tmp_base}{counter}",
                    "Position X (mm)": x + xpos,
                    "Position Y (mm)": self.y_max - self.small_wall_finishes_height -self.wall_height,
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
                counter += 1         
        self.index += 1
        self.addTMP6()

    def addTMP6(self):
        ceiling = int(self.Cellingstoreyz)
        df = pd.read_excel("PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl")
        df = df[df["Stage 2"].notna()]
        df = df[df["Pin ID"].astype(str).str.startswith("TMP6S2")]
        df["Z Interval (mm)"] = df.apply(self.get_interval, axis=1)
        df["Base ID"] = df["Pin ID"].str.extract(r"(TMP6S2[a-z])")
        grouped = df.groupby("Base ID").first().reset_index()
        wall_entry = None
        wallname = ""
        for entry in self.label_map:
            letter, wall, *_ = entry
            if letter == "F":
                wall_entry = entry
                wallname = wall["name"]
                break
        matched_wall_obj = next((obj for obj in self.verts_data if wallname in obj.get("Point number/name", "")), None)
        xpos = matched_wall_obj.get("Position X (mm)", 0)
        ypos = matched_wall_obj.get("Position Y (mm)", 0)
        x_values = matched_wall_obj.get("verticles", [])[:, 0] if len(matched_wall_obj.get("verticles", [])) else []
        x_max = np.max(x_values) - self.wall_height - self.small_wall_finishes_height
        wall_finish_obj = next(
            (obj for obj in self.verts_data
            if "Wall Finishes" in obj.get("Point number/name", "")
            and self.is_near_wall(obj, wall_entry, threshold=100)),
            None
        )   
        width = self.get_interval({"Penetration/Fitting/Reference Point Name": wall_finish_obj["Point number/name"]})
        x_array = [x_max - width, x_max - (width * 2)]
        for i, xpos in enumerate(x_array):
            tmp_base = self.get_next_tmp_base("TMP6S2a", i)
            match = grouped[grouped["Base ID"] == tmp_base]
            interval = int(match.iloc[0]["Z Interval (mm)"]) if not match.empty else 600
            counter = 1
            for z in range(self.zreference, ceiling, interval):
                self.data.append({
                    "Stage": "Stage 2",
                    "Marking type": "Tile",
                    "Point number/name": f"{tmp_base}{counter}",
                    "Position X (mm)": self.x_max-self.thickness,
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
                })
                counter += 1  
        self.index += 1
        self.addTMP7()

    def addTMP7(self):
        df = pd.read_excel("PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl")
        df = df[df["Stage 2"].notna()]
        df = df[df["Pin ID"].astype(str).str.startswith("TMP7S2")]
        base_groups = defaultdict(list)
        for pid in df["Pin ID"].dropna().astype(str):
            match = re.fullmatch(r"TMP7S2([a-z])(\d+)", pid)
            if match:
                letter, number = match.groups()
                base = f"TMP7S2{letter}"
                base_groups[base].append(int(number))
        ref_names = df["Penetration/Fitting/Reference Point Name"].dropna().astype(str).unique()
        target_name_keyword150 = next((n for n in ref_names if "150mm" in n.lower() and "floor" in n.lower()), None)
        target_name_keyword600 = next((n for n in ref_names if "600mm" in n.lower() and "floor" in n.lower()), None)
        tece_label = next((n for n in ref_names if "tece" in n.lower()), None)
        drain_label = next((n for n in ref_names if "drain" in n.lower()), None)
        found_tece = found_floor150 = found_floor = found_drain = False
        unique_y = []
        width = height = width150 = height150 = 0
        for obj in self.verts_data:
            name = obj.get("Point number/name", "")
            prefinedType = obj.get("PredefinedType", "")
            level = obj.get("Level", "")
            if tece_label and tece_label in name:
                xpostece = obj["Position X (mm)"]
                found_tece = True
            if "floor" in name.lower() and "floor" in prefinedType.lower() and "bedroom" in level.lower():
                vertices = np.array(obj.get("verticles", []))
                if target_name_keyword150 and target_name_keyword150 in name:
                    y_values = vertices[:, 1]
                    rounded_y = np.ceil(y_values / 10) * 10
                    unique_y = np.unique(rounded_y.astype(int))
                    match = re.search(r"\((\d+)[xX](\d+)mm\)", name)
                    if match:
                        width150 = int(match.group(1))
                        height150 = int(match.group(2))
                    found_floor150 = True
                if target_name_keyword600 and target_name_keyword600 in name:
                    match = re.search(r"\((\d+)[xX](\d+)mm\)", name)
                    if match:
                        width = int(match.group(1))
                        height = int(match.group(2))
                    found_floor = True
            if drain_label and drain_label in name:
                xposdrain = obj["Position X (mm)"]
                vertices = np.array(obj.get("verticles", []))
                x_max = np.max(vertices[:, 0])
                xposdrain += x_max
                found_drain = True
            if all([found_tece, found_drain, found_floor150, found_floor]) and len(unique_y) >= 2:
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
                tile_steps = [height150] * len(floor_small_x) + [width] * len(floor_large_x)
                base_list = sorted(base_groups.keys())
                for i, base in enumerate(base_list):
                    x = all_x_positions[i]
                    step = tile_steps[i]
                    if step == height150:
                        y_start = unique_y[0] + height150
                        y_end = unique_y[-1]
                    elif step == width:
                        y_start = unique_y[0] + width
                        y_end = unique_y[-1] + width
                    y_positions = list(range(y_start, y_end, step))
                    for counter, y_pos in enumerate(y_positions, start=1):
                        label = f"{base}{counter}"
                        if not any(d["Point number/name"] == label for d in self.data):
                            self.data.append({
                                "Stage": "Stage 2",
                                "Marking type": "Tile",
                                "Point number/name": label,
                                "Position X (mm)": x,
                                "Position Y (mm)": y_pos,
                                "Position Z (mm)": 0,
                                "Wall Number": "7",
                                "Shape type": "",
                                "Status": "blank",
                                "Quadrant": 1,
                                "Unnamed : 9": "",
                                "Width": "",
                                "Height": "",
                                "Orientation": "",
                                "Diameter": "",
                                })
        return self.data

    def addobjects(self):
        objects_data = []
        for object in self.opening:
            x, y, z = (0, 0, 0)
            if object.ObjectPlacement:
                placement = object.ObjectPlacement.RelativePlacement
                if placement and placement.Location:
                    x, y, z = placement.Location.Coordinates
                revert_origin = object.Name if object.Name == "CP1:CP1:1433163" else ""
                scale_factor = 1000.0
            if object.Representation is not None:
                settings = ifcopenshell.geom.settings()
                shape = ifcopenshell.geom.create_shape(settings, object)
                verts = shape.geometry.verts
                grouped_verts = [
                    [verts[i], verts[i + 1], verts[i + 2]]
                    for i in range(0, len(verts), 3)
                ]
                scaled_grouped_verts = np.array(grouped_verts) * scale_factor
                scaled_grouped_verts = scaled_grouped_verts.astype(int)
            objects_data.append(
                {
                    "ExpressID": object.id(),
                    "GlobalID": object.GlobalId,
                    "Class": object.is_a(),
                    "PredefinedType": Element.get_predefined_type(object),
                    "Name": object.Name,
                    "Level": (
                        Element.get_container(object).Name
                        if Element.get_container(object)
                        else ""
                    ),
                    "ObjectType": (
                        Element.get_type(object).Name
                        if Element.get_type(object)
                        else ""
                    ),
                    "Position": [x, y, z],
                    "RevertOrigin": revert_origin,
                    "Vertices": scaled_grouped_verts,
                }
            )
        return objects_data
