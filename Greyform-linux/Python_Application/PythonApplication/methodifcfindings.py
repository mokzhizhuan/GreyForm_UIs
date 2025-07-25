import os, sys, math, argparse
import pandas as pd
import numpy as np
import ifcopenshell
import heapq
import ifcopenshell.util.element as Element
import ifcopenshell
import ifcopenshell.util.placement
import ifcopenshell.util.element

SCALE = 1000.0

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
        direction = tuple(ref_dir.DirectionRatios) if ref_dir else (1.0, 0.0, 0.0)
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

def process_elements(elements, name_filter):
    data = []
    brep_z = []
    brep_z_data = []
    furnishing_pos = []
    getfurnishing_pos = []
    for obj in elements:
        name = getattr(obj, "Name", "")
        if name_filter in name.lower():
            if obj.is_a("IfcBuildingElementProxy") and "mirror" not in name.lower():
                origin, dir = get_posxyz(obj)
                origin = change_z(origin, obj)
            elif obj.is_a("IFCSlab") and "notdefined" not in obj.PredefinedType.lower():
                if "notdefined" not in obj.PredefinedType.lower():
                    origin, dir = get_posxyz(obj)
                    origin = get_floorpos(obj)
                else:
                    continue
            elif obj.is_a("IfcFurnishingElement") and "bin" not in name.lower():
                origin, dir = get_posxyz(obj)
                getfurnishing_pos , base_stats = get_furnishing_y(obj)
                origin = change_z(origin, obj)
            elif obj.is_a("IfcFlowTerminal") and "floor" not in name.lower():
                origin, dir = get_posxyz(obj)
                brep_z = get_brep(obj)
                origin = change_z(origin, obj)
            else:
                origin, dir = get_posxyz(obj)
            if origin == None:
                origin, dir = get_posxyz(obj)
            area = get_area(obj)  # for centerpoint
            axis = "Unknown"
            if axis:
                axis, facing_axis = classify_direction(dir)
            data.append(
                {
                    "name": name,
                    "type": obj.is_a(),
                    "x": round(origin[0]),
                    "y": round(origin[1]),
                    "z": round(origin[2]),
                    "axis": axis,
                    "facingaxis": facing_axis,
                    "area": area,
                    "vertices": get_vertices(obj),
                }
            )
            if brep_z:
                brep_z_data.append(
                    {
                        "name": name,
                        "type": obj.is_a(),
                        "z_min": round(brep_z[0]),
                        "z_max": round(brep_z[1]),
                    }
                )
            if getfurnishing_pos:
                furnishing_pos.append(
                    {
                        "name": name,
                        "type": obj.is_a(),
                        "furnishing_y_pos": round(getfurnishing_pos[1]),
                        "width": round(base_stats["width"]),
                        "height": round(base_stats["height"]),
                    }
                )
    return data , brep_z_data , furnishing_pos


def change_z(origin, obj):
    if len(origin) == 3 and round(origin[2]) <= 0.0:
        placement = obj.ObjectPlacement
        while hasattr(placement, "PlacementRelTo") and placement.PlacementRelTo:
            placement = placement.PlacementRelTo
        shape = obj.Representation
        for item in shape.Representations:
            for mapped in item.Items:
                if mapped.is_a("IfcMappedItem"):
                    mapping_source = mapped.MappingSource
                    for subitem in mapping_source.MappedRepresentation.Items:
                        if subitem.is_a("IfcExtrudedAreaSolid"):
                            z_corrected = extract_z_from_shape_item(subitem)
                            origin = set_origin_z(origin, z_corrected , subitem)
                            return origin
                        elif subitem.is_a("IfcFacetedBrep"):
                            z_corrected = extract_z_from_shape_item(subitem)
                            origin = set_origin_z(origin, z_corrected , subitem)
                            return origin
                        elif subitem.is_a("IfcFaceBasedSurfaceModel"):
                            z_corrected = extract_z_from_shape_item(subitem)
                            origin = set_origin_z(origin, z_corrected , subitem)
                            return origin
    return origin

def get_furnishing_y(obj):
    based_curve_points, base_stats = [] , {}
    coords = None
    placement = obj.ObjectPlacement
    while hasattr(placement, "PlacementRelTo") and placement.PlacementRelTo:
        placement = placement.PlacementRelTo
    shape = obj.Representation
    for item in shape.Representations:
        for mapped in item.Items:
            if mapped.is_a("IfcMappedItem"):
                mapping_source = mapped.MappingSource
                for subitem in mapping_source.MappedRepresentation.Items:
                    if subitem.is_a("IfcExtrudedAreaSolid"):
                        profile = subitem.SweptArea
                        if profile.is_a("IfcArbitraryClosedProfileDef"):
                            outer_curve = profile.OuterCurve
                            base_pts, _ = get_rail_points(outer_curve)
                            based_curve_points.extend(base_pts)
                            base_stats = compute_width_height(based_curve_points)
                            coords = subitem.Position.Location.Coordinates
                            return coords , base_stats
    return coords , base_stats

