import string
import pandas as pd
from openpyxl.utils import get_column_letter
import numpy as np
import ifcopenshell
import ifcopenshell.util.element as Element
from ifcopenshell.util.placement import get_local_placement
import math
import re
import PythonApplication.loadtmp as tmpinserter
import PythonApplication.loadtmp2 as tmpinserter2
from collections import defaultdict


class loadmainTMP:
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
        axis_widths,
        count_minus_y,
        count_plus_y,
        floor_offset
    ):
        self.data = data
        self.verts_data = verts_data
        self.Cellingstorey = Cellingstorey
        self.Cellingstoreyz = Cellingstorey[2]
        self.thickness = thickness
        self.wall_height = wall_height
        self.meterline = meterline
        self.ifc_file = ifc_file
        self.opening = ifc_file.by_type("IfcOpeningElement")
        self.dataopening = self.addobjects()
        self.label_map = label_map
        self.wall_finishes_height = wall_finishes_height
        self.small_wall_finishes_height = small_wall_finishes_height
        self.wall_format = wall_format
        self.index = 1
        self.axis_widths = axis_widths
        self.count_minus_y = count_minus_y
        self.count_plus_y = count_plus_y
        self.floor_offset = floor_offset
        self.x_min, self.x_max = min(self.axis_widths["x"]), max(self.axis_widths["x"])
        self.y_min, self.y_max = min(self.axis_widths["y"]), max(self.axis_widths["y"])
        self.addTMP1()

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
            raise TypeError(
                f"[FATAL] current_base is not a string: {type(current_base)}"
            )
        if len(current_base) < 7:
            raise ValueError(f"[FATAL] Base ID too short: '{current_base}'")
        if not current_base.startswith("TMP"):
            raise ValueError(
                f"[FATAL] Base ID does not start with TMP: '{current_base}'"
            )
        prefix = current_base[:-1]
        last_letter = current_base[-1].lower()
        if last_letter not in string.ascii_lowercase:
            raise ValueError(
                f"[FATAL] Invalid last letter in Base ID: '{last_letter}' from '{current_base}'"
            )
        next_index = string.ascii_lowercase.index(last_letter) + index_offset
        if next_index >= len(string.ascii_lowercase):
            raise ValueError(
                f"[FATAL] Base ID overflow: {current_base} + {index_offset}"
            )
        next_letter = string.ascii_lowercase[next_index]
        return f"{prefix}{next_letter}"

    def addTMP1(self):
        ceiling = int(self.Cellingstoreyz)
        self.zreference = self.find_first_z_reference(225)
        df = pd.read_excel(
            "PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl"
        )
        df = df[df["Stage 2"].notna()]
        df = df[df["Pin ID"].astype(str).str.startswith("TMP1S2")]
        df["Z Interval (mm)"] = df.apply(self.get_interval, axis=1)
        df["Base ID"] = df["Pin ID"].str.extract(r"(TMP1S2[a-z])", expand=False)
        grouped = df.groupby("Base ID").first().reset_index()
        candidate_objs = sorted(
            [
                obj
                for obj in self.verts_data
                if "Wall Finishes" in obj.get("Point number/name", "")
                and self.wall_height < obj["Position Y (mm)"] < self.thickness
            ],
            key=lambda o: o["Position X (mm)"],
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
                self.data.append(
                    {
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
                    }
                )
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
                    result_pairs.append(
                        [
                            unique_x_vertices[x_keys[i]][0],
                            unique_x_vertices[x_keys[i]][1],
                            unique_x_vertices[x_keys[j]][2],
                        ]
                    )
                    result_pairs.append(
                        [
                            unique_x_vertices[x_keys[j]][0],
                            unique_x_vertices[x_keys[j]][1],
                            unique_x_vertices[x_keys[i]][2],
                        ]
                    )
        for i, pair in enumerate(result_pairs):
            current_base = grouped.iloc[-1]["Base ID"]
            tmp_base = self.get_next_tmp_base(current_base, i + 1)
            interval = grouped.iloc[-1]["Z Interval (mm)"]
            xres, yres, zres = pair
            counter = 1
            for z in range(self.zreference, ceiling, interval):
                self.data.append(
                    {
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
                    }
                )
                counter += 1
        self.index += 1
        if self.count_plus_y == 2:
            datainserter = tmpinserter.loadTMP(
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
                self.count_plus_y,
                self.floor_offset
            )
        elif self.count_minus_y == 2:
            datainserter = tmpinserter2.loadTMP2(
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
                self.count_plus_y,
                self.floor_offset
            )
            datainserter.addTMP6()

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