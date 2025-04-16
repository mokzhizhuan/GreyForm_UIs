import pandas as pd
from openpyxl.utils import get_column_letter


class Exportexcelinfolegend(object):
    def __init__(self, markingitems):
        # starting initialize
        super().__init__()
        try:
            dataframe_Legend = pd.read_excel(
                "Pin Allocation BOM for PBU_T1a.xlsx", skiprows=2, engine="openpyxl"
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
            markingitem = pd.DataFrame(markingitems)
            markingitem["Stages"] = markingitem.apply(
                self.determine_stage_number, axis=1
            )
            markingitem["Stages"] = markingitem["Stages"].apply(
                lambda x: f"Stage {int(x)}" if pd.notnull(x) else None
            )
            markingitem = {
                stage: group.drop(columns='Stages').to_dict(orient='list')
                for stage, group in markingitem.groupby('Stages', dropna=False)
            }
            self.markingdata = markingitem
            self.process_data()
        except Exception as e:
            self.log_error(f"Failed to write Excel file: {e}")

    def process_data(self):
        # Process and assign data to markingitems
        self.markingitems = self.markingdata
        self.returndata()

    # write log error
    def log_error(self, message):
        with open("error_log.txt", "a") as log_file:
            log_file.write(message + "\n")

    def returndata(self):
        return self.markingitems

    # get wal number
    def determine_stage_number(self, row):
        wallnum = None
        name = row["markingidentifiers"]
        if pd.isnull(name):
            self.index += 1
            return None
        name = str(name)
        if self.index == 117:
            self.index += 1
            return None
        if self.wall_name in name:
            if self.indexwall < len(self.wall_600x600mm):
                wallnum = self.stagenumber(
                    self.wall_600x600mm[self.indexwall]["Pin ID"]
                )
                self.indexwall += 1
                self.index += 1
                return wallnum
        for data_legend in self.wall_legend:
            data_pen_name = data_legend.get(self.pen_column)
            data_pin_id = data_legend.get(self.pin_id_column)
            if data_pen_name in name:
                wallnum = self.stagenumber(data_pin_id)
                self.index += 1
                return wallnum
        stagenum = self.stagenumber(name)
        self.index += 1
        return stagenum

    # determine wall number
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
