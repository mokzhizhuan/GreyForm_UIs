import pandas as pd
import vtk

#Excel extractor
def exceldataextractor():
    excel_file_path = "exporteddatas.xlsx"
    all_sheets = pd.read_excel(excel_file_path, sheet_name=None)
    wall_numbers = []
    markingidentifiers = []
    wall_numbers_by_sheet = {}
    for sheet_name, df in all_sheets.items():
        wall_numbers = df["Wall Number"].tolist()
        markingidentifiers = df["Point number/name"].tolist()
        positionx = df["Position X (m)"].tolist()
        positiony = df["Position Y (m)"].tolist()
        positionz = df["Position Z (m)"].tolist()
        shapetype = df["Shape type"].tolist()
        wall_numbers_by_sheet[sheet_name] = {
            "markingidentifiers": markingidentifiers,
            "wall_numbers": wall_numbers,
            "Position X (m)": positionx,
            "Position Y (m)": positiony,
            "Position Z (m)": positionz,
            "Shape type": shapetype,
        }
    wall_identifiers = []
    wall_numbers = wall_numbers_by_sheet["IfcBuildingElementProxy"]["wall_numbers"]
    markingidentifiers = wall_numbers_by_sheet["IfcBuildingElementProxy"][
        "markingidentifiers"
    ]
    shapetypes = wall_numbers_by_sheet["IfcBuildingElementProxy"]["Shape type"]
    PositionX = wall_numbers_by_sheet["IfcBuildingElementProxy"]["Position X (m)"]
    PositionY = wall_numbers_by_sheet["IfcBuildingElementProxy"]["Position Y (m)"]
    PositionZ = wall_numbers_by_sheet["IfcBuildingElementProxy"]["Position Z (m)"]
    for rowidx, (name, wall_num, posx, posy, posz, shapetype) in enumerate(
        zip(
            markingidentifiers,
            wall_numbers,
            PositionX,
            PositionY,
            PositionZ,
            shapetypes,
        ),
        start=1,
    ):
        if "CP" in name or "LP" in name or "SP" in name or "TMP" in name:
            if posz < 0:
                posz = 0
            wall_identifiers.append(
                {
                    "Point number/name": name.split(":")[0],
                    "Wall Number": wall_num,
                    "Position X (m)": posx,
                    "Position Y (m)": posy,
                    "Position Z (m)": posz,
                    "Shape type": shapetype,
                    "Point ID": None,
                }
            )
    return wall_identifiers

