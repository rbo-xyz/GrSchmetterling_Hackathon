# import_gpx.py
import gpxpy

def parse_gpx(filepath):
    with open(filepath, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append((point.latitude, point.longitude, point.elevation))
        return points
