import pandas as pd
from ifcopenshell.util.placement import get_local_placement, get_axis2placement
import PythonApplication.arraystorage as storingelement
import PythonApplication.ifcextractfiles as extractor
import PythonApplication.loadmaintmp as loadTmpMain
import PythonApplication.loadtmpFloor as FloorTMP
import PythonApplication.loadLP as Lpinserter

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
        wall_offset,
        label_map,
        directional_axes_axis,
        Cellingstorey,
        args
    ):
        # starting initialize
        super().__init__()
        self.file = file
        self.args = args
        self.wall_dimensions = wall_dimensions
        self.floor = floor
        self.floorheight = offset
        self.flooroffset = floor_offset
        self.floor_height = floor_height
        self.floor_height = int(self.floor_height)
        self.floor_height = self.floor_height * 2
        self.wall_finishes_dimensions = wall_finishes_dimensions
        self.wall_finishes_offset = wall_finishes_offset
        self.wall_offset = wall_offset
        self.label_map = label_map
        self.directional_axes_axis = directional_axes_axis
        self.stagecategory = storingelement.stagecatergorize(self.file)
        self.axis_widths = {"x": [], "y": []}
        self.wall_finishes_height, self.small_wall_height = (
            storingelement.wall_format_finishes(self.wall_finishes_dimensions)
        )
        self.wallformat, self.heighttotal, self.wall_height = (
            storingelement.wall_format(
                self.wall_dimensions,
                self.floor,
                self.label_map,
                self.wall_finishes_height,
            )
        )
        self.thickness = self.wall_height + self.wall_finishes_height
        self.smallthickness = self.wall_height + self.small_wall_height
        self.wallformat, self.axis_widths = extractor.addranges(
            self.floor,
            self.wall_height,
            self.wall_finishes_height,
            self.label_map,
            self.wallformat,
            self.axis_widths,
            self.directional_axes_axis,
        )
        self.meterline = 1000
        self.wallformat = dict(sorted(self.wallformat.items()))
        self.direction_stack = []
        self.count_plus_y = 0
        self.count_minus_y = 0
        for index, (start, end, direction) in enumerate(self.directional_axes_axis):
            self.direction_stack.append(direction)
            self.count_minus_y = self.direction_stack.count("-Y")
            self.count_plus_y = self.direction_stack.count("+Y")
        try:
            data, verts_data = extractor.get_objects_data_by_class(file, class_type)
            loadTmpMain.loadmainTMP(
                data,
                verts_data,
                Cellingstorey,
                self.thickness,
                self.wall_height,
                self.file,
                self.meterline,
                self.label_map,
                self.wall_finishes_height,
                self.small_wall_height,
                self.wallformat,
                self.axis_widths,
                self.count_minus_y,
                self.count_plus_y,
                self.flooroffset,
                self.args
            )
            datainserter = FloorTMP.loadTMPFloor(
                data,
                verts_data,
                Cellingstorey,
                self.thickness,
                self.wall_height,
                self.meterline,
                self.label_map,
                self.wall_finishes_height,
                self.small_wall_height,
                self.wallformat,
                self.axis_widths,
                self.flooroffset,
                self.args
            )
            data = datainserter.addTMP7()
            datainserterLP = Lpinserter.loadLP(
                data,
                verts_data,
                self.wall_offset,
                self.count_minus_y,
                self.count_plus_y,
                self.args
            )
            data = datainserterLP.loadLP7()
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
            ) = storingelement.add_legends(self.args)
            pandas_data = []
            for object_data in data:
                row = []
                for attribute in attributes:
                    value = extractor.get_attribute_value(object_data, attribute)
                    row.append(value)
                pandas_data.append(tuple(row))
            dataframe = pd.DataFrame.from_records(pandas_data, columns=attributes)
            dataframe["Wall Number"] = dataframe.apply(self.itemposition, axis=1)
            dataframe["Wall Number"] = dataframe.apply(
                self.determine_wall_number, axis=1
            )
            dataframe["Shape type"] = dataframe.apply(self.add_markers, axis=1)
            dataframe[
                [
                    "Width",
                    "Height",
                    "Position X (mm)",
                    "Position Y (mm)",
                    "Position Z (mm)",
                ]
            ] = dataframe.apply(self.determinewallbasedonwidthandheight, axis=1)
            dataframe[["Position X (mm)", "Position Y (mm)", "Position Z (mm)"]] = (
                dataframe.apply(self.applywallpoints, axis=1)
            )
            dataframe[["Stage", "Marking type"]] = dataframe.apply(
                self.applystage, axis=1
            )
            dataframe[["Width", "Height"]] = dataframe.apply(
                self.applyinternalwidth, axis=1
            )
            dataframe = dataframe[dataframe["Stage"] != "Stage 1"]
            startingwall = -abs(self.meterline + (self.flooroffset))
            endingwall = -abs(self.centerlinez() + (self.flooroffset))
            dataframe = dataframe[
                (
                    (dataframe["Wall Number"] == 7)
                ) |
                (
                    (dataframe["Wall Number"] != 7) &
                    (
                        (dataframe["Position Z (mm)"] >= startingwall) |
                        (dataframe["Position Z (mm)"] <= endingwall)
                    )
                )
            ]
            dataframe = dataframe[dataframe["Position Z (mm)"] < Cellingstorey[2]]
            unwanted_names = [
                "Basic Wall",
                "BSS.Gate Valve",
                "Ceiling",
                "THRESHOLD",
                "BSS.Shower",
                "BSS.GESSI.SH",
                "BSS.Vesbo Tee Fiting",
                "BSS.MONIC.BIB TAP",
                "BSS.Bottle Trap",
                "BSS.GESSI,BM",
                "BSS.Shallow",
                "M_Coupling",
            ]
            pattern = "|".join(unwanted_names)
            dataframe = dataframe[
                ~dataframe["Point number/name"].str.contains(
                    pattern, case=False, na=False
                )
            ]
            dataframe = dataframe[
                ~(
                    dataframe["Point number/name"].str.contains(
                        "Floor", case=False, na=False
                    )
                    & (dataframe["Marking type"] == "Tile")
                )
            ]
            stages = sorted(
                dataframe["Stage"].unique(), key=lambda x: (x == "Obstacles", x)
            )
            if "Obstacles" not in stages:
                stages.append("Obstacles")
            dataframe["Unnamed : 9"] = ""
            dataframe = dataframe[dataframe["Wall Number"] != 8].sort_values(
                by="Wall Number"
            )
            dataframe.loc[dataframe["Wall Number"] == 7, "Wall Number"] = "F"
            dataframe[
                [
                    "Position X (mm)",
                    "Position Y (mm)",
                    "Position Z (mm)",
                    "Width",
                    "Height",
                ]
            ] = (
                dataframe[
                    [
                        "Position X (mm)",
                        "Position Y (mm)",
                        "Position Z (mm)",
                        "Width",
                        "Height",
                    ]
                ]
                / 1000
            )
            dataframe.rename(
                columns={
                    "Position X (mm)": "Position X",
                    "Position Y (mm)": "Position Y",
                    "Position Z (mm)": "Position Z",
                    "Point number/name": "Point Name",
                    "Shape type": "Shape Type",
                },
                inplace=True,
            )
            dataframe = dataframe.drop_duplicates(subset=["Point Name"])
            file_name = self.args.output_excel
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
                    extractor.apply_rotation_to_markers(worksheet, df_class)
        except Exception as e:
            extractor.log_error(f"Failed to write Excel file: {e}")

    def applyinternalwidth(self, row):
        width = row["Width"]
        height = row["Height"]
        wall_num = row["Wall Number"]
        x_max, x_min = max(self.axis_widths["x"]), min(self.axis_widths["x"])
        y_max, y_min = max(self.axis_widths["y"]), min(self.axis_widths["y"])
        if width == y_min:
            if (
                width % 10 != 0
                and y_max % 10 != 0
                or (self.small_wall_height <= (self.wall_finishes_height / 2))
            ):
                internal_height = y_max - (self.thickness + self.smallthickness)
                second_internal_height = y_max - y_min - (self.thickness * 2)
                return pd.Series([internal_height - second_internal_height, height])
            else:
                return pd.Series([width, height])
        if width == x_min:
            if (
                width % 10 != 0
                and y_max % 10 != 0
                or (self.small_wall_height <= (self.wall_finishes_height / 2))
            ):
                internal_height = x_max - (self.thickness + self.smallthickness)
                second_internal_height = x_max - x_min - (self.thickness * 2)
                return pd.Series([internal_height - second_internal_height, height])
            else:
                return pd.Series([width, height])
        if width % 10 != 0:
            return pd.Series([(width - (self.thickness + self.smallthickness)), height])
        if wall_num == 7:
            internal_width = 0
            internal_height = 0
            if height % 10 != 0:
                internal_height = height - (self.thickness + self.smallthickness)
            else:
                internal_height = height - (self.thickness * 2)
            if width % 10 != 0:
                internal_width = width - (self.thickness + self.smallthickness)
            else:
                internal_width = width - (self.thickness * 2)
            return pd.Series([internal_width, internal_height])
        return pd.Series([(width - (self.thickness * 2)), height])

    def applywallpoints(self, row):
        wall_number = row["Wall Number"]
        positionx = row["Position X (mm)"]
        positiony = row["Position Y (mm)"]
        positionz = row["Position Z (mm)"]
        center_z = self.centerlinez()
        internaldimensiony = self.floor[1]
        thickness = self.wall_finishes_height + self.wall_height
        small_thickness = self.small_wall_height + self.wall_height
        internaldimensionx = extractor.calculate_internaldimensionx(
            thickness, small_thickness, self.wallformat
        )
        if internaldimensiony != (
            max(self.axis_widths["x"]) - min(self.axis_widths["x"])
        ):
            internaldimensiony = max(self.axis_widths["x"]) - min(self.axis_widths["x"])
        pos_z = positionz - center_z + (self.floorheight) - (self.flooroffset)
        center_x = internaldimensionx / 2
        posy = internaldimensiony / 2
        for wall_id, wall in self.wallformat.items():
            if wall_number == wall_id:
                if wall["axis"] == "y":
                    if wall_id == len(self.wallformat) and self.count_minus_y == 2:
                        pos_z = positionz - center_z + (self.floorheight)
                    elif (
                        wall_id == (len(self.wallformat) / 3) and self.count_plus_y == 2
                    ):
                        pos_z = positionz - center_z + (self.floorheight)
                    robotposy = positiony - posy
                    robotposx = positionx - thickness
                    if self.count_plus_y == 2:
                        if robotposx > center_x:
                            if robotposx >= (
                                internaldimensionx - (thickness * 2)
                            ) and robotposx < (internaldimensionx):
                                robotposx = (
                                    internaldimensionx - (thickness * 2)
                                ) - robotposx
                                return pd.Series([robotposy, robotposx, pos_z])
                        if robotposx > 0:
                            return pd.Series([-abs(robotposy), robotposx, pos_z])
                        else:
                            return pd.Series([abs(robotposy), robotposx, pos_z])
                    else:
                        if robotposx > center_x:
                            return pd.Series([robotposy, robotposx, pos_z])
                        if robotposx > 0:
                            return pd.Series([-abs(robotposy), robotposx, pos_z])
                        else:
                            return pd.Series([abs(robotposy), robotposx, pos_z])
                    return pd.Series([robotposy, robotposx, pos_z])
                elif wall["axis"] == "x":
                    robotposy = positiony - thickness
                    robotposx = positionx - center_x
                    if self.count_plus_y == 2:
                        if robotposy > 0:
                            robotposy = (
                                internaldimensiony - (thickness * 2)
                            ) - robotposy
                            if robotposx > 0:
                                return pd.Series([-abs(robotposx), robotposy, pos_z])
                            else:
                                return pd.Series([abs(robotposx), robotposy, pos_z])
                        return pd.Series([robotposx, robotposy, pos_z])
                    else:
                        if robotposy > 0:
                            robotposy = (
                                internaldimensiony - (thickness * 2)
                            ) - robotposy
                            return pd.Series([robotposx, robotposy, pos_z])
                        if robotposx > 0:
                            return pd.Series([-abs(robotposx), robotposy, pos_z])
                        else:
                            return pd.Series([abs(robotposx), robotposy, pos_z])
        return pd.Series(
            [
                positionx - center_x,
                positiony - posy,
                positionz - self.meterline,
            ]
        )

    def centerlinez(self):
        return (self.floorheight - (self.flooroffset)) + self.meterline

    def itemposition(self, row):
        walls = 0
        for index, (wall, data) in enumerate(self.wallformat.items()):
            transformed_x = row["Position X (mm)"]
            transformed_y = row["Position Y (mm)"]
            transformed_z = row["Position Z (mm)"]
            x_pass = data["pos_x_range"][0] < transformed_x < data["pos_x_range"][1]
            y_pass = data["pos_y_range"][0] <= transformed_y < data["pos_y_range"][1]
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

    def applystage(self, row):
        stage = ""
        stagenum = ""
        markingtypes = ["Pipes", "Tile", "Fitting"]
        name = row["Point number/name"]
        if self.wall_name in name:
            if self.indexwall < len(self.wall_600x600mm):
                stagenum = extractor.stagenumber(
                    self.wall_600x600mm[self.indexwall]["Pin ID"]
                )
        for data_legend in self.wall_legend:
            data_pen_name = data_legend.get(self.pen_column)
            data_pin_id = data_legend.get(self.pin_id_column)
            if data_pen_name in name:
                stagenum = extractor.stagenumber(data_pin_id)
        if "CP" in name or "LP" in name or "SP" in name or "TMP" in name:
            stagenum = extractor.stagenumber(name)
        for stage, names in self.stagecategory.items():
            for namesatge in names:
                if name == namesatge and "BSS.Shallow" not in name:
                    markingtype = extractor.changemarkingtype(stage, markingtypes)
                    return pd.Series([stage, markingtype])
        if "BSS.Shallow" in name:
            stagenum = 3
        if stagenum:
            stage = f"Stage {stagenum}"
        else:
            stage = "Obstacles"
        markingtype = extractor.changemarkingtype(stage, markingtypes)
        return pd.Series([stage, markingtype])

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

    # add marker and store it in the excel data
    def add_markers(self, row):
        name = row.get("Point number/name")
        if pd.isnull(name):
            return "6"
        if isinstance(name, str) and name.startswith("TMP"):
            if (
                len(name) > 8
                and name[8] == "s"
                and any(c in name for c in ["a", "b", "c"])
            ):
                return "T"
            else:
                return "+"
        return "6"

    # determine wall number based on the exceldata name
    def determine_wall_number(self, row):
        wallnum = 7
        name = row["Point number/name"]
        if self.wall_name in name:
            if self.indexwall < len(self.wall_600x600mm):
                wallnum = extractor.wallnumber(
                    self.wall_600x600mm[self.indexwall]["Pin ID"]
                )
                return wallnum
        for data_legend in self.wall_legend:
            data_pen_name = data_legend.get(self.pen_column)
            data_pin_id = data_legend.get(self.pin_id_column)
            if data_pen_name in name:
                wallnum = extractor.wallnumber(data_pin_id)
                return wallnum
        if "CP" in name or "LP" in name or "SP" in name or "TMP" in name:
            wallnum = extractor.wallnumber(name)
        if "Floor:BSS.60" in name or "Celling" in name:
            wallnum = 8
        return wallnum
