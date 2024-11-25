import ezdxf
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon 
import pandas as pd


def read_dxf_to_gdf(filepath):
    doc = ezdxf.readfile(filepath)
    msp = doc.modelspace()

    data = []
    for entity in msp:
        try:
            if entity.dxftype() == 'POINT':
                x, y, z = entity.dxf.location
                geom = Point(x, y, z)
            elif entity.dxftype() == 'LINE':
                start = (float(entity.dxf.start.x), float(entity.dxf.start.y))
                end = (float(entity.dxf.end.x), float(entity.dxf.end.y))
                geom = LineString([start, end])
            elif entity.dxftype() == 'LWPOLYLINE':
                points = entity.get_points(format='xy')
                geom = Polygon(points)

            if geom:
                data.append({
                    'Class': entity.dxftype(),
                    'Marking type': entity.dxftype(),
                    'Point number/name': entity.dxf.handle,
                    'Position X (m)': getattr(geom, 'x', None),
                    'Position Y (m)': getattr(geom, 'y', None),
                    'Position Z (m)': getattr(geom, 'z', 0),
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

