import ezdxf
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon 
import pandas as pd
from shapely.geometry import Point
from shapely.affinity import rotate
from math import radians, cos, sin, pi

def is_polyface_mesh(polyline):
    """ Check if the polyline is a polyface mesh based on the flags attribute. """
    return polyline.dxf.flags & 0x80 == 0x80  # Polyface mesh flag check


def read_dxf_to_gdf(filepath):
    doc = ezdxf.readfile(filepath)
    msp = doc.modelspace()

    data = []
    for entity in msp:
        print(f"Processing entity type: {entity.dxftype()}, handle: {entity.dxf.handle}")
        try:
            geom = None
            x, y, z = None, None, None
            if entity.dxftype() == 'POINT':
                x, y, z = entity.dxf.location
                geom = Point(x, y, z)
            elif entity.dxftype() == 'LINE':
                start = (float(entity.dxf.start.x), float(entity.dxf.start.y))
                end = (float(entity.dxf.end.x), float(entity.dxf.end.y))
                geom = LineString([start, end])
                x, y  = geom.centroid.x, geom.centroid.y 
            elif entity.dxftype() == 'POLYLINE' and is_polyface_mesh(entity):
                geom = handle_polyface(entity)
                if geom:
                    data.append({
                        'Class': 'POLYLINE',
                        'Marking type': entity.dxftype(),
                    'Point number/name': entity.dxf.handle,
                    'Position X (m)': geom.centroid.x if geom else None,
                    'Position Y (m)': geom.centroid.y if geom else None,
                    'Position Z (m)': geom.centroid.z if geom else 0,
                    'Wall Number': '',
                    'Shape type': '',
                    'Status': 'Active',
                    'Quadrant': 1,
                    'Width': None,
                    'Height': None,
                    'Orientation': 1,
                    'Geometry': geom
                    })
            elif entity.dxftype() == 'ARC':
                center = (entity.dxf.center.x, entity.dxf.center.y)
                radius = entity.dxf.radius
                start_angle = entity.dxf.start_angle
                end_angle = entity.dxf.end_angle
                geom = arc_to_line(center, radius, start_angle, end_angle)
                x, y = geom.centroid.x, geom.centroid.y 
            elif entity.dxftype() == 'INSERT':
                geoms = process_insert(entity, doc.blocks)
                for geom in geoms:
                    data.append({
                        'Class': entity.dxftype(),
                        'Marking type': entity.dxftype(),
                        'Point number/name': entity.dxf.handle,
                        'Position X (m)': x,
                        'Position Y (m)': y,
                        'Position Z (m)': z if z is not None else 0,
                        'Wall Number': '',
                        'Shape type': '',
                        'Status': 'Active',
                        'Quadrant': 1,
                        'Width': None,
                        'Height': None,
                        'Orientation': 1,
                        'Geometry': geom
                    })
            if geom:
                data.append({
                    'Class': entity.dxftype(),
                    'Marking type': entity.dxftype(),
                    'Point number/name': entity.dxf.handle,
                    'Position X (m)': x,
                    'Position Y (m)': y,
                    'Position Z (m)': z if z is not None else 0,
                    'Wall Number': '',
                    'Shape type': '',
                    'Status': 'Active',
                    'Quadrant': 1,
                    'Width': None,
                    'Height': None,
                    'Orientation': 1,
                    'Geometry': geom
                })

        except Exception as err:
            print(f"Failed to process {entity.dxftype()} with handle {entity.dxf.handle}: {err}")

    if not data:
        raise ValueError("No valid geometry data found in DXF file")

    gdf = gpd.GeoDataFrame(data, geometry='Geometry')
    df = pd.DataFrame(gdf.drop(columns=['Geometry']))
    df['Geometry'] = gdf['Geometry'].apply(lambda geom: geom.wkt)
    excel_path = 'output.xlsx'
    df.to_excel(excel_path, index=False)

def arc_to_line(center, radius, start_angle, end_angle, num_points=30):
    """ Convert an ARC entity to a LineString approximation """
    points = []
    delta_angle = radians(end_angle - start_angle) / num_points
    for i in range(num_points + 1):
        angle = radians(start_angle) + i * delta_angle
        x = center[0] + radius * cos(angle)
        y = center[1] + radius * sin(angle)
        points.append((x, y))
    return LineString(points)

def process_insert(entity, blocks):
    """ Process an INSERT entity to extract and transform its block definition """
    insert_point = (entity.dxf.insert.x, entity.dxf.insert.y)
    block = blocks[entity.dxf.name]  # Access the block definition using the block name
    # Assume block entities are transformed into geometry here, for simplicity
    # You would need to apply translation, rotation, and scaling based on the INSERT entity's attributes
    transformed_geometries = []
    for blk in block:
        if blk.dxftype() == 'POINT':
            # Similar transformation as an example, real transformation needs matrix operations
            x, y = blk.dxf.location.x + insert_point[0], blk.dxf.location.y + insert_point[1]
            geom = Point(x, y)
            transformed_geometries.append(geom)
    return transformed_geometries

def handle_polyface(entity):
    # Retrieve all vertices of the polyface mesh
    vertices = list(entity.vertices())
    if not vertices:
        return None
    
    points = [(vertex.dxf.location.x, vertex.dxf.location.y, vertex.dxf.location.z) for vertex in vertices]
    if len(points) > 2:
        return Polygon(points)  # or LineString(points) if more appropriate
    elif len(points) == 2:
        return LineString(points)
    elif len(points) == 1:
        return Point(points[0])

    return None