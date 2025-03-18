import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def stagecatergorize(ifc_file):
    data = {"Stage 1": [], "Stage 2": [], "Stage 3": []}

    def safe_get_name(element):
        return getattr(element, "Name", None)

    for element in ifc_file:
        name = safe_get_name(element)
        if element.is_a("IfcFlowSegment"):
            if name:
                data["Stage 1"].append(name)
        elif element.is_a("IfcCovering") or element.is_a("IfcWallStandardCase"):
            if name:
                data["Stage 2"].append(name)
        elif name and (
            "Shallow" in name
            or "Shower Door Hand Rail" in name
            or "Ceiling Access" in name
            or "GOMGO" in name
        ):
            data["Stage 2" if "Shallow" in name else "Stage 3"].append(name)
        elif (
            element.is_a("IfcDoor")
            or element.is_a("IfcFurnishingElement")
            or element.is_a("IfcSlab")
            or element.is_a("IfcFlowTerminal")
            or element.is_a("IfcFlowFitting")
        ):
            if name:
                if "Floor" in name or "Wall" in name:
                    data["Stage 2"].append(name)
                elif "BSS.Round" in name or "Elbow" in name or "M_Transition" in name:
                    data["Stage 1"].append(name)
                else:
                    data["Stage 3"].append(name)
    return data


def add_legends():
    dataframe_Legend = pd.read_excel("Pin Allocation BOM for PBU_T1a.xlsx", skiprows=2)
    pen_column = dataframe_Legend.columns[3]
    pin_id_column = dataframe_Legend.columns[9]
    dataframe_Legend = dataframe_Legend[[pen_column, pin_id_column]]
    if (
        pen_column in dataframe_Legend.columns
        and pin_id_column in dataframe_Legend.columns
    ):
        dataframe_Legend[pen_column].fillna("", inplace=True)
        dataframe_Legend[pin_id_column].fillna("", inplace=True)
        filtered_dataframe = dataframe_Legend[
            (dataframe_Legend[pen_column] != "")
            & (dataframe_Legend[pin_id_column] != "")
        ]
        wall_legend = filtered_dataframe.to_dict(orient="records")
        wall_name = "BSS.20mm Wall Finishes (600x600mm)"
        wall_600x600mm = []
        indexwall = 0
        index = 0
        for data_legend in wall_legend:
            data_pen_name = data_legend.get(pen_column)
            data_pin_id = data_legend.get(pin_id_column)
            if wall_name in data_pen_name:
                wall_600x600mm.append(
                    {
                        "Penetration/Fitting/Reference Point Name": data_pen_name,
                        "Pin ID": data_pin_id,
                    }
                )
    return wall_legend, pen_column, pin_id_column, wall_600x600mm, wall_name, indexwall


def wall_format(wall):
    wall_format = {}
    axis = ""
    for index, (wall, dims) in enumerate(wall.items(), start=0):
        width = dims.get("width", "Not available")
        depth = dims.get("depth", "Not available")
        height = dims.get("height", "Not available")
        if index % 2 == 0:
            axis = "y"
        else:
            axis = "x"
        if index + 1 in [2, 5]:
            wall_format[index + 1] = {
                "axis": axis,
                "width": width + height,
                "height": depth + height + 10,
            }
        elif index + 1 in [6]:
            wall_format[index + 1] = {
                "axis": axis,
                "width": width + (height * 2),
                "height": depth + height + 10,
            }
        else:
            wall_format[index + 1] = {
                "axis": axis,
                "width": width,
                "height": depth + height + 10,
            }
        heighttotal = depth + height + 10
    return wall_format, heighttotal , height

def wall_formats_reversed(wall):
    wall_format = {}
    axis = ""
    for index, (wall, dims) in enumerate(wall.items(), start=0):
        width = dims.get("width", "Not available")
        depth = dims.get("depth", "Not available")
        height = dims.get("height", "Not available")
        if index % 2 == 0:
            axis = "x"
        else:
            axis = "y"
        if index + 1 in [2, 5]:
            wall_format[index + 1] = {
                "axis": axis,
                "width": width + height,
                "height": depth + height + 10,
            }
        elif index + 1 in [1]:
            wall_format[index + 1] = {
                "axis": axis,
                "width": width + (height * 2),
                "height": depth + height + 10,
            }
        else:
            wall_format[index + 1] = {
                "axis": axis,
                "width": width,
                "height": depth + height + 10,
            }
        heighttotal = depth + height + 10
    return wall_format, heighttotal , height



def wall_format_finishes(wall):
    for index, (wall, dims) in enumerate(wall.items(), start=0):
        height = dims.get("height", "Not available")
    return height


def wall_format4sides(wall):
    wall_format = {}
    axis = ""
    for index, (wall, dims) in enumerate(wall.items(), start=0):
        width = dims.get("width", "Not available")
        depth = dims.get("depth", "Not available")
        height = dims.get("height", "Not available")
        if index % 2 == 0:
            axis = "y"
        else:
            axis = "x"
        if index + 1 in [2, 3]:
            wall_format[index + 1] = {
                "axis": axis,
                "width": width + height,
                "height": depth + height + 10,
            }
        elif index + 1 in [4]:
            wall_format[index + 1] = {
                "axis": axis,
                "width": width + (height * 2),
                "height": depth + height + 10,
            }
        else:
            wall_format[index + 1] = {
                "axis": axis,
                "width": width,
                "height": depth + height + 10,
            }
        heighttotal = depth + height + 10
    return wall_format, heighttotal

def wallmaker(wall):
    x_values = [-925, 25, 1330, 1225, 625]  # Example X positions
    z_values = [1050, 450, -150, -750, -975]  # Example Z positions
    y_value = 50  # Constant Y position

    # List to store generated coordinates
    data = []

    # Generate coordinates using nested loops
    for z in z_values:  # Loop through Z-axis (height)
        for x in x_values:  # Loop through X-axis
            point_name = f"TMP1S2x{len(data) + 1}"  # Auto-generate name
            data.append({"Point Name": point_name, "X (mm)": x, "Y (mm)": y_value, "Z (mm)": z})

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Save to CSV for external use
    df.to_csv("generated_coordinates.csv", index=False)

    # Plotting the generated coordinates
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(df["X (mm)"], df["Y (mm)"], df["Z (mm)"], c="red", marker="o")

    # Label each point
    for i in range(len(df)):
        ax.text(df["X (mm)"][i], df["Y (mm)"][i], df["Z (mm)"][i], df["Point Name"][i])

    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_zlabel("Z (mm)")
    ax.set_title("Auto-generated TMP1S2 Coordinates")

    # Show plot
