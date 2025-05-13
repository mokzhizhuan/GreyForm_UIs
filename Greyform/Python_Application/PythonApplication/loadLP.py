
import pandas as pd
from ifcopenshell.util.placement import get_local_placement, get_axis2placement
import numpy as np

class loadLP:
    def __init__(self,data,verts_data,offset):
        self.data = data
        self.verts_data = verts_data
        self.offset = offset
        self.loadLP1()

    def get_wall_alias_from_excel(self, pin_id: str) -> str:
        df = pd.read_excel("PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl")
        df = df[df["Stage 2"].notna()]
        df["Pin ID"] = df["Pin ID"].astype(str)
        df["Pin Base"] = df["Pin ID"].str.extract(r"(TMP\\d+S\\d+[a-z])")
        match = df[df["Pin ID"] == pin_id]
        if not match.empty:
            wall = match.iloc[0]["Wall"]
            return str(wall).strip() if pd.notna(wall) else "Unknown"
        return "Unknown"

    def loadLP1(self):
        df = pd.read_excel("PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl")
        df = df[df["Stage 3"].notna()]
        df = df[df["Pin ID"].astype(str).str.startswith("LP1S3")]
        df["Base ID"] = df["Pin ID"].str.extract(r"(LP1S3[a-z])", expand=False)
        grouped = df.groupby("Base ID").first().reset_index()
        for _, row in grouped.iterrows():
            LP_base = row.get("Base ID", "")
            label_name = str(row["Penetration/Fitting/Reference Point Name"])
            wall_name = self.get_wall_alias_from_excel(LP_base)
            for obj in self.verts_data:
                raw_name = obj.get("Point number/name", "")
                if label_name.lower() in raw_name.strip().lower():
                    xpos = obj.get("Position X (mm)", 0)
                    ypos = obj.get("Position Y (mm)", 0)
                    zpos = obj.get("Position Z (mm)", 0)
                    vert = np.array(obj.get("verticles", []))
                    self.data = [entry for entry in self.data if label_name.lower() not in str(entry.get("Point number/name", "")).lower()]
                    if len(vert) > 0:
                        vert = np.array(vert)
                        x_min, x_max = vert[:, 0].min(), vert[:, 0].max()
                        z_min, z_max = vert[:, 2].min(), vert[:, 2].max()
                        x_offset = (x_max - x_min) // 2
                        z_offset = (z_max - z_min) // 2
                        positions = [
                            ("1", xpos - x_offset, ypos, zpos + z_offset),  # Upper Left
                            ("2", xpos + x_offset, ypos, zpos + z_offset),  # Upper Right
                            ("3", xpos - x_offset, ypos, zpos - z_offset),  # Lower Left
                            ("4", xpos + x_offset, ypos, zpos - z_offset),  # Lower Right
                        ]
                        for suffix, x, y, z in positions:
                            self.data.append({
                                "Stage": "Stage 3",
                                "Marking type": "Fitting",
                                "Point number/name": f"{LP_base}{suffix}",
                                "Position X (mm)": int(x),
                                "Position Y (mm)": int(y),
                                "Position Z (mm)": int(z),
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
        self.loadLP3()
    
    def loadLP3(self):
        df = pd.read_excel("PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl")
        df = df[df["Stage 3"].notna()]
        df = df[df["Pin ID"].astype(str).str.startswith("LP3S3")]
        df["Base ID"] = df["Pin ID"].str.extract(r"(LP3S3[a-z])", expand=False)
        grouped = df.groupby("Base ID").first().reset_index()
        for _, row in grouped.iterrows():
            LP_base = row.get("Base ID", "")
            label_name = str(row["Penetration/Fitting/Reference Point Name"])
            wall_name = self.get_wall_alias_from_excel(LP_base)
            for obj in self.verts_data:
                raw_name = obj.get("Point number/name", "")
                if label_name.lower() in raw_name.strip().lower():
                    xpos = obj.get("Position X (mm)", 0)
                    ypos = obj.get("Position Y (mm)", 0)
                    zpos = obj.get("Position Z (mm)", 0)
                    vert = np.array(obj.get("verticles", []))
                    self.data = [entry for entry in self.data if label_name.lower() not in str(entry.get("Point number/name", "")).lower()]
                    if len(vert) > 0:
                        vert = np.array(vert)
                        x_min, x_max = vert[:, 0].min(), vert[:, 0].max()
                        z_min, z_max = vert[:, 2].min(), vert[:, 2].max()
                        x_offset = (x_max - x_min) // 2
                        z_offset = (z_max - z_min) // 2
                        positions = [
                            ("1", xpos - x_offset, ypos, zpos + z_offset),  # Upper Left
                            ("2", xpos + x_offset, ypos, zpos + z_offset),  # Upper Right
                            ("3", xpos - x_offset, ypos, zpos - z_offset),  # Lower Left
                            ("4", xpos + x_offset, ypos, zpos - z_offset),  # Lower Right
                        ]
                        for suffix, x, y, z in positions:
                            self.data.append({
                                "Stage": "Stage 3",
                                "Marking type": "Fitting",
                                "Point number/name": f"{LP_base}{suffix}",
                                "Position X (mm)": int(x),
                                "Position Y (mm)": int(y),
                                "Position Z (mm)": int(z),
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
        self.loadLP4()

    def loadLP4(self):
        df = pd.read_excel("PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl")
        df = df[df["Stage 3"].notna()]
        df = df[df["Pin ID"].astype(str).str.startswith("LP4S3")]
        df["Base ID"] = df["Pin ID"].str.extract(r"(LP4S3[a-z])", expand=False)
        grouped = df.groupby("Base ID").first().reset_index()
        for _, row in grouped.iterrows():
            LP_base = row.get("Base ID", "")
            label_name = str(row["Penetration/Fitting/Reference Point Name"])
            wall_name = self.get_wall_alias_from_excel(LP_base)
            for obj in self.verts_data:
                raw_name = obj.get("Point number/name", "")
                if label_name.lower() in raw_name.strip().lower():
                    xpos = obj.get("Position X (mm)", 0)
                    ypos = obj.get("Position Y (mm)", 0)
                    zpos = obj.get("Position Z (mm)", 0)
                    vert = np.array(obj.get("verticles", []))
                    self.data = [entry for entry in self.data if label_name.lower() not in str(entry.get("Point number/name", "")).lower()]
                    if len(vert) > 0:
                        vert = np.array(vert)
                        y_min, y_max = vert[:, 1].min(), vert[:, 1].max()
                        y_offset = (y_max - y_min) // 2
                        positions = [
                            ("1", xpos, ypos - y_offset, zpos),  # Upper Left
                            ("2", xpos, ypos + y_offset, zpos),  # Upper Right
                        ]
                        for suffix, x, y, z in positions:
                            self.data.append({
                                "Stage": "Stage 3",
                                "Marking type": "Fitting",
                                "Point number/name": f"{LP_base}{suffix}",
                                "Position X (mm)": int(x),
                                "Position Y (mm)": int(y),
                                "Position Z (mm)": int(z),
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
        self.loadLP5()

    def loadLP5(self):
        df = pd.read_excel("PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl")
        df = df[df["Stage 3"].notna()]
        df = df[df["Pin ID"].astype(str).str.startswith("LP5S3")]
        df["Base ID"] = df["Pin ID"].str.extract(r"(LP5S3[a-z])", expand=False)
        grouped = df.groupby("Base ID").first().reset_index()
        for _, row in grouped.iterrows():
            LP_base = row.get("Base ID", "")
            label_name = str(row["Penetration/Fitting/Reference Point Name"])
            wall_name = self.get_wall_alias_from_excel(LP_base)
            for obj in self.verts_data:
                raw_name = obj.get("Point number/name", "")
                if label_name.lower() in raw_name.strip().lower():
                    xpos = obj.get("Position X (mm)", 0)
                    ypos = obj.get("Position Y (mm)", 0)
                    zpos = obj.get("Position Z (mm)", 0)
                    vert = np.array(obj.get("verticles", []))
                    self.data = [entry for entry in self.data if label_name.lower() not in str(entry.get("Point number/name", "")).lower()]
                    if len(vert) > 0:
                        vert = np.array(vert)
                        x_min, x_max = vert[:, 0].min(), vert[:, 0].max()
                        z_min, z_max = vert[:, 2].min(), vert[:, 2].max()
                        x_offsets = (x_max - x_min)
                        if "basin" in label_name.lower():
                            x_offset = (x_max - x_min) // (2*2)
                        else:
                            x_offset = (x_max - x_min) // 2
                        if "mirror" in label_name.lower():
                            z_offset = 0
                        else:
                            z_offset = (z_max - z_min) // 2
                        if "tece" in label_name.lower():
                            zmax = z_max
                        else:
                            zmax = z_max - z_min
                        if "tece" in label_name.lower():
                            if "concealed" in label_name.lower():
                                positions = [
                                    ("1", xpos, ypos, zpos + z_offset + zmax),  # Upper Left
                                    ("2", xpos + x_offsets, ypos, zpos + z_offset + zmax),  # Upper Right
                                    ("3", xpos, ypos, zpos - z_offset + zmax),  # Lower Left
                                    ("4", xpos + x_offsets, ypos, zpos - z_offset + zmax),  # Lower Right
                                    ("5", xpos + x_offset, ypos, zpos + zmax),  # original Position
                                ]
                            else:
                                positions = [
                                    ("1", xpos - x_offset, ypos, zpos + z_offset + zmax),  # Upper Left
                                    ("2", xpos + x_offset, ypos, zpos + z_offset + zmax),  # Upper Right
                                    ("3", xpos - x_offset, ypos, zpos - z_offset + zmax),  # Lower Left
                                    ("4", xpos + x_offset, ypos, zpos - z_offset + zmax),  # Lower Right
                                    ("5", xpos , ypos, zpos + zmax),  # original Position
                                ]
                        else:
                            positions = [
                                ("1", xpos - x_offset, ypos, zpos + z_offset + zmax),  # Upper Left
                                ("2", xpos + x_offset, ypos, zpos + z_offset + zmax),  # Upper Right
                                ("3", xpos - x_offset, ypos, zpos - z_offset + zmax),  # Lower Left
                                ("4", xpos + x_offset, ypos, zpos - z_offset + zmax),  # Lower Right
                            ]
                        for suffix, x, y, z in positions:
                            self.data.append({
                                "Stage": "Stage 3",
                                "Marking type": "Fitting",
                                "Point number/name": f"{LP_base}{suffix}",
                                "Position X (mm)": int(x),
                                "Position Y (mm)": int(y),
                                "Position Z (mm)": int(z),
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
        self.loadLP7()

    def loadLP7(self):
        df = pd.read_excel("PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl")
        df = df[df["Stage 3"].notna()]
        df = df[df["Pin ID"].astype(str).str.startswith("LP7S3")]
        df["Base ID"] = df["Pin ID"].str.extract(r"(LP7S3[a-z])", expand=False)
        grouped = df.drop_duplicates(subset="Base ID")
        processed_bases = set()
        for _, row in grouped.iterrows():
            LP_base = row["Base ID"]
            if LP_base in processed_bases:
                continue  # ✅ skip duplicates
            processed_bases.add(LP_base)
            label_name = str(row["Penetration/Fitting/Reference Point Name"]).strip().lower()
            wall_name = self.get_wall_alias_from_excel(LP_base)
            for obj in self.verts_data:
                raw_name = obj.get("Point number/name", "").strip().lower()
                if label_name in raw_name:
                    xpos = obj.get("Position X (mm)", 0)
                    ypos = obj.get("Position Y (mm)", 0)
                    zpos = obj.get("Position Z (mm)", 0)
                    vert = np.array(obj.get("verticles", []))
                    self.data = [
                        entry for entry in self.data 
                        if LP_base not in str(entry.get("Point number/name", "")).strip().lower()
                    ]
                    if len(vert) == 0:
                        break
                    x_min, x_max = vert[:, 0].min(), vert[:, 0].max()
                    z_min, z_max = vert[:, 2].min(), vert[:, 2].max()
                    x_offset = (x_max - x_min) // 2
                    z_offset = (z_max - z_min) // 2
                    positions = [
                        ("1", xpos - x_offset, ypos, zpos + z_offset + z_max),
                        ("2", xpos + x_offset, ypos, zpos + z_offset + z_max),
                        ("3", xpos - x_offset, ypos, zpos - z_offset + z_max),
                        ("4", xpos + x_offset, ypos, zpos - z_offset + z_max),
                    ]
                    for suffix, x, y, z in positions:
                        self.data.append({
                            "Stage": "Stage 3",
                            "Marking type": "Fitting",
                            "Point number/name": f"{LP_base}{suffix}",
                            "Position X (mm)": int(x),
                            "Position Y (mm)": int(y),
                            "Position Z (mm)": int(z),
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
                    break  
        return self.data
