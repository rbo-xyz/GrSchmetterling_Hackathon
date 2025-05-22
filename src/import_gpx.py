import gpxpy
from pyproj import Transformer

transformer = Transformer.from_crs("EPSG:4326", "EPSG:2056", always_xy=True)

def parse_gpx(filepath: str):

    points_lv95 = []
    with open(filepath, 'r', encoding="utf-8") as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    lon, lat, elev = point.longitude, point.latitude, point.elevation or 0.0
                    # Transformation in LV95
                    e, n = transformer.transform(lon, lat)
                    points_lv95.append((e, n, elev))
    return points_lv95