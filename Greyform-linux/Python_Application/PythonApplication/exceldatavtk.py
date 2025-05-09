import pandas as pd

def exceldataextractor():
    excel_file_path = "exporteddatassss(with TMP)(draft)(tetra).xlsx"
    all_sheets = pd.read_excel(excel_file_path, sheet_name=None)
    wall_numbers_by_sheet = {}
    unique_wall_numbers_by_sheet = {}
    unique_width_height_dict = {}  
    column_names = list(all_sheets.keys())
    if "Obstacles" in column_names:
        column_names.remove("Obstacles")
    for sheet_name, df in all_sheets.items():
        if "Wall Number" not in df.columns:
            continue  # Skip if no wall data in sheet
        if "Position X (mm)" in df.columns:
            df.rename(columns={
                "Position X (mm)": "Position X (m)",
                "Position Y (mm)": "Position Y (m)",
                "Position Z (mm)": "Position Z (m)",
            }, inplace=True)    
        df["Wall Number"] = df["Wall Number"].astype(str).fillna("Unknown")  # Convert all to string, replace NaN
        df["Wall Number"] = df["Wall Number"].apply(lambda x: int(x) if x.isdigit() else x)  # Convert numbers to int
        wall_numbers_by_sheet[sheet_name] = {
            "markingidentifiers": df["Point number/name"].astype(str).tolist(),
            "Wall Number": df["Wall Number"].tolist(),
            "Position X (m)": df["Position X (m)"].tolist(),
            "Position Y (m)": df["Position Y (m)"].tolist(),
            "Position Z (m)": df["Position Z (m)"].tolist(),
            "Shape type": df["Shape type"].tolist(),
            "width": df["Width"].tolist(),
            "height": df["Height"].tolist(),
            "Status": df["Status"].tolist(),
        }
        for wall_num, length, breath in zip(df["Wall Number"], df["Width"], df["Height"]):
            if wall_num not in unique_width_height_dict:
                unique_width_height_dict[wall_num] = {"width": set(), "height": set()}
            unique_width_height_dict[wall_num]["width"].add(length)
            unique_width_height_dict[wall_num]["height"].add(breath)
        unique_data = (
            df.groupby("Wall Number")
            .agg({"Status": lambda x: list(set(x))})  # Collect unique statuses for each wall number
            .reset_index()
        )
        unique_wall_numbers_by_sheet[sheet_name] = {
            "wall_numbers": unique_data["Wall Number"].tolist(),
            "status": unique_data["Status"].tolist(),
        }
    unique_width_height_df = pd.DataFrame([
        {"Wall Number": wall_num, "width": list(data["width"]), "height": list(data["height"])}
        for wall_num, data in unique_width_height_dict.items()
    ])
    wall_list = unique_width_height_df.to_dict(orient="records")
    return wall_numbers_by_sheet, wall_list, excel_file_path, unique_wall_numbers_by_sheet, column_names


def wall_format(wall):
    sorted_wall = sorted(
        wall, key=lambda x: int(x["Wall Number"]) if isinstance(x["Wall Number"], int) else float("inf")
    )
    wall_format = {}
    for dims in sorted_wall:
        Wallnum = dims["Wall Number"]  # Now correctly extracted
        width = dims.get("width", ["Not available"])  # Default to list
        height = dims.get("height", ["Not available"])  # Default to list
        width = width *1000
        height = height *1000
        width = width[0] if len(width) == 1 else width
        height = height[0] if len(height) == 1 else height
        if isinstance(Wallnum, int):
            axis = "y" if Wallnum % 2 == 0 else "x"
        else:
            axis = "Unknown"
        wall_format[Wallnum] = {"axis": axis, "width": width, "height": height}
    return wall_format





