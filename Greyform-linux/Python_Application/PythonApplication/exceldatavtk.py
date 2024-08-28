import pandas as pd
import vtk


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
        wall_numbers_by_sheet[sheet_name] = {
            "markingidentifiers": markingidentifiers,
            "wall_numbers": wall_numbers,
            "Position X (m)": positionx,
            "Position Y (m)": positiony,
            "Position Z (m)": positionz,
        }
    wall_identifiers = []
    wall_numbers = wall_numbers_by_sheet["IfcBuildingElementProxy"]["wall_numbers"]
    markingidentifiers = wall_numbers_by_sheet["IfcBuildingElementProxy"][
        "markingidentifiers"
    ]
    PositionX = wall_numbers_by_sheet["IfcBuildingElementProxy"]["Position X (m)"]
    PositionY = wall_numbers_by_sheet["IfcBuildingElementProxy"]["Position Y (m)"]
    PositionZ = wall_numbers_by_sheet["IfcBuildingElementProxy"]["Position Z (m)"]
    for rowidx, (name, wall_num, posx, posy, posz) in enumerate(
        zip(markingidentifiers, wall_numbers, PositionX, PositionY, PositionZ),
        start=1,
    ):
        if "CP" in name or "LP" in name or "SP" or "TMP" in name:
            if posz < 0:
                posz = 0
            wall_identifiers.append(
                {
                    "Point number/name": name.split(":")[0],
                    "Wall Number": wall_num,
                    "Position X (m)": posx,
                    "Position Y (m)": posy,
                    "Position Z (m)": posz,
                    "Point ID": None,
                }
            )
    return wall_identifiers


def excel_extractor(excel_file_path, reader):
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
        for x, y, z in zip(positionx, positiony, positionz):
            x, y, z = int(x), int(y), int(z)
            point_id = find_closest_point(reader, (x, y, z))
            wall_numbers_by_sheet[sheet_name] = {
                "markingidentifiers": markingidentifiers,
                "wall_numbers": wall_numbers,
                "Position X (m)": str(x),
                "Position Y (m)": str(y),
                "Position Z (m)": str(z),
                "Point ID": point_id,
            }
    return wall_numbers_by_sheet


def find_closest_point(polydata, target_position):
    point_locator = vtk.vtkKdTreePointLocator()
    point_locator.SetDataSet(polydata)
    point_locator.BuildLocator()
    point_id = point_locator.FindClosestPoint(target_position)
    return point_id
