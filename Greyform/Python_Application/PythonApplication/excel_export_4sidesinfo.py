import pandas as pd
import ifcopenshell.util.element as Element
from ifcopenshell.util.placement import get_local_placement, get_axis2placement
import PythonApplication.arraystorage as storingelement
import numpy as np


# export excel sheet
class Exportexcelinfo(object):
    def __init__(
        self,
        file,
        class_type,
        wall_dimensions,
        floor,
        offset,
        wall_finishes_dimensions,
        floor_offset,
        floor_height,
        wall_finishes_offset,
    ):
        # starting initialize
        super().__init__()
        self.file = file
        self.wall_dimensions = wall_dimensions
        self.floor = floor
        self.stagecategory = storingelement.stagecatergorize(self.file)
        self.wallformat, self.heighttotal = storingelement.wall_format4sides(
            self.wall_dimensions
        )
        self.addranges()
        try:
            data = self.get_objects_data_by_class(file, class_type)
            attributes = [
                "Stage",
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
                "Diameter",
            ]
            (
                self.wall_legend,
                self.pen_column,
                self.pin_id_column,
                self.wall_600x600mm,
                self.wall_name,
                self.indexwall,
            ) = storingelement.add_legends()
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
            dataframe["Unnamed : 9"] = dataframe.apply(self.setunwantedpos, axis=1)
            dataframe["Shape type"] = dataframe.apply(self.add_markers, axis=1)
            dataframe[
                ["Position X (m)", "Position Y (m)", "Position Z (m)", "Diameter"]
            ] = dataframe.apply(self.determine_pipes_pos, axis=1)
            dataframe["Wall Number"] = dataframe.apply(self.determine_walls, axis=1)
            dataframe[["Wall Number", "Orientation"]] = dataframe.apply(
                self.itemposition, axis=1
            )
            dataframe[["Width", "Height"]] = dataframe.apply(
                self.determinewallbasedonwidthandheight, axis=1
            )
            dataframe["Wall Number"] = dataframe.apply(self.wall_increment, axis=1)
            dataframe["Stage"] = dataframe.apply(self.applystage, axis=1)
            stages = sorted(
                dataframe["Stage"].unique(), key=lambda x: (x == "Obstacles", x)
            )
            dataframe = dataframe[dataframe["Wall Number"] != 6]
            file_name = f"exporteddatass4sides.xlsx"
            with pd.ExcelWriter(file_name) as writer:
                "stage 1, stage 2 , stage 3 , obstacle"
                for object_class in stages:
                    df_class = dataframe[dataframe["Stage"] == object_class]
                    df_class = df_class.drop(["Stage"], axis=1)
                    df_class.to_excel(writer, sheet_name=object_class)
                    worksheet = writer.sheets[object_class]
                    self.apply_rotation_to_markers(worksheet, df_class)
        except Exception as e:
            self.log_error(f"Failed to write Excel file: {e}")

    def addranges(self):
        current_y = 0
        current_x = 0
        max_y = self.floor[1]  # Maximum Y position based on the image
        max_x = self.floor[0]  # Maximum X position based on the image

        for wall_id, wall in self.wallformat.items():
            if "pos_y_range" not in wall or wall["pos_y_range"] is None:
                wall["pos_y_range"] = (0, 0)

            if "pos_x_range" not in wall or wall["pos_x_range"] is None:
                wall["pos_x_range"] = (0, 0)
            if wall["axis"] == "y":  # Wall along the Y-axis
                # Y-axis walls increase current_y
                if wall_id == 1:  # Specific for Wall 1
                    wall["pos_x_range"] = (0, 50)
                    wall["pos_y_range"] = (0, max_y)
                elif wall_id == 3:  # Specific for wall 3
                    wall["pos_x_range"] = (self.floor[1] - 50, self.floor[1])
                    wall["pos_y_range"] = (0, self.floor[1])
                else:
                    wall["pos_x_range"] = (0, max_x)
                    wall["pos_y_range"] = (current_y, current_y + self.floor[0])
            elif wall["axis"] == "x":  # Wall along the X-axis
                # X-axis walls increase current_x
                if wall_id == 2:  # Specific for Wall 2
                    wall["pos_x_range"] = (0, wall["width"])
                    wall["pos_y_range"] = (
                        max_y - self.wallformat[3]["width"] + 50,
                        max_y,
                    )
                elif wall_id == 4:  # Specific for Wall 4
                    wall["pos_x_range"] = (0, max_x)
                    wall["pos_y_range"] = (max_y - 50, max_y)
                else:
                    wall["pos_x_range"] = (current_x, current_x + max_x)
                    wall["pos_y_range"] = (0, max_y)
            wall["pos_x_range"] = (
                max(0, wall["pos_x_range"][0]),
                min(max_x, wall["pos_x_range"][1]),
            )
            wall["pos_y_range"] = (
                max(0, wall["pos_y_range"][0]),
                min(max_y, wall["pos_y_range"][1]),
            )

    def itemposition(self, row):
        register = row["Unnamed : 9"]
        walls = 0
        if register != "Unregistered":
            for index, (wall, data) in enumerate(self.wallformat.items()):
                if (
                    data["pos_x_range"][0]
                    <= row["Position X (m)"]
                    <= data["pos_x_range"][1]
                    and data["pos_y_range"][0]
                    <= row["Position Y (m)"]
                    <= data["pos_y_range"][1]
                    and 70 <= row["Position Z (m)"] <= data["height"]
                ):
                    orientation = self.determine_orientation(
                        row["Position X (m)"],
                        row["Position Y (m)"],
                        row["Position Z (m)"],
                        wall,
                    )
                    return pd.Series([wall, orientation])
            if row["Position Z (m)"] <= 70:
                walls = 5
                return pd.Series([walls, ""])
            elif (
                row["Position Z (m)"] >= self.heighttotal - 60
                and row["Position Z (m)"] <= self.heighttotal
            ):
                walls = 6
                return pd.Series([walls, ""])
        return pd.Series([row["Wall Number"], ""])

    def determine_orientation(self, posx, posy, posz, wallnum):
        orientation = 0
        for index, (wall, bounds) in enumerate(self.wallformat.items()):
            if bounds["axis"] == "x" and index + 1 == wallnum:
                if posx <= bounds["width"] / 2 and posz >= bounds["height"] / 2:
                    orientation = 1
                elif (
                    posx >= bounds["width"] / 2
                    and posz >= bounds["height"] / 2
                    and posx <= bounds["width"]
                    and posz <= bounds["height"]
                ):
                    orientation = 2
                elif posx <= bounds["width"] / 2 and posz <= bounds["height"] / 2:
                    orientation = 3
                elif (
                    posx >= bounds["width"] / 2
                    and posz <= bounds["height"] / 2
                    and posx <= bounds["width"]
                ):
                    orientation = 4
            elif bounds["axis"] == "y" and index + 1 == wallnum:
                if posy <= bounds["width"] / 2 and posz >= bounds["height"] / 2:
                    orientation = 1
                elif (
                    posy >= bounds["width"] / 2
                    and posz >= bounds["height"] / 2
                    and posy <= bounds["width"]
                    and posz <= bounds["height"]
                ):
                    orientation = 2
                elif posy <= bounds["width"] / 2 and posz <= bounds["height"] / 2:
                    orientation = 3
                elif (
                    posy >= bounds["width"] / 2
                    and posz <= bounds["height"] / 2
                    and posy <= bounds["width"]
                ):
                    orientation = 4
        return orientation

    def setunwantedpos(self, row):
        name = row["Point number/name"]
        if (
            "CP" in name
            or "LP" in name
            or "SP" in name
            or "TMP" in name
            or "Floor" in name
            or "Ceiling" in name
            or "Basic Wall:BSS.50" in name
        ):
            return "Unregistered"
        return ""

    def applystage(self, row):
        stage = ""
        stagenum = ""
        name = row["Point number/name"]
        if self.wall_name in name:
            if self.indexwall < len(self.wall_600x600mm):
                stagenum = self.stagenumber(
                    self.wall_600x600mm[self.indexwall]["Pin ID"]
                )
        for data_legend in self.wall_legend:
            data_pen_name = data_legend.get(self.pen_column)
            data_pin_id = data_legend.get(self.pin_id_column)
            if data_pen_name in name:
                stagenum = self.stagenumber(data_pin_id)
        if "CP" in name or "LP" in name or "SP" in name or "TMP" in name:
            stagenum = self.stagenumber(name)
        for stage, names in self.stagecategory.items():
            for namesatge in names:
                if name == namesatge:
                    return stage
        if stagenum:
            stage = f"Stage {stagenum}"
        else:
            stage = "Obstacles"
        return stage

    def stagenumber(self, name):
        if "CP" in name:
            index = name.index("CP") + 4
            if index < len(name) and name[index].isdigit():
                return int(name[index])
        if "LP" in name:
            index = name.index("LP") + 4
            if index < len(name) and name[index].isdigit():
                return int(name[index])
        if "SP" in name:
            index = name.index("SP") + 4
            if index < len(name) and name[index].isdigit():
                return int(name[index])
        if "TMP" in name:
            index = name.index("TMP") + 5
            if index < len(name) and name[index].isdigit():
                return int(name[index])

    # pipes insertion with ifccratesionpoint
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
                                        radius = round(radius, 1)
                                        diameter = radius * 2
                                        if center.is_a("IfcCartesianPoint"):
                                            center_coords = center.Coordinates
                                        return pd.Series(
                                            [
                                                abs(int(round(center_coords[0]))),
                                                abs(int(round(center_coords[1]))),
                                                abs(int(round(center_coords[2]))),
                                                diameter,
                                            ]
                                        )
                                    if profile.is_a("IfcArbitraryClosedProfileDef"):
                                        outer_curve = profile.OuterCurve
                                        center = item.Position.Location
                                        center_coords = center.Coordinates
                                        if outer_curve.is_a("IfcPolyLine"):
                                            diameterspoint = []
                                            diametersegmentpoints = [
                                                p.Coordinates
                                                for p in outer_curve.Points
                                                if p.is_a("IFCCartesianPoint")
                                            ]
                                            diameterspoint.extend(diametersegmentpoints)
                                            if diameterspoint:
                                                x_values = [
                                                    p[0] for p in diameterspoint
                                                ]
                                                diameter_x = max(x_values) - min(
                                                    x_values
                                                )
                                                return pd.Series(
                                                    [
                                                        abs(
                                                            int(round(center_coords[0]))
                                                        ),
                                                        abs(
                                                            int(round(center_coords[1]))
                                                        ),
                                                        abs(
                                                            int(round(center_coords[2]))
                                                        ),
                                                        round(diameter_x, 1),
                                                    ]
                                                )
        elements = self.file.by_type("IfcRectangleProfileDef")
        for element in elements:
            if "Shower Ledge" in element and "Shower Ledge" in name:
                for use in self.file.get_inverse(element):
                    placement = use.Position
                    coords = placement.Location.Coordinates
                    return pd.Series(
                        [
                            abs(int(round(coords[0]))),
                            abs(int(round(coords[1]))),
                            abs(int(round(coords[2]))),
                            row["Diameter"],
                        ]
                    )
        openingelems = self.file.by_type("IFCOpeningElement")
        for openingelem in openingelems:
            if name in openingelem and "Basic Wall:BSS" in name:
                if openingelem.Representation:
                    for representation in openingelem.Representation.Representations:
                        for item in representation.Items:
                            center = item.Position.Location
                            center_coords = center.Coordinates
                            return pd.Series(
                                [
                                    abs(int(round(center_coords[0]))),
                                    abs(int(round(center_coords[1]))),
                                    abs(int(round(center_coords[2]))),
                                    row["Diameter"],
                                ]
                            )
        doorelems = self.file.by_type("IFCDoor")
        for doorelem in doorelems:
            if name in doorelem and "BSS.Shower Glass Door" in name:
                if doorelem.ObjectPlacement:
                    placement = doorelem.ObjectPlacement
                    while (
                        hasattr(placement, "PlacementRelTo")
                        and placement.PlacementRelTo
                    ):
                        placement = placement.PlacementRelTo
                        if hasattr(placement, "RelativePlacement"):
                            location = placement.RelativePlacement.Location
                            coords = location.Coordinates
                            return pd.Series(
                                [
                                    abs(int(round(coords[0]))),
                                    abs(int(round(coords[1]))),
                                    abs(int(round(coords[2]))),
                                    row["Diameter"],
                                ]
                            )
        return pd.Series(
            [
                row["Position X (m)"],
                row["Position Y (m)"],
                row["Position Z (m)"],
                row["Diameter"],
            ]
        )

    def determine_walls(self, row):
        for index, (wall, dims) in enumerate(self.wall_dimensions.items(), start=0):
            if "Basic Wall:BSS.50" in wall and wall == row["Point number/name"]:
                return index + 1
        return row["Wall Number"]

    def wall_increment(self, row):
        if row["Wall Number"] == 4:
            return 1
        elif row["Wall Number"] < 4:
            return row["Wall Number"] + 1
        return row["Wall Number"]

    # get wall height and width
    def determinewallbasedonwidthandheight(self, row):
        for index, (wall, dims) in enumerate(self.wall_dimensions.items(), start=0):
            if (index + 1) == row["Wall Number"]:
                width = dims.get("width", "Not available")
                depth = dims.get("depth", "Not available")
                height = dims.get("height", "Not available")
                if row["Wall Number"] in [2, 3]:
                    return pd.Series([width + height, depth + height + 10])
                if index + 1 == len(self.wall_dimensions):
                    return pd.Series([width + (height * 2), depth + height + 10])
                return pd.Series([width, depth + height + 10])
            if row["Wall Number"] == 5 or row["Wall Number"] == 6:
                height = dims.get("height", "Not available")
                return pd.Series([self.floor[0], self.floor[2]])
        return pd.Series([0, 0])

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
            level_name = ""
            if hasattr(object, "ContainedInStructure"):
                for rel in object.ContainedInStructure:
                    if rel.RelatingStructure and hasattr(rel.RelatingStructure, "Name"):
                        level_name = rel.RelatingStructure.Name
            if "CEILING" in level_name:
                continue
            objects_data.append(
                {
                    "Stage": "",
                    "Marking type": object.is_a(),
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
                    "Diameter": "",
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
        wallnum = 5
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
        if "Floor:BSS.60" in name or "Celling" in name:
            wallnum = 6
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
