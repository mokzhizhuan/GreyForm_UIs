import ifcopenshell
import ifcopenshell.geom
import pandas as pd
import ifcopenshell.util.element as Element
from ifcopenshell.util.placement import get_local_placement


class Exportexcelinfo(object):
    def __init__(self, file, class_type):
        try:
            data, pset_attributes = self.get_objects_data_by_class(file, class_type)
            attributes = [
                "ExpressID",
                "GlobalID",
                "Class",
                "PredefinedType",
                "Name",
                "Level",
                "ObjectType",
                "PlacementMatrix",
                "RevertOrigin",
                "Vertices",
            ] + pset_attributes

            pandas_data = []
            for object_data in data:
                row = []
                for attribute in attributes:
                    value = self.get_attribute_value(object_data, attribute)
                    row.append(value)
                pandas_data.append(tuple(row))

            dataframe = pd.DataFrame.from_records(pandas_data, columns=attributes)
            dataframe["Markers"] = dataframe.apply(self.add_markers, axis=1)
            file_name = f"exporteddata.xlsx"
            with pd.ExcelWriter(file_name) as writer:
                workbook = writer.book
                # format_rotated = workbook.add_format({'text_wrap': True, 'valign': 'top', 'rotation': 90})

                for object_class in dataframe["Class"].unique():
                    df_class = dataframe[dataframe["Class"] == object_class]
                    df_class = df_class.drop(
                        [
                            "Class",
                            "PredefinedType",
                            "RevertOrigin",
                            "Vertices",
                            "Pset_ProvisionForVoid.Width",
                            "Pset_ProvisionForVoid.Depth",
                            "Pset_QuantityTakeOff.Reference",
                            "Pset_ProvisionForVoid.id",
                            "Pset_ProductRequirements.id",
                            "Pset_BuildingElementProxyCommon.Reference",
                            "Pset_QuantityTakeOff.id",
                            "Pset_BuildingElementProxyCommon.id",
                            "Pset_ProvisionForVoid.Height",
                            "Pset_ProductRequirements.Category",
                        ],
                        axis=1,
                    )
                    df_class = df_class.dropna(axis=1, how="all")
                    df_class.to_excel(writer, sheet_name=object_class)
                    # Rotated cell
                    worksheet = writer.sheets[object_class]
                    self.apply_rotation_to_markers(workbook, worksheet, df_class)
            # Apply this custom formatting function to the 'PlacementMatrix' column
            dataframe["PlacementMatrix"] = dataframe["PlacementMatrix"].apply(
                self.format_matrix
            )
        except Exception as e:
            self.log_error(f"Failed to write Excel file: {e}")

    def get_objects_data_by_class(self, file, class_type):
        pset_attributes = set()
        objects_data = []
        objects = file.by_type(class_type)
        for object in objects:
            psets = Element.get_psets(object, psets_only=True)
            self.add_pset_attributes(psets, pset_attributes)
            qtos = Element.get_psets(object, qtos_only=True)
            self.add_pset_attributes(qtos, pset_attributes)
            placement_matrix = get_local_placement(object.ObjectPlacement)
            revert_origin = object.Name if object.Name == "CP1:CP1:1433163" else ""
            # Extract Vertices of Elements
            if object.Representation is not None:
                settings = ifcopenshell.geom.settings()
                shape = ifcopenshell.geom.create_shape(settings, object)
                verts = shape.geometry.verts
                grouped_verts = [
                    [verts[i], verts[i + 1], verts[i + 2]]
                    for i in range(0, len(verts), 3)
                ]
            objects_data.append(
                {
                    "ExpressID": object.id(),
                    "GlobalID": object.GlobalId,
                    "Class": object.is_a(),
                    "PredefinedType": Element.get_predefined_type(object),
                    "Name": object.Name,
                    "Level": (
                        Element.get_container(object).Name
                        if Element.get_container(object)
                        else ""
                    ),
                    "ObjectType": (
                        Element.get_type(object).Name
                        if Element.get_type(object)
                        else ""
                    ),
                    "PlacementMatrix": placement_matrix,
                    "RevertOrigin": revert_origin,
                    "Vertices": grouped_verts,
                    "QuantitySets": qtos,
                    "PropertySets": psets,
                }
            )
        return objects_data, list((pset_attributes))

    def add_pset_attributes(self, psets, pset_attributes):
        for pset_name, pset_data in psets.items():
            for property_name in pset_data.keys():
                pset_attributes.add(f"{pset_name}.{property_name}")

    def log_error(self, message):
        with open("error_log.txt", "a") as log_file:
            log_file.write(message + "\n")

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

    def format_matrix(self, matrix):
        return [[f"{element:.2f}" for element in row] for row in matrix]

    def add_markers(self, row):
        if row["Name"] and row["Name"].startswith("TMP"):
            if (
                any(char in row["Name"] for char in ["a", "b", "c"])
                and row["Name"][8] == "s"
            ):
                return "T"
            else:
                return "+"
        return ""

    def apply_rotation_to_markers(self, workbook, worksheet, df_class):
        marker_col_index = df_class.columns.get_loc("Markers")
        format_rotated_n90 = workbook.add_format({"rotation": -90})
        format_rotated_90 = workbook.add_format({"rotation": 90})
        for row_idx, (name, marker) in enumerate(
            zip(df_class["Name"], df_class["Markers"]), start=1
        ):
            if name and name.startswith("TMP") and name[8] == "s" and name[3] == "7":
                print(f"Rotating marker for row {row_idx}: {marker}")
                if "b" in name:
                    worksheet.write(
                        row_idx, marker_col_index + 1, marker, format_rotated_90
                    )
                else:
                    worksheet.write(
                        row_idx, marker_col_index + 1, marker, format_rotated_n90
                    )
