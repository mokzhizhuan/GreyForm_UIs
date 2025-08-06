import pandas as pd
import vtk


def exceldataextractor(excel_file):
    all_sheets = pd.read_excel(excel_file, sheet_name=None)
    wall_numbers_by_sheet = {}
    unique_wall_numbers_by_sheet = {}
    unique_width_height_dict = {}
    column_names = list(all_sheets.keys())
    if "Obstacles" in column_names:
        column_names.remove("Obstacles")
    for sheet_name, df in all_sheets.items():
        # Ensure all required columns exist
        required_columns = {
            "Wall Number", "Name", "Position X", "Position Y", "Position Z",
            "Shape Type", "Width", "Height", "Status"
        }
        if not required_columns.issubset(set(df.columns)):
            continue  # Skip this sheet if any column is missing
        df["Wall Number"] = (df["Wall Number"].astype(str).fillna("Unknown"))
        df["Wall Number"] = df["Wall Number"].apply(lambda x: int(x) if x.isdigit() else x)
        wall_numbers_by_sheet[sheet_name] = {
            "markingidentifiers": df["Name"].astype(str).tolist(),
            "Wall Number": df["Wall Number"].tolist(),
            "Position X": df["Position X"].tolist(),
            "Position Y": df["Position Y"].tolist(),
            "Position Z": df["Position Z"].tolist(),
            "Shape Type": df["Shape Type"].tolist(),
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
              .agg({"Status": lambda x: list(set(x))})
              .reset_index()
        )
        unique_wall_numbers_by_sheet[sheet_name] = {
            "wall_numbers": unique_data["Wall Number"].tolist(),
            "status": unique_data["Status"].tolist(),
        }
    unique_width_height_df = pd.DataFrame([
        {
            "Wall Number": wall_num,
            "width": list(data["width"]),
            "height": list(data["height"]),
        }
        for wall_num, data in unique_width_height_dict.items()
    ])
    wall_list = unique_width_height_df.to_dict(orient="records")
    return (
        wall_numbers_by_sheet,
        wall_list,
        unique_wall_numbers_by_sheet,
        column_names,
    )


def wall_format(wall):
    sorted_wall = sorted(
        wall,
        key=lambda x: (
            int(x["Wall Number"]) if isinstance(x["Wall Number"], int) else float("inf")
        ),
    )
    wall_format = {}
    for dims in sorted_wall:
        Wallnum = dims["Wall Number"]  # Now correctly extracted
        width = dims.get("width", ["Not available"])  # Default to list
        height = dims.get("height", ["Not available"])  # Default to list
        width = width * 1000
        height = height * 1000
        width = width[0] if len(width) == 1 else width
        height = height[0] if len(height) == 1 else height
        if isinstance(Wallnum, int):
            axis = "y" if Wallnum % 2 == 0 else "x"
        else:
            axis = "Unknown"
        wall_format[Wallnum] = {"axis": axis, "width": width, "height": height}
    return wall_format
