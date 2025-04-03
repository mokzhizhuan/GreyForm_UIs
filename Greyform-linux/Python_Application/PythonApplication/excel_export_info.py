import pandas as pd
from ifcopenshell.util.placement import get_local_placement, get_axis2placement
import PythonApplication.arraystorage as storingelement
import PythonApplication.ifcextractfiles as extractor


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
    ):
        # starting initialize
        super().__init__()
        self.file = file
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
        self.wallformat, self.heighttotal, self.wall_height = (
            storingelement.wall_format(self.wall_dimensions, self.floor, self.label_map)
        )
        self.wall_finishes_height, self.small_wall_height = (
            storingelement.wall_format_finishes(self.wall_finishes_dimensions)
        )
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
        try:
            data = extractor.get_objects_data_by_class(file, class_type)
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
                    value = extractor.get_attribute_value(object_data, attribute)
                    row.append(value)
                pandas_data.append(tuple(row))
            dataframe = pd.DataFrame.from_records(pandas_data, columns=attributes)
            dataframe["Wall Number"] = dataframe.apply(
                self.determine_wall_number, axis=1
            )
            dataframe["Shape type"] = dataframe.apply(self.add_markers, axis=1)
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
            dataframe = dataframe[dataframe["Stage"] != "Stage 1"]
            startingwall = -abs(self.meterline + (self.wall_height / 2))
            endingwall = -abs(self.centerlinez() + (self.wall_height / 2))
            dataframe = dataframe[
                (dataframe["Position Z (mm)"] >= startingwall)
                | (dataframe["Position Z (mm)"] <= endingwall)
            ]  # Exclude specific conditions for Wall Number 7
            dataframe = dataframe[
                ~(
                    dataframe["Position Z (mm)"].between(
                        0, self.wall_finishes_height / 2
                    )
                    & (dataframe["Wall Number"] == 7)
                )
            ]
            unwanted_names = [
                "Basic Wall",
                "BSS.Shower",
                "M_Coupling",
                "BSS.TECE.CONCEALED",
                "BSS.Gate Valve",
                "LP",
                "Floor",
            ]
            pattern = "|".join(unwanted_names)
            dataframe = dataframe[
                ~dataframe["Point number/name"].str.contains(
                    pattern, case=False, na=False
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
            file_name = f"exporteddatassss(with TMP)(draft1)(tetra).xlsx"
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
                    extractor.apply_rotation_to_markers(worksheet, df_class)
        except Exception as e:
            extractor.log_error(f"Failed to write Excel file: {e}")

    def determine_walls(self, row):
        for index, (wall, dims) in enumerate(self.wall_dimensions.items(), start=0):
            if "Basic Wall:BSS.50" in wall and wall == row["Point number/name"]:
                return index + 1
        return row["Wall Number"]

    def applywallpoints(self, row):
        wall_number = row["Wall Number"]
        positionx = row["Position X (mm)"]
        positiony = row["Position Y (mm)"]
        positionz = row["Position Z (mm)"]
        center_z = self.centerlinez()
        internaldimensiony = self.floor[1]
        twowall_x = 0
        thickness = self.wall_finishes_height + self.wall_height
        small_thickness = self.small_wall_height + self.wall_height
        internaldimensionx = extractor.calculate_internaldimensionx(
            thickness, small_thickness, self.wallformat
        )
        x_min, x_max = min(self.axis_widths["x"]), max(self.axis_widths["x"])
        y_min, y_max = min(self.axis_widths["y"]), max(self.axis_widths["y"])
        direction_stack = []
        count_plus_y = 0
        count_minus_y = 0
        for index, (start, end, direction) in enumerate(self.directional_axes_axis):
            direction_stack.append(direction)
            count_minus_y = direction_stack.count("-Y")
            count_plus_y = direction_stack.count("+Y")
            if count_plus_y >= 2:
                twowall_x = x_max - (x_max - x_min)
            elif count_minus_y >= 2:
                twowall_x = x_max - x_min
        if internaldimensiony != (
            max(self.axis_widths["x"]) - min(self.axis_widths["x"])
        ):
            internaldimensiony = max(self.axis_widths["x"]) - min(self.axis_widths["x"])
            y_max = max(self.axis_widths["x"]) - min(self.axis_widths["x"])
            y_min = (max(self.axis_widths["x"]) - min(self.axis_widths["x"])) - (
                max(self.axis_widths["y"]) - min(self.axis_widths["y"])
            )
        pos_z = positionz - center_z + (self.floorheight) - (self.wall_height / 2)
        for wall_id, wall in self.wallformat.items():
            center_x = internaldimensionx / 2
            posy = internaldimensiony / 2
            if wall_number == wall_id:
                if wall["axis"] == "y":
                    if wall_id == len(self.wallformat):
                        pos_z = positionz - center_z + (self.floorheight)
                    robotposy = positiony - posy
                    robotposx = positionx - thickness
                    if (
                        twowall_x < positionx
                        and internaldimensionx > positionx
                        and count_plus_y == 2
                    ) or (
                        center_x < positionx
                        and internaldimensionx > positionx
                        and count_minus_y == 2
                    ):
                        startingrange = wall["pos_y_range"][0]
                        if (
                            startingrange > y_max - y_min - thickness
                            and startingrange < internaldimensiony - thickness
                        ):
                            startingrange = internaldimensiony - thickness
                        endrange = wall["pos_y_range"][1]
                        endrangex = wall["pos_x_range"][1]
                        if (
                            endrange - startingrange < internaldimensiony
                            and endrange - startingrange > y_min
                            and count_plus_y == 2
                        ):
                            endrange = internaldimensiony
                        elif count_plus_y == 2:
                            endrange = internaldimensiony - thickness
                        if count_minus_y == 2 and endrangex == x_max:
                            if self.wallformat[wall_id - 1]["width"] <= x_min:
                                robotposx = robotposx - (
                                    (x_max - x_min) - (thickness * 2)
                                )
                            else:
                                robotposx = robotposx - (x_max - (x_max - x_min))
                        elif count_plus_y == 2 and endrangex == x_max:
                            if self.wallformat[wall_id - 1]["width"] <= x_min:
                                robotposx = robotposx - (
                                    (x_max - x_min) - (thickness * 2)
                                )
                            else:
                                robotposx = robotposx - (x_max - (x_max - x_min))
                        robotposy = (
                            positiony - startingrange - ((endrange - startingrange) / 2)
                        )
                        if robotposy > 0:
                            return pd.Series([robotposx, -abs(robotposy), pos_z])
                        else:
                            return pd.Series([robotposx, abs(robotposy), pos_z])
                    else:
                        endrange = wall["pos_y_range"][1]
                        if endrange != internaldimensiony:
                            robotposy = positiony - (endrange / 2)
                        if count_plus_y == 2:
                            robotposx = -abs(internaldimensionx - (thickness * 2))
                        return pd.Series([robotposx, robotposy, pos_z])
                elif wall["axis"] == "x":
                    robotposy = positiony - thickness
                    robotposx = positionx - center_x
                    if posy < positiony and internaldimensiony > positiony:
                        startingrange = wall["pos_x_range"][0]
                        endrange = wall["pos_x_range"][1]
                        endrangey = wall["pos_y_range"][1]
                        robotposx = (
                            positionx - startingrange - ((endrange - startingrange) / 2)
                        )
                        if count_minus_y == 2 and (
                            endrangey == y_max - y_min
                            or endrangey == y_max - (y_max - y_min)
                        ):
                            robotposy = -abs((y_max - (thickness * 2)) - robotposy)
                            robotposx = (
                                positionx
                                - startingrange
                                - ((endrange - startingrange) / 2)
                            )
                        elif (
                            count_plus_y == 2
                            and endrangey > y_max - y_min
                            and endrangey <= y_max
                        ):
                            if self.wallformat[wall_id - 1]["width"] <= y_min:
                                robotposy = robotposy - (
                                    (y_max - y_min) - (thickness * 2)
                                )
                            else:
                                robotposy = robotposy - (
                                    (y_max - (y_max - y_min)) - (thickness * 2)
                                )
                        if robotposx > 0:
                            return pd.Series([robotposy, -abs(robotposx), pos_z])
                        else:
                            return pd.Series([robotposy, abs(robotposx), pos_z])
                    else:
                        return pd.Series([robotposy, robotposx, pos_z])
        return pd.Series([positionx - thickness, positiony - thickness, positionz])

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
