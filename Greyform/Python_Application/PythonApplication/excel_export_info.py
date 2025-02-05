import pandas as pd
import ifcopenshell.util.element as Element
from ifcopenshell.util.placement import get_local_placement, get_axis2placement
import PythonApplication.arraystorage as storingelement
import ifcopenshell
import numpy as np
import math


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
        self.floorheight = offset
        self.flooroffset = floor_offset
        self.floor_height = floor_height
        self.wall_finishes_dimensions = wall_finishes_dimensions
        self.wall_finishes_offset = wall_finishes_offset
        self.stagecategory = storingelement.stagecatergorize(self.file)
        self.wallformat, self.heighttotal, self.wall_height = (
            storingelement.wall_format(self.wall_dimensions)
        )
        self.wall_finishes_height = storingelement.wall_format_finishes(
            self.wall_finishes_dimensions
        )
        self.spacing = "\n"
        self.addranges()
        self.meterline = 1000
        self.wallformat = {
            key + 1 if key < 6 else 1: value for key, value in self.wallformat.items()
        }
        self.wallformat = dict(sorted(self.wallformat.items()))
        try:
            data = self.get_objects_data_by_class(file, class_type)
            attributes = [
                "Stage",
                "Marking type",
                "Point number/name",
                "Position X (mm)",
                "Position Y (mm)",
                "Position Z (mm)",
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
                ["Position X (mm)", "Position Y (mm)", "Position Z (mm)", "Diameter"]
            ] = dataframe.apply(self.determine_pipes_pos, axis=1)
            dataframe[
                [
                    "Position X (mm)",
                    "Position Y (mm)",
                    "Position Z (mm)",
                ]
            ] = dataframe.apply(self.refreshwallfinishespoint, axis=1)
            dataframe["Wall Number"] = dataframe.apply(self.determine_walls, axis=1)
            dataframe["Wall Number"] = dataframe.apply(self.itemposition, axis=1)
            dataframe[
                [
                    "Width",
                    "Height",
                    "Position X (mm)",
                    "Position Y (mm)",
                    "Position Z (mm)",
                ]
            ] = dataframe.apply(self.determinewallbasedonwidthandheight, axis=1)
            dataframe[
                [
                    "Position X (mm)",
                    "Position Y (mm)",
                    "Position Z (mm)",
                ]
            ] = dataframe.apply(self.applywallpoints, axis=1)
            dataframe[["Stage", "Marking type"]] = dataframe.apply(
                self.applystage, axis=1
            )
            stages = sorted(
                dataframe["Stage"].unique(), key=lambda x: (x == "Obstacles", x)
            )
            dataframe["Unnamed : 9"] = ""
            if "Obstacles" not in stages:
                stages.append("Obstacles")
            dataframe = dataframe[(dataframe["Wall Number"] != 8)].sort_values(
                by="Wall Number"
            )
            dataframe.loc[dataframe["Wall Number"] == 7, "Wall Number"] = "F"
            file_name = f"exporteddatassss(draft(changes)).xlsx"
            print(self.wallformat)
            with pd.ExcelWriter(file_name) as writer:
                "stage 1, stage 2 , stage 3 , obstacle"
                for object_class in stages:
                    if object_class in dataframe["Stage"].values:
                        df_class = dataframe[dataframe["Stage"] == object_class]
                    else:
                        df_class = pd.DataFrame(columns=attributes)
                    df_class = df_class.drop(["Stage"], axis=1)
                    df_class.to_excel(writer, sheet_name=object_class)
                    worksheet = writer.sheets[object_class]
                    self.apply_rotation_to_markers(worksheet, df_class)
        except Exception as e:
            self.log_error(f"Failed to write Excel file: {e}")

    def refreshwallfinishespoint(self, row):
        name = row["Point number/name"]
        if "Basic Wall:BSS.20mm Wall Finishes (600x600mm)" in name:
            for wall_name, dims in self.wall_finishes_offset.items():
                if wall_name in name:
                    width = dims.get("width", "Not available")
                    depth = dims.get("depth", "Not available")
                    height = dims.get("height", "Not available")
                    return pd.Series([width, height, depth])
        return pd.Series(
            [row["Position X (mm)"], row["Position Y (mm)"], row["Position Z (mm)"]]
        )

    def applywallpoints(self, row):
        wall_number = row["Wall Number"]
        positionx = row["Position X (mm)"]
        positiony = row["Position Y (mm)"]
        positionz = row["Position Z (mm)"]
        name = row["Point number/name"]
        posy = 0
        posx = 0
        for wall_id, wall in self.wallformat.items():
            if wall_number == wall_id:
                if wall["axis"] == "y":
                    internaldimensionx = self.floor[0]
                    center_x = internaldimensionx / 2
                    internaldimensiony = self.floor[1]
                    posy = internaldimensiony / 2
                    center_z = self.centerlinez()
                    if center_x < positionx and internaldimensionx > positionx:
                        startingrange = wall["pos_y_range"][0]
                        endrange = wall["pos_y_range"][1]
                        robotposy = (
                            positiony - startingrange - ((endrange - startingrange) / 2)
                        )
                        print(name)
                        print(f"Wall {wall} is a potential match.")
                        print(startingrange)
                        print(endrange)
                        print(robotposy)
                        return pd.Series(
                            [
                                positionx,
                                robotposy,
                                positionz - center_z + (self.floorheight),
                            ]
                        )
                    else:
                        if 0 < positiony - posy:
                            return pd.Series(
                                [
                                    positionx,
                                    -abs(positiony - posy),
                                    positionz - center_z + (self.floorheight),
                                ]
                            )
                        else:
                            return pd.Series(
                                [
                                    positionx,
                                    abs(positiony - posy),
                                    positionz - center_z + (self.floorheight),
                                ]
                            )
                else:
                    center_z = self.centerlinez()
                    internaldimensionx = self.floor[0]
                    internaldimensiony = self.floor[1]
                    posx = internaldimensionx / 2
                    posy = internaldimensiony / 2
                    if posy < positiony and internaldimensiony > positiony:
                        return pd.Series(
                            [
                                positionx - posx,
                                positiony,
                                positionz - center_z + (self.floorheight),
                            ]
                        )
                    else:
                        if 0 < positionx - posx:
                            return pd.Series(
                                [
                                    -abs(positionx - posx),
                                    positiony,
                                    positionz - center_z + (self.floorheight),
                                ]
                            )
                        else:
                            return pd.Series(
                                [
                                    abs(positionx - posx),
                                    positiony,
                                    positionz - center_z + (self.floorheight),
                                ]
                            )
        if wall_number == 7:
            internaldimensionx = self.floor[0]
            wallcenterline_y = self.floor[1] - self.meterline
            center_z = (self.floorheight - (self.flooroffset * 2)) + self.meterline
            return pd.Series(
                [
                    positionx - (internaldimensionx / 2),
                    positiony - wallcenterline_y,
                    positionz,
                ]
            )
        return pd.Series([positionx, positiony, positionz])

    def centerlinez(self):
        return (
            self.floorheight - (self.flooroffset + (self.floor_height))
        ) + self.meterline

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
                    wall["pos_x_range"] = (
                        current_x,
                        self.wall_finishes_height + (self.wall_height / 2),
                    )
                    wall["pos_y_range"] = (0, self.floor[0])
                elif wall_id == 3:  # Specific for wall 3
                    wall["pos_x_range"] = (
                        self.floor[1] - self.wall_height,
                        self.floor[1],
                    )
                    wall["pos_y_range"] = (
                        self.floor[1]
                        - self.wallformat[wall_id]["width"]
                        - (self.wall_height * 2)
                        - (self.wall_finishes_height * 2),
                        self.floor[1],
                    )
                elif wall_id == 5:  # Specific for wall 5
                    wall["pos_x_range"] = (self.floor[0] - self.wall_height * 2, max_x)
                    wall["pos_y_range"] = (
                        0,
                        max_y - self.wallformat[wall_id - 2]["width"],
                    )
                else:
                    wall["pos_x_range"] = (0, max_x)
                    wall["pos_y_range"] = (current_y, current_y + self.floor[0])
            elif wall["axis"] == "x":  # Wall along the X-axis
                # X-axis walls increase current_x
                if wall_id == 2:  # Specific for Wall 2
                    wall["pos_x_range"] = (0, wall["width"])
                    wall["pos_y_range"] = (
                        max_y
                        - self.wallformat[wall_id + 1]["width"]
                        + self.wall_height,
                        max_y,
                    )
                elif wall_id == 4:  # Specific for Wall 4
                    wall["pos_x_range"] = (
                        self.floor[1] - self.wall_height * 2,
                        max_x - self.wall_height - (self.wall_finishes_height * 2),
                    )
                    wall["pos_y_range"] = (
                        max_y
                        - self.wallformat[wall_id - 1]["width"]
                        - self.wall_height * 2
                        - self.wall_finishes_height,
                        max_y - self.wallformat[wall_id - 1]["width"],
                    )
                elif wall_id == 6:  # Wall 6
                    wall["pos_x_range"] = (
                        self.wall_finishes_height + self.wall_height,
                        max_x,
                    )  # Corrected range
                    wall["pos_y_range"] = (current_y, self.wall_height)
                else:
                    wall["pos_x_range"] = (
                        current_x,
                        current_x
                        + max_x
                        - self.wall_finishes_height
                        - self.wall_height,
                    )
                    wall["pos_y_range"] = (current_y, max_y)
            wall["pos_x_range"] = (
                max(current_x, wall["pos_x_range"][0]),
                min(max_x, wall["pos_x_range"][1]),
            )
            wall["pos_y_range"] = (
                max(0, wall["pos_y_range"][0]),
                min(max_y, wall["pos_y_range"][1]),
            )

    def itemposition(self, row):
        register = row["Unnamed : 9"]
        name = row["Point number/name"]
        walls = 0
        if register != "Unregistered":
            for index, (wall, data) in enumerate(self.wallformat.items()):

                transformed_x = row["Position X (mm)"] - (self.wall_height / 2)
                transformed_y = row["Position Y (mm)"] - self.wall_height
                transformed_z = row["Position Z (mm)"]

                x_pass = data["pos_x_range"][0] < transformed_x < data["pos_x_range"][1]
                y_pass = (
                    data["pos_y_range"][0] <= transformed_y < data["pos_y_range"][1]
                )
                z_pass = transformed_z >= -abs(self.floorheight - self.wall_height)
                if x_pass and y_pass and z_pass:
                    return wall
            if row["Position Z (mm)"] < -abs(self.floorheight - self.wall_height):
                walls = 7
                return walls
            elif self.heighttotal - 60 <= row["Position Z (mm)"] <= self.heighttotal:
                walls = 8
                return walls
        return row["Wall Number"]

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
        markingtypes = ["Pipes", "Tile", "Fitting"]
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
                    markingtype = self.changemarkingtype(stage, markingtypes)
                    return pd.Series([stage, markingtype])
        if stagenum:
            stage = f"Stage {stagenum}"
        else:
            stage = "Obstacles"
        markingtype = self.changemarkingtype(stage, markingtypes)
        return pd.Series([stage, markingtype])

    def changemarkingtype(self, stage, markingtypes):
        if stage == "Stage 1":
            return markingtypes[0]
        elif stage == "Stage 2":
            return markingtypes[1]
        elif stage == "Stage 3":
            return markingtypes[2]
        else:
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
        type = row["Marking type"]
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
                                        if outer_curve.is_a("IfcCompositeCurve"):
                                            diameterspoint = []
                                            for segment in outer_curve.Segments:
                                                parent_curve = segment.ParentCurve
                                                if parent_curve.is_a("IfcPolyline"):
                                                    diametersegmentpoints = [
                                                        p.Coordinates
                                                        for p in parent_curve.Points
                                                        if p.is_a("IFCCartesianPoint")
                                                    ]
                                                    diameterspoint.extend(
                                                        diametersegmentpoints
                                                    )
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
                                                        diameter_x,
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
                row["Position X (mm)"],
                row["Position Y (mm)"],
                row["Position Z (mm)"],
                row["Diameter"],
            ]
        )

    def determine_walls(self, row):
        for index, (wall, dims) in enumerate(self.wall_dimensions.items(), start=0):
            if "Basic Wall:BSS.50" in wall and wall == row["Point number/name"]:
                return index + 1
        return row["Wall Number"]

    def wall_increment(self, row):
        name = row["Point number/name"]
        if row["Wall Number"] == 6:
            if all(keyword not in name for keyword in ["CP", "LP", "SP", "TMP"]):
                return 1
        elif row["Wall Number"] < 6:
            if all(keyword not in name for keyword in ["CP", "LP", "SP", "TMP"]):
                return row["Wall Number"] + 1
        return row["Wall Number"]

    # get wall height and width
    def determinewallbasedonwidthandheight(self, row):
        name = row["Point number/name"]
        for index, (wall, dims) in enumerate(self.wallformat.items(), start=0):
            if (index + 1) == row["Wall Number"]:
                width = dims.get("width", "Not available")
                height = dims.get("height", "Not available")
                return pd.Series(
                    [
                        width,
                        height,
                        row["Position X (mm)"],
                        row["Position Y (mm)"],
                        row["Position Z (mm)"],
                    ]
                )
            if row["Wall Number"] == 7:
                height = dims.get("height", "Not available")
                if "Floor" in name:
                    return pd.Series(
                        [
                            self.floor[0],
                            self.floor[1],
                            (self.floor[0]) / 2,
                            self.floor[1] / 2,
                            0,
                        ]
                    )
                return pd.Series(
                    [
                        self.floor[0],
                        self.floor[1],
                        row["Position X (mm)"],
                        row["Position Y (mm)"],
                        row["Position Z (mm)"],
                    ]
                )
            elif row["Wall Number"] == 8:
                height = dims.get("height", "Not available")
                if "Floor" in name:
                    return pd.Series(
                        [
                            self.floor[0],
                            self.floor[1],
                            (self.floor[0]) / 2,
                            self.floor[1] / 2,
                            height,
                        ]
                    )
                return pd.Series(
                    [
                        self.floor[0],
                        self.floor[1],
                        row["Position X (mm)"],
                        row["Position Y (mm)"],
                        row["Position Z (mm)"],
                    ]
                )
        return pd.Series(
            [
                0,
                0,
                row["Position X (mm)"],
                row["Position Y (mm)"],
                row["Position Z (mm)"],
            ]
        )

    # get object data based on class using ifc
    def get_objects_data_by_class(self, file, class_type):
        objects_data = []
        self.pset_attributes = set()
        objects = file.by_type(class_type)
        for object in objects:
            storey = None
            if object.is_a() != "IfcOpeningElement":
                wall_number = object.Tag if object.Tag else ""
                name = object.Name if object.Name else ""
                psets = Element.get_psets(object, psets_only=True)
                self.add_pset_attributes(psets)
                qtos = Element.get_psets(object, qtos_only=True)
                self.add_pset_attributes(qtos)
                placement_matrix = get_local_placement(object.ObjectPlacement)
                # Extract Vertices of Elements
                x, y, z = (0, 0, 0)
                scale_factor = 1000.0
                scaled_grouped_verts = []
                if object.Representation is not None:
                    settings = ifcopenshell.geom.settings()
                    shape = ifcopenshell.geom.create_shape(settings, object)
                    verts = shape.geometry.verts
                    grouped_verts = [
                        [verts[i], verts[i + 1], verts[i + 2]]
                        for i in range(0, len(verts), 3)
                    ]
                    scaled_grouped_verts = np.array(grouped_verts) * scale_factor
                    scaled_grouped_verts = np.round(scaled_grouped_verts).astype(int)
                if object.ObjectPlacement:
                    placement = object.ObjectPlacement.RelativePlacement
                    if placement and placement.Location:
                        x, y, z = placement.Location.Coordinates
                for rel in object.ContainedInStructure:
                    if rel.RelatingStructure.is_a("IfcBuildingStorey"):
                        storey = rel.RelatingStructure
                if storey and "Ceiling" in storey.Name:
                    continue
                if "CP" in name:
                    z = abs(z)
                objects_data.append(
                    {
                        "Stage": "",
                        "Marking type": object.is_a(),
                        "Point number/name": name,
                        "Position X (mm)": int(round(x)),
                        "Position Y (mm)": int(round(y)),
                        "Position Z (mm)": int(round(z)),
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

    def add_pset_attributes(self, psets):
        for pset_name, pset_data in psets.items():
            for property_name in pset_data.keys():
                self.pset_attributes.add(f"{pset_name}.{property_name}")

    # error will send into the error log text
    def log_error(self, message):
        with open("error_log.txt", "a") as log_file:
            log_file.write(message + "\n")

    def log_text(self, message):
        with open("log.txt", "a") as log_file:
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
        wallnum = 7
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
            wallnum = 8
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
