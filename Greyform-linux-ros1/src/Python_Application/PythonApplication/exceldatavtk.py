import pandas as pd
import vtk


# excel extractor for vtk
def exceldataextractor():
    excel_file_path = "exporteddatassss(with TMP)(draft).xlsx"
    all_sheets = pd.read_excel(excel_file_path, sheet_name=None)
    wall_numbers = []
    markingidentifiers = []
    wall_numbers_by_sheet = {}
    unique_wall_numbers_by_sheet = {}
    wall = []
    dfs = pd.ExcelFile(excel_file_path)
    column_names = dfs.sheet_names
    if "Obstacles" in column_names:
        index = column_names.index("Obstacles")  # Find index
        column_names.pop(index)  # Remove by index
    for sheet_name, df in all_sheets.items():
        wall_numbers = df["Wall Number"].tolist()
        markingidentifiers = df["Point number/name"].astype(str).tolist()
        positionx = df["Position X (mm)"].tolist()
        positiony = df["Position Y (mm)"].tolist()
        positionz = df["Position Z (mm)"].tolist()
        status = df["Status"].tolist()
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
            "Status" : status,
        }
        unique_data = (
            df.groupby("Wall Number")
            .agg({"Status": lambda x: list(set(x))})  # Collect unique statuses for each wall number
            .reset_index()
        )
        unique_wall_numbers_by_sheet[sheet_name] = {
            "wall_numbers": unique_data["Wall Number"].tolist(),
            "status": unique_data["Status"].tolist(),
        }
    wall_numberes = wall_numbers_by_sheet["Stage 2"]["wall_numbers"]
    markingidentifierswall = wall_numbers_by_sheet["Stage 2"][
        "markingidentifiers"
    ]
    shapetypes = wall_numbers_by_sheet["Stage 2"]["Shape type"]
    PositionX = wall_numbers_by_sheet["Stage 2"]["Position X (m)"]
    PositionY = wall_numbers_by_sheet["Stage 2"]["Position Y (m)"]
    PositionZ = wall_numbers_by_sheet["Stage 2"]["Position Z (m)"]
    widths = wall_numbers_by_sheet["Stage 2"]["width"]
    heights = wall_numbers_by_sheet["Stage 2"]["height"]
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
            new_wall = {
                "Point number/name": name,
                "Wall Number": wall_num,
                "Position X (m)": posx,
                "Position Y (m)": posy,
                "Position Z (m)": posz,
                "Shape type": shapetype,
                "width": length,
                "height": breath,
            }
            if new_wall not in wall:
                wall.append(new_wall)
    return wall_numbers_by_sheet , wall , excel_file_path , unique_wall_numbers_by_sheet , column_names

def wall_format(wall):
    sorted_wall = sorted(wall, key=lambda x: x.get("Wall Number", float('inf')))
    wall_format = {}
    axis = ""
    for index, (dims) in enumerate(sorted_wall, start=0):
        Wallnum = dims.get("Wall Number", "Not available")
        width = dims.get("width", "Not available")
        height = dims.get("height", "Not available")
        if Wallnum % 2 == 0:
            axis = "y"
        else:
            axis = "x"
        wall_format[Wallnum] = {"axis": axis, "width": width , "height": height}
    return wall_format 


