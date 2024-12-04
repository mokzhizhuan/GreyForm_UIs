import pandas as pd
import ifcopenshell
import ifcopenshell.geom
import meshio
import multiprocessing
import ifcopenshell.util.element as Element
from ifcopenshell.util.placement import get_local_placement
import numpy as np
import math


# export excel sheet
class Exportexcelinfo(object):
    def __init__(self, file, class_type, wall_dimensions, widtharea, heightarea):
        # starting initialize
        super().__init__()
        self.file = file
        self.class_type = class_type
        self.wall_dimensions = wall_dimensions
        self.widtharea = widtharea
        self.heightarea = heightarea
        try:
            data = self.get_objects_data_by_class(file, class_type)
            attributes = [
                "Class",
                "Marking type",
                "Point number/name",
                "Position X (m)",
                "Position Y (m)",
                "Position Z (m)",
                "Wall Number",
                "Shape type",
                "Status",
                "Quadrant",
                "Unnamed : 9",
                "Width",
                "Height",
                "Orientation",
            ]
            self.add_legends()
            pandas_data = []
            for object_data in data:
                row = []
                for attribute in attributes:
                    value = self.get_attribute_value(object_data, attribute)
                    row.append(value)
                pandas_data.append(tuple(row))
            dataframe = pd.DataFrame.from_records(pandas_data, columns=attributes)
            dataframe["Wall Number"] = dataframe.apply(
                self.determine_wall_number, axis=1
            )
            dataframe["Shape type"] = dataframe.apply(self.add_markers, axis=1)
            dataframe[["Position X (m)", "Position Y (m)", "Position Z (m)"]] = (
                dataframe.apply(self.determine_pipes_pos, axis=1)
            )
            dataframe[["Width", "Height"]] = dataframe.apply(
                self.determinewallbasedonwidthandheight, axis=1
            )
            file_name = f"exporteddatass.xlsx"
            with pd.ExcelWriter(file_name) as writer:
                for object_class in dataframe["Class"].unique():
                    df_class = dataframe[dataframe["Class"] == object_class]
                    df_class = df_class.drop(["Class"], axis=1)
                    df_class.to_excel(writer, sheet_name=object_class)
                    worksheet = writer.sheets[object_class]
                    self.apply_rotation_to_markers(worksheet, df_class)
        except Exception as e:
            self.log_error(f"Failed to write Excel file: {e}")

    def determine_pipes_pos(self, row):
        name = row["Point number/name"]
        pipes = self.file.by_type("IFCFlowSegment")
        for pipe in pipes:
            if name in pipe:
                if pipe.Representation:
                    for representation in pipe.Representation.Representations:
                        if hasattr(representation, "Items"):
                            for item in representation.Items:
                                if item.is_a("IfcExtrudedAreaSolid"):
                                    profile = item.SweptArea
                                    if profile.is_a("IfcCircleProfileDef"):
                                        center = item.Position.Location
                                        radius = profile.Radius
                                        radius = round(radius,1)
                                        if center.is_a("IfcCartesianPoint"):
                                            center_coords = center.Coordinates
                                        diameterpoint = []
                                        diameterpoint.append([center_coords[0]+radius,center_coords[1],center_coords[2]])
                                        diameterpoint.append([center_coords[0]-radius,center_coords[1],center_coords[2]])
                                        return pd.Series(
                                            [
                                                abs(int(round(center_coords[0]))),
                                                abs(int(round(center_coords[1]))),
                                                abs(int(round(center_coords[2]))),
                                            ]
                                        )
                                    if profile.is_a("IfcArbitraryClosedProfileDef"):
                                        outer_curve = profile.OuterCurve
                                        if outer_curve.is_a("IfcCompositeCurve"):
                                            points = []
                                            for segment in outer_curve.Segments:
                                                parent_curve = segment.ParentCurve
                                                if parent_curve.is_a("IfcPolyline"):
                                                    segment_points = [
                                                        tuple(int(abs(round(coord))) for coord in p.Coordinates)
                                                        for p in parent_curve.Points
                                                        if p.is_a("IFCCartesianPoint")
                                                    ]
                                                    points.extend(segment_points)
                                            if points:
                                                num_points = len(points)
                                                center_x = (
                                                    sum(p[0] for p in points)
                                                    / num_points
                                                )
                                                center_y = (
                                                    sum(p[1] for p in points)
                                                    / num_points
                                                )
                                                center_z = (
                                                    sum(
                                                        p[2] if len(p) > 2 else 0
                                                        for p in points
                                                    )
                                                    / num_points
                                                )
                                                center_x = round(center_x, 6)
                                                center_y = round(center_y, 6)
                                                center_z = round(center_z, 6)
                                                return pd.Series(
                                                    [
                                                        int(abs(round(center_x))),
                                                        int(abs(round(center_y))),
                                                        int(abs(round(center_z))),
                                                    ]
                                                )
        return pd.Series(
            [row["Position X (m)"], row["Position Y (m)"], row["Position Z (m)"]]
        )

    def determinewallbasedonwidthandheight(self, row):
        for index, (wall, dims) in enumerate(self.wall_dimensions.items(), start=0):
            if (index + 1) == row["Wall Number"]:
                width = dims.get("width", "Not available")
                height = dims.get("height", "Not available")
                return pd.Series([width, height])
        if row["Wall Number"] == 7 or row["Wall Number"] == "F":
            return pd.Series([self.widtharea, self.heightarea])
        return pd.Series([0, 0])

    def add_legends(self):
        dataframe_Legend = pd.read_excel(
            "Pin Allocation BOM for PBU_T1a.xlsx", skiprows=2
        )
        self.pen_column = dataframe_Legend.columns[3]
        self.pin_id_column = dataframe_Legend.columns[9]
        dataframe_Legend = dataframe_Legend[[self.pen_column, self.pin_id_column]]
        if (
            self.pen_column in dataframe_Legend.columns
            and self.pin_id_column in dataframe_Legend.columns
        ):
            dataframe_Legend[self.pen_column].fillna("", inplace=True)
            dataframe_Legend[self.pin_id_column].fillna("", inplace=True)
            filtered_dataframe = dataframe_Legend[
                (dataframe_Legend[self.pen_column] != "")
                & (dataframe_Legend[self.pin_id_column] != "")
            ]
            self.wall_legend = filtered_dataframe.to_dict(orient="records")
            self.wall_name = "BSS.20mm Wall Finishes (600x600mm)"
            self.wall_600x600mm = []
            self.indexwall = 0
            self.index = 0
            for data_legend in self.wall_legend:
                data_pen_name = data_legend.get(self.pen_column)
                data_pin_id = data_legend.get(self.pin_id_column)
                if self.wall_name in data_pen_name:
                    self.wall_600x600mm.append(
                        {
                            "Penetration/Fitting/Reference Point Name": data_pen_name,
                            "Pin ID": data_pin_id,
                        }
                    )

    # get object data based on class using ifc
    def get_objects_data_by_class(self, file, class_type):
        objects_data = []
        objects = file.by_type(class_type)
        for object in objects:
            wall_number = object.Tag if object.Tag else ""
            name = object.Name if object.Name else ""
            # Extract Vertices of Elements
            x, y, z = (0, 0, 0)
            if object.ObjectPlacement:
                placement = object.ObjectPlacement.RelativePlacement
                if placement and placement.Location:
                    x, y, z = placement.Location.Coordinates
            objects_data.append(
                {
                    "Class": str(object.is_a()).replace("Ifc", ""),
                    "Marking type": (
                        Element.get_type(object).Name
                        if Element.get_type(object)
                        else object.Name
                    ),
                    "Point number/name": name,
                    "Position X (m)": abs(int(x)),
                    "Position Y (m)": abs(int(y)),
                    "Position Z (m)": abs(int(z)),
                    "Wall Number": str(wall_number),
                    "Shape type": "",
                    "Status": "blank",
                    "Quadrant": 1,
                    "Unnamed : 9": "",
                    "Width": "",
                    "Height": "",
                    "Orientation": "",
                }
            )
        return objects_data

    # error will send into the error log text
    def log_error(self, message):
        with open("error_log.txt", "a") as log_file:
            log_file.write(message + "\n")

    # add marker and store it in the excel data
    def add_markers(self, row):
        if pd.isnull(row["Point number/name"]):
            return "6"
        if row["Point number/name"] and row["Point number/name"].startswith("TMP"):
            if (
                any(char in row["Point number/name"] for char in ["a", "b", "c"])
                and row["Point number/name"][8] == "s"
            ):
                return "T"
            else:
                return "+"
        return "6"

    # convert to other wall number for rotation
    def apply_rotation_to_markers(self, worksheet, df_class):
        marker_col_index = df_class.columns.get_loc("Shape type")
        for row_idx, (name, marker) in enumerate(
            zip(
                df_class["Point number/name"],
                df_class["Shape type"],
            ),
            start=1,
        ):
            if name and name.startswith("TMP") and name[8] == "s" and name[3] == "7":
                print(f"Rotating marker for row {row_idx}: {marker}")
                if "b" in name:
                    marker = 4
                    worksheet.write(row_idx, marker_col_index + 1, marker)
                else:
                    marker = 3
                    worksheet.write(row_idx, marker_col_index + 1, marker)
            else:
                if marker == "T":
                    marker = 2
                    worksheet.write(row_idx, marker_col_index + 1, marker)
                elif marker == "+":
                    marker = 1
                    worksheet.write(row_idx, marker_col_index + 1, marker)
                elif marker == "6":
                    marker = 6
                    worksheet.write(row_idx, marker_col_index + 1, marker)

    # get attribute value for excel data
    def get_attribute_value(self, object_data, attribute):
        if "." not in attribute:
            return object_data[attribute]
        elif "." in attribute:
            pset_name = attribute.split(".", 1)[0]
            prop_name = attribute.split(".", -1)[1]
            if pset_name in object_data["PropertySets"].keys():
                if prop_name in object_data["PropertySets"][pset_name].keys():
                    return object_data["PropertySets"][pset_name][prop_name]
                else:
                    return None
            if pset_name in object_data["QuantitySets"].keys():
                if prop_name in object_data["QuantitySets"][pset_name].keys():
                    return object_data["QuantitySets"][pset_name][prop_name]
                else:
                    return None
        else:
            return None

    # determine wall number based on the exceldata name
    def determine_wall_number(self, row):
        wallnum = "F"
        name = row["Point number/name"]
        if self.wall_name in name:
            if self.indexwall < len(self.wall_600x600mm):
                wallnum = self.wallnumber(self.wall_600x600mm[self.indexwall]["Pin ID"])
                return wallnum
        for data_legend in self.wall_legend:
            data_pen_name = data_legend.get(self.pen_column)
            data_pin_id = data_legend.get(self.pin_id_column)
            if data_pen_name in name:
                wallnum = self.wallnumber(data_pin_id)
                return wallnum
        if "CP" in name or "LP" in name or "SP" in name or "TMP" in name:
            wallnum = self.wallnumber(name)
        return wallnum

    # get wall number form excel data
    def wallnumber(self, name):
        if "CP" in name:
            index = name.index("CP") + 2
            if index < len(name) and name[index].isdigit():
                return int(name[index])
        if "LP" in name:
            index = name.index("LP") + 2
            if index < len(name) and name[index].isdigit():
                return int(name[index])
        if "SP" in name:
            index = name.index("SP") + 2
            if index < len(name) and name[index].isdigit():
                return int(name[index])
        if "TMP" in name:
            index = name.index("TMP") + 3
            if index < len(name) and name[index].isdigit():
                return int(name[index])
