import pandas as pd
import vtk


# excel extractor for vtk
def exceldataextractor():
    excel_file_path = "exporteddatass.xlsx"
    all_sheets = pd.read_excel(excel_file_path, sheet_name=None)
    wall_numbers = []
    markingidentifiers = []
    wall_numbers_by_sheet = {}
    wall = []
    for sheet_name, df in all_sheets.items():
        wall_numbers = df["Wall Number"].tolist()
        markingidentifiers = df["Point number/name"].astype(str).tolist()
        positionx = df["Position X (m)"].tolist()
        positiony = df["Position Y (m)"].tolist()
        positionz = df["Position Z (m)"].tolist()
        shapetype = df["Shape type"].tolist()
        width = df["Width"].tolist()
        height = df["Height"].tolist()
        wall_numbers_by_sheet[sheet_name] = {
            "markingidentifiers": markingidentifiers,
            "wall_numbers": wall_numbers,
            "Position X (m)": positionx,
            "Position Y (m)": positiony,
            "Position Z (m)": positionz,
            "Shape type": shapetype,
            "width" : width,
            "height" : height,
        }
    wall_numberes = wall_numbers_by_sheet["Stage 3"]["wall_numbers"]
    markingidentifierswall = wall_numbers_by_sheet["Stage 3"][
        "markingidentifiers"
    ]
    shapetypes = wall_numbers_by_sheet["Stage 3"]["Shape type"]
    PositionX = wall_numbers_by_sheet["Stage 3"]["Position X (m)"]
    PositionY = wall_numbers_by_sheet["Stage 3"]["Position Y (m)"]
    PositionZ = wall_numbers_by_sheet["Stage 3"]["Position Z (m)"]
    widths = wall_numbers_by_sheet["Stage 3"]["width"]
    heights = wall_numbers_by_sheet["Stage 3"]["height"]
    for rowidx, (name, wall_num, posx, posy, posz, shapetype, length, breath) in enumerate(
        zip(
            markingidentifierswall,
            wall_numberes,
            PositionX,
            PositionY,
            PositionZ,
            shapetypes,
            widths,
            heights,
        ),
        start=0,
    ):
        if "Basic Wall:BSS.50" in name:
            wall.append(
                {
                    "Point number/name": name,
                    "Wall Number": wall_num,
                    "Position X (m)": posx,
                    "Position Y (m)": posy,
                    "Position Z (m)": posz,
                    "Shape type": shapetype,
                    "width" : length,
                    "height" : breath,
                }
            )
    return wall_numbers_by_sheet , wall , excel_file_path

