import xml.etree.ElementTree as ET
import os

import geopandas as gpd
from shapely.geometry import Point, LineString
import gpxpy
from pyproj import Transformer

transformer = Transformer.from_crs("EPSG:4326", "EPSG:2056", always_xy=True)

## <---------------------------------------------------------------------------------------------------------------->
## <---------------------------------------------------------------------------------------------------------------->

def import_gpx(filepath: str):
    
    ## Filepath vorhanden
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Datei '{filepath}' wurde nicht gefunden.")

    ## Filepath ist lesbar
    try:
        ET.parse(filepath)
    except ET.ParseError as e:
        raise ValueError(f"Datei '{filepath}' ist kein gültiges XML/GPX: {e}")

    ## Check Source
    source = identify_source(filepath)

    ## Gebe an Importmethode weiter
    if source == "app":
        gdf = import_app(filepath)
    if source == "web":
        pass
    if source == "unknown":
        raise ValueError(f"Datei '{filepath}' ist weder von der Swisstopo-App noch vom Siwsstopo-GIS erstellt worden.")

    return gdf

## <---------------------------------------------------------------------------------------------------------------->
## <---------------------------------------------------------------------------------------------------------------->

def identify_source(filepath: str):
    """
    Liest eine GPX-Datei ein und gibt zurück,
    ob sie mit der Swisstopo-App oder via Web (OpenLayers) erstellt wurde.

    Eingabe:
        - filepath: Pfad zur GPX-Datei

    Rückgabe:
        - 'app' für Swisstopo App
        - 'web' für Web-Export (OpenLayers)
        - 'unknown' falls weder eindeutig noch lesbar
    """

    XSI = "http://www.w3.org/2001/XMLSchema-instance"

    tree = ET.parse(filepath)
    root = tree.getroot()

    creator    = root.attrib.get("creator", "").lower()
    schema_loc = root.attrib.get(f"{{{XSI}}}schemaLocation", "").lower()

    if "swisstopo app" in creator or "swisstopoextensions.xsd" in schema_loc:
        return "app"
    if "openlayers" in creator:
        return "web"
    return "unknown"

## <---------------------------------------------------------------------------------------------------------------->
## <---------------------------------------------------------------------------------------------------------------->

def import_app(filepath: str):
    """
    Importiert GPX-Datei, die mit der Swisstopo-App erstellt wurde.
    """
    ## Erstellung Waypoints GeoDataFrame
    gdf_waypoints = gpd.read_file(filepath, layer="waypoints", driver="GPX")
    gdf_waypoints = gdf_waypoints.set_crs(epsg=4326).to_crs(epsg=2056)
    pts_3d = [Point(x, y, z) for x, y, z in zip(gdf_waypoints.geometry.x, gdf_waypoints.geometry.y, gdf_waypoints["ele"])]
    gdf_waypoints = gdf_waypoints.set_geometry(pts_3d, crs=gdf_waypoints.crs)[["swisstopo_waypoint_id", "name", "geometry"]]
    gdf_waypoints.rename(columns={"swisstopo_waypoint_id": "id"}, inplace=True)

    ## Erstellung des Tracks GeoDataFrames
    lines_lv95 = []
    identifier_segment = 0
    identifier_list = []

    with open(filepath, 'r', encoding='utf-8') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        for track in gpx.tracks:
            for segment in track.segments:
                coords = []
                identifier_segment += 1
                for pt in segment.points:
                    lon, lat, elev = pt.longitude, pt.latitude, pt.elevation or 0.0
                    e, n = transformer.transform(lon, lat)
                    coords.append((e, n, elev))
                # 3D-LineString erzeugen
                lines_lv95.append(LineString(coords))
                identifier_list.append(identifier_segment)

    gdf_lines = gpd.GeoDataFrame(
        {"id": identifier_list, "geometry": lines_lv95},
        crs="EPSG:2056"   # LV95
    )

    ## Konvertierung der Dataframe für die Ausgabe
    result = combine_waypoints_lines(gdf_lines, gdf_waypoints)

    return result

## <---------------------------------------------------------------------------------------------------------------->
## <---------------------------------------------------------------------------------------------------------------->

def import_web(filepath: str):
    pass



## <---------------------------------------------------------------------------------------------------------------->
## <---------------------------------------------------------------------------------------------------------------->

def combine_waypoints_lines(gdf_lines: gpd.GeoDataFrame,
                            gdf_waypoints: gpd.GeoDataFrame):

    ## Lines GeoDataFrame unbennene und angleichen an Waypoints GeoDataFrame
    gdf = (
        gdf_lines
        .rename(columns={"id": "segment_id"})
        .copy()
        .set_geometry("geometry")
        .rename_geometry("segment_geom")
        .to_crs(gdf_waypoints.crs)
    )

    ## Start und endpunkt extrahieren
    gdf["von_pkt_geom"] = gdf.segment_geom.apply(lambda ln: Point(*ln.coords[0]))
    gdf["bis_pkt_geom"] = gdf.segment_geom.apply(lambda ln: Point(*ln.coords[-1]))

    ## Erstellung der GeoDataFrames der Start und Endpunkte der Linien
    gdf_v = gdf[["segment_id", "von_pkt_geom"]].set_geometry("von_pkt_geom")
    gdf_b = gdf[["segment_id", "bis_pkt_geom"]].set_geometry("bis_pkt_geom")
    gdf_v.crs = gdf.crs
    gdf_b.crs = gdf.crs

    ## Joins erstellen
    sj_v = (
        gpd.sjoin_nearest(
            gdf_v,
            gdf_waypoints[["id", "name", "geometry"]],
            how="left"
        )
        .rename(columns={"id": "von_pkt_id", "name": "von_pkt_name"})
        .drop(columns=["index_right"])
    )

    sj_b = (
        gpd.sjoin_nearest(
            gdf_b,
            gdf_waypoints[["id", "name", "geometry"]],
            how="left"
        )
        .rename(columns={"id": "bis_pkt_id", "name": "bis_pkt_name"})
        .drop(columns=["index_right"])
    )

    ## Merge der Waypoints in die Linien GeoDataFrame
    df = (
        gdf
        .merge(sj_v[["segment_id", "von_pkt_name"]], on="segment_id", how="left")
        .merge(sj_b[["segment_id", "bis_pkt_name"]], on="segment_id", how="left")
    )

    ## Resultat-GeoDataFrame
    out = df[[
        "segment_id",
        "von_pkt_name", "von_pkt_geom",
        "bis_pkt_name", "bis_pkt_geom",
        "segment_geom"
    ]]

    out["segment_id"]     = out["segment_id"].astype("Int32")
    out["von_pkt_name"]   = out["von_pkt_name"].astype(str)
    out["bis_pkt_name"]   = out["bis_pkt_name"].astype(str)

    return gpd.GeoDataFrame(out, geometry="segment_geom", crs=gdf.crs)

