import string
import pandas as pd
from openpyxl.utils import get_column_letter

class loadTMP():
    def __init__(self , data , verts_data, Cellingstorey, thickness , wall_height):
        self.data = data
        self.verts_data = verts_data
        self.Cellingstoreyz = Cellingstorey[2]
        self.thickness = thickness
        self.wall_height = wall_height
        self.addTMP1()

    def addTMP1(self):
        dataframe_Legend = pd.read_excel(
                "PinAllocationBOMforPBU_T1am.xlsx", skiprows=2, engine="openpyxl"
            )
        print(f"Before: {len(self.data)}")
        ceiling = int(self.Cellingstoreyz)
        for item in self.verts_data:
            name = item["Point number/name"]
            if "GESSI.SH" in name:
                vertices = item["verticles"]
                if len(vertices) > 0:
                    x1, y1, z1 = vertices[-1]
        for obj in self.verts_data:
            name = obj.get("Point number/name", "")
            if "GESSI.SH" in name:
                x = obj["Position X (mm)"]
                y = obj["Position Y (mm)"]
                z = obj["Position Z (mm)"]
                z = int(z)
                counter = 1
                for i in range(z1, ceiling, 600):
                    self.data.append({
                        "Stage": "",
                        "Marking type": "Tile",
                        "Point number/name": f"TMP1S1a{counter}",
                        "Position X (mm)": x,
                        "Position Y (mm)": self.thickness,
                        "Position Z (mm)": i,
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
        all_wall_finishes = [obj for obj in self.verts_data if "Wall Finishes" in obj.get("Point number/name", "")]
        filtered_wall_finishes = [obj for obj in all_wall_finishes if self.wall_height < obj["Position Y (mm)"] < self.thickness]
        # Assign letters only to filtered
        wall_finish_id_map = {}
        for i, obj in enumerate(sorted(filtered_wall_finishes, key=lambda o: int(o["Point number/name"].split(":")[-1]))):
            obj_id = int(obj["Point number/name"].split(":")[-1])
            wall_finish_id_map[obj_id] = string.ascii_lowercase[i + 1]
        for obj in filtered_wall_finishes:
            obj_id = int(obj["Point number/name"].split(":")[-1])
            letter = wall_finish_id_map.get(obj_id, "?")  # fallback just in case
            counter = 1
            for i in range(z1, ceiling, 600):
                self.data.append({
                    "Stage": "",
                    "Marking type": "Tile",
                    "Point number/name": f"TMP1S1{letter}{counter}",
                    "Position X (mm)": x,
                    "Position Y (mm)": self.thickness,
                    "Position Z (mm)": i,
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
        for obj in self.verts_data:
            name = obj.get("Point number/name", "")
            if "TECE.CHAIR" in name:
                x = obj["Position X (mm)"]
                y = obj["Position Y (mm)"]
                z = obj["Position Z (mm)"]
                z = int(z)
                counter = 1
                for i in range(z1, ceiling, 600):
                    self.data.append({
                        "Stage": "",
                        "Marking type": "Tile",
                        "Point number/name": f"TMP1S1d{counter}",
                        "Position X (mm)": x,
                        "Position Y (mm)": self.thickness,
                        "Position Z (mm)": i,
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
        
        print(f"After: {len(self.data)}")
            