def compute_width_height(points_3d):
    xs, ys = [], []
    for pt in points_3d:
        # Flatten excessive dimensions
        if isinstance(pt, tuple) and len(pt) >= 2:
            x, y = float(pt[0]), float(pt[1])
            xs.append(x)
            ys.append(y)
    if not xs or not ys:
        raise ValueError("No valid 2D or 3D points in input")
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width = max_x - min_x
    height = max_y - min_y  
    return {
        "min_x": min_x,
        "max_x": max_x,
        "min_y": min_y,
        "max_y": max_y,
        "width": width,
        "height": height
    }


def extract_composite_curve_points(composite_curve, arc_resolution=10):
    points = []
    if composite_curve.is_a("IfcCompositeCurve"):
        for segment in composite_curve.Segments:
            subcurve = segment.ParentCurve
            points.extend(extract_composite_curve_points(subcurve))
    elif composite_curve.is_a("IfcPolyline"):
        points.extend([to_3d(pt.Coordinates) for pt in composite_curve.Points])
    elif composite_curve.is_a("IfcTrimmedCurve"):
        base = composite_curve.BasisCurve
        if base.is_a("IfcCircle"):
            center = base.Position.Location.Coordinates
            radius = base.Radius
            start_angle = composite_curve.Trim1[0].wrappedValue
            end_angle = composite_curve.Trim2[0].wrappedValue
            for i in range(arc_resolution + 1):
                angle_deg = start_angle + i * (end_angle - start_angle) / arc_resolution
                angle_rad = math.radians(angle_deg)
                x = center[0] + radius * math.cos(angle_rad)
                y = center[1] + radius * math.sin(angle_rad)
                points.append((x, y, 0.0))
    else:
        print("⚠️ Unhandled segment type:", composite_curve.is_a())
    return points

def to_3d(coords, z=0.0):
    return tuple(list(coords) + [0.0] * (3 - len(coords[:-1])) + [z])

def get_rail_points(outer_curve_entity, extrusion_height=60.0):
    base_profile = extract_composite_curve_points(outer_curve_entity)
    top_profile = [(pt[0], pt[1], extrusion_height) for pt in base_profile]
    return base_profile, top_profile             

def get_brep(obj):
    placement = obj.ObjectPlacement
    while hasattr(placement, "PlacementRelTo") and placement.PlacementRelTo:
        placement = placement.PlacementRelTo
    shape = obj.Representation
    for item in shape.Representations:
        for mapped in item.Items:
            if mapped.is_a("IfcMappedItem"):
                mapping_source = mapped.MappingSource
                for subitem in mapping_source.MappedRepresentation.Items:
                    if subitem.is_a("IfcFacetedBrep"):
                        min_z , max_z = extract_z_from_shape_item_face(subitem)
                        brep_z = [min_z, max_z]
                        return brep_z

def set_origin_z(origin, new_z, shape_item):
    if round(origin[2]) < 0.0 and shape_item.is_a("IfcExtrudedAreaSolid"):
        point = (origin[0], origin[1], origin[2] + new_z)
    else:
        point = (origin[0], origin[1], new_z)
    return point

def extract_z_from_shape_item_face(shape_item):
    if shape_item.is_a("IfcFacetedBrep"):
        all_z = []
        for face in shape_item.Outer.CfsFaces:
            for bound in face.Bounds:
                for pt in bound.Bound.Polygon:
                    z = pt.Coordinates[2]
                    all_z.append(z)
        return min(all_z) , max(all_z)

def extract_z_from_shape_item(shape_item):
    if shape_item.is_a("IfcExtrudedAreaSolid"):
        return shape_item.Position.Location.Coordinates[2]
    elif shape_item.is_a("IfcFacetedBrep"):
        all_z = []
        for face in shape_item.Outer.CfsFaces:
            for bound in face.Bounds:
                for pt in bound.Bound.Polygon:
                    z = pt.Coordinates[2]
                    all_z.append(z)
            if all_z:
                return min(all_z) 
    elif shape_item.is_a("IfcFaceBasedSurfaceModel"):
        all_z , pts = [], []
        for connected in shape_item.FbsmFaces:
            for face in connected.CfsFaces:
                for bound in face.Bounds:
                    for pt in bound.Bound.Polygon:
                        all_z.append(pt.Coordinates[2])
        return min(all_z) if all_z else None
    return None


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

def find_closest_wall_rotation(current, pool):
    cx, cy = float(current["x"]), float(current["y"])
    return min(
        (
            (w, math.hypot(w["x"] - cx, w["y"] - cy))
            for w in pool
            if w["name"] != current["name"] and w["axis"] == current["axis"]
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

def extract_storeys(ifc_file):
    storeys, ground = [], []
    for storey in ifc_file.by_type("IfcBuildingStorey"):
        name, elevation = storey.Name or "Unnamed", storey.Elevation
        if any(k in name.upper() for k in ["CEILING"]):
            storeys.append({"name": name, "elevation": elevation})
        if any(k in name.upper() for k in ["BEDROOM", "FLOOR", "GROUND"]):
            ground.append({"name": name, "elevation": elevation})
    return storeys, ground

def log_info(message):
    with open("log.txt", "a") as log_file:
        log_file.write(message + "\n")

