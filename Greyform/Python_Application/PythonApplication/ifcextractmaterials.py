import numpy as np
import ifcopenshell

# include error in text file
def log_error(message):
    with open("error_log.txt", "a") as log_file:
        log_file.write(message + "\n")


def log(message):
    with open("log.txt", "a") as log_file:
        log_file.write(message + "\n")

def openings(ifc_file):
    openings = ifc_file.by_type("IfcOpeningElement")
    opening_wall_objects = []
    for opening in openings:
        opening_name = opening.Name
        if "basic wall:bss.50" in opening_name.lower():
            x, y, z = (0, 0, 0)
            if opening.ObjectPlacement:
                placement = opening.ObjectPlacement.RelativePlacement
                if placement and placement.Location:
                    x, y, z = placement.Location.Coordinates
            scale_factor = 1000.0
            scaled_grouped_verts = 0
            if opening.Representation is not None:
                settings = ifcopenshell.geom.settings()
                shape = ifcopenshell.geom.create_shape(settings, opening)
                verts = shape.geometry.verts
                grouped_verts = [
                    [verts[i], verts[i + 1], verts[i + 2]]
                    for i in range(0, len(verts), 3)
                ]
                scaled_grouped_verts = np.array(grouped_verts) * scale_factor
                scaled_grouped_verts = scaled_grouped_verts.astype(int)
            opening_wall_objects.append(
                {
                    "name": opening_name,
                    "x": x,
                    "y": y,
                    "z": z,
                    "vertices": scaled_grouped_verts,
                }
            )
    return opening_wall_objects
