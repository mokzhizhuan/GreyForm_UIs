import os, sys, math, argparse
import pandas as pd
import numpy as np
import ifcopenshell
import heapq
import ifcopenshell.util.element as Element

SCALE = 1000.0

def validate_file(path, ext):
    if not path.lower().endswith(ext) or not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"Invalid or missing file: {path}")
    return path

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("excel_file", type=lambda p: validate_file(p, ".xlsx"))
    parser.add_argument("output_excel", type=str)
    return parser.parse_args()

def get_vertices(obj):
    if obj.Representation:
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, obj)
        verts = shape.geometry.verts
        grouped = np.array(
            [[verts[i], verts[i + 1], verts[i + 2]] for i in range(0, len(verts), 3)]
        )
        return (grouped * SCALE).astype(int)
    return 0

def get_posxyz(obj):
    if obj.ObjectPlacement and obj.ObjectPlacement.RelativePlacement:
        placement = obj.ObjectPlacement.RelativePlacement
        loc = getattr(placement, "Location", None)
        ref_dir = getattr(placement, "RefDirection", None)
        origin = tuple(loc.Coordinates) if loc else None
        direction = (
            tuple(ref_dir.DirectionRatios) if ref_dir else (1.0, 0.0, 0.0)
        )  # default X+
        return origin, direction
    return None, None, None

def classify_direction(direction_vector):
    dx, dy, dz = direction_vector
    if abs(dx) == 1.0 and dy == 0.0:
        return ("X", "+X") if dx > 0 else ("X", "-X")
    elif abs(dy) == 1.0 and dx == 0.0:
        return ("Y", "+Y") if dy > 0 else ("Y", "-Y")
    elif abs(dz) == 1.0 and dx == 0.0 and dy == 0.0:
        return ("Z", "")
    return ("Unknown", "")

def transform_from_operator(operator):
    scale = getattr(operator, "Scale", 1.0) or 1.0
    x_axis = (
        np.array(operator.Axis1.DirectionRatios)
        if operator.Axis1
        else np.array([1.0, 0.0, 0.0])
    )
    y_axis = (
        np.array(operator.Axis2.DirectionRatios)
        if operator.Axis2
        else np.array([0.0, 1.0, 0.0])
    )
    z_axis = (
        np.array(operator.LocalZ.DirectionRatios)
        if hasattr(operator, "LocalZ") and operator.LocalZ
        else np.cross(x_axis, y_axis)
    )
    origin = np.array(operator.LocalOrigin.Coordinates)
    matrix = np.identity(4)
    matrix[0:3, 0] = x_axis * scale
    matrix[0:3, 1] = y_axis * scale
    matrix[0:3, 2] = z_axis * scale
    matrix[0:3, 3] = origin
    return matrix

def axis2placement3d_to_matrix(placement):
    location = np.array(placement.Location.Coordinates)
    z_axis = (
        np.array(placement.Axis.DirectionRatios)
        if placement.Axis
        else np.array([0, 0, 1])
    )
    x_axis = (
        np.array(placement.RefDirection.DirectionRatios)
        if placement.RefDirection
        else np.array([1, 0, 0])
    )
    y_axis = np.cross(z_axis, x_axis)  # compute Y via cross product
    matrix = np.identity(4)
    matrix[0:3, 0] = x_axis
    matrix[0:3, 1] = y_axis
    matrix[0:3, 2] = z_axis
    matrix[0:3, 3] = location
    return matrix

def get_proxy_geometry_position(obj):
    if not obj.Representation:
        return (0.0, 0.0, 0.0)
    for rep in obj.Representation.Representations:
        for item in rep.Items:
            if item.is_a("IfcMappedItem"):
                operator = item.MappingTarget
                mapping_matrix = transform_from_operator(operator)
                origin = item.MappingSource.MappingOrigin
                origin_matrix = axis2placement3d_to_matrix(origin)
                combined = np.dot(mapping_matrix, origin_matrix)
                for shape in item.MappingSource.MappedRepresentation.Items:
                    if shape.is_a("IfcExtrudedAreaSolid"):
                        solid_offset = axis2placement3d_to_matrix(shape.Position)
                        combined = np.dot(combined, solid_offset)
                        x, y, z = combined[0, 3], combined[1, 3], combined[2, 3]
                        return (x, y, z)

def process_elements(elements, name_filter):
    data = []
    for obj in elements:
        name = getattr(obj, "Name", "")
        if name_filter in name.lower():
            if obj.is_a("IfcBuildingElementProxy"):
                origin, dir = get_posxyz(obj)
                origin = get_proxy_geometry_position(obj)
            elif obj.is_a("IFCSlab"):
                if get_storey_name(obj) != "ceiling level":
                    origin, dir = get_posxyz(obj)
                    origin = get_floorpos(obj)
                else:
                    continue
            else:
                origin, dir = get_posxyz(obj)
            if origin == None:
                origin, dir = get_posxyz(obj)
            area = get_area(obj)  # for centerpoint
            axis = "Unknown"
            if axis:
                axis , facing_axis = classify_direction(dir)
            data.append(
                {
                    "name": name,
                    "x": round(origin[0]),
                    "y": round(origin[1]),
                    "z": round(origin[2]),
                    "axis": axis,
                    "facingaxis" : facing_axis,
                    "area": area,
                    "vertices": get_vertices(obj),
                }
            )
    return data

def get_area(obj):
    width, height, extrusion_depth = 0, 0, 0
    if obj.Representation is not None:
        for representation in obj.Representation.Representations:
            if representation.RepresentationType == "SweptSolid":
                solid = representation.Items[0]
                extruded_area = solid.SweptArea
                extrusion_depth = solid.Depth if hasattr(solid, "Depth") else None
                if hasattr(extruded_area, "XDim") and hasattr(extruded_area, "YDim"):
                    width = extruded_area.XDim
                    height = extruded_area.YDim
            elif (
                representation.RepresentationIdentifier == "Body"
                and representation.RepresentationType == "Clipping"
            ):
                for item in representation.Items:
                    if item.is_a("IfcBooleanClippingResult"):
                        if item.FirstOperand.is_a("IfcExtrudedAreaSolid"):
                            extruded_area_solid = item.FirstOperand
                            extrusion_depth = extruded_area_solid.Depth
                            profile = extruded_area_solid.SweptArea
                            width = profile.XDim
                            height = profile.YDim
    return (round(width), round(height), round(extrusion_depth))

def get_floorpos(obj):
    origin = (0, 0, 0)
    if obj.Representation:
        for rep in obj.Representation.Representations:
            for item in rep.Items:
                if item.is_a("IfcExtrudedAreaSolid"):
                    origin = tuple(item.Position.Location.Coordinates)
    else:
        placement = obj.ObjectPlacement
        if placement:
            point = placement.RelativePlacement.Location.Coordinates
        return tuple(point)
    return origin

def find_closest_wall(current, pool):
    cx, cy = float(current["x"]), float(current["y"])
    return min(
        (
            (w, math.hypot(w["x"] - cx, w["y"] - cy))
            for w in pool
            if w["name"] != current["name"]
        ),
        key=lambda x: x[1],
        default=(None, float("inf")),
    )

def compute_area(area_tuple):
    if area_tuple and len(area_tuple) >= 2:
        x, y = area_tuple[0], area_tuple[1]
        return x * y
    return 0

def get_storey_name(obj):
    if hasattr(obj, "ContainedInStructure"):
        for rel in obj.ContainedInStructure:
            if rel.is_a("IfcRelContainedInSpatialStructure"):
                storey = rel.RelatingStructure
                if storey.is_a("IfcBuildingStorey"):
                    return storey.Name.strip().lower()
    return None

def assign_stage(name):
    name = str(name).lower()
    return (
        "Stage 1"
        if "pipe" in name
        else (
            "Stage 2"
            if "wall" in name or "floor" in name and "drain" not in name
            else "Stage 3"
        )
    )
            
def extract_storeys(ifc_file):
    storeys, ground = [], []
    for storey in ifc_file.by_type("IfcBuildingStorey"):
        name, elevation = storey.Name or "Unnamed", storey.Elevation
        if any(k in name.upper() for k in ["CEILING"]):
            storeys.append({"name": name, "elevation": elevation})
        if any(k in name.upper() for k in ["BEDROOM", "FLOOR", "GROUND"]):
            ground.append({"name": name, "elevation": elevation})
    return storeys, ground

