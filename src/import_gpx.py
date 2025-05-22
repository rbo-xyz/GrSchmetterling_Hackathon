import xml.etree.ElementTree as ET
import os
import requests
import json

import numpy as np

import geopandas as gpd
from shapely.geometry import Point, LineString, MultiPoint, MultiLineString, mapping
from shapely.ops import linemerge, split
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
        gdf = import_web(filepath)
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

    ## CRS neu setzen
    gdf_waypoints = gdf_waypoints.set_crs(epsg=2056, allow_override=True)
    gdf_lines = gdf_lines.set_crs(epsg=2056, allow_override=True)

    ## Konvertierung der Dataframe für die Ausgabe
    result = combine_waypoints_lines(gdf_lines, gdf_waypoints)

    return result

## <---------------------------------------------------------------------------------------------------------------->
## <---------------------------------------------------------------------------------------------------------------->

def import_web(filepath: str):
    ## Erstellung Waypoints GeoDataFrame
    gdf_waypoints = gpd.read_file(filepath, layer="waypoints", driver="GPX")
    gdf_waypoints['id'] = range(1, len(gdf_waypoints)+1)
    gdf_waypoints = gdf_waypoints.set_crs(epsg=4326, allow_override=True).to_crs(epsg=2056)
    gdf_waypoints["geometry"] = gdf_waypoints.geometry.apply(to_3d_Point)
    gdf_waypoints = gdf_waypoints[["id","name", "geometry"]]

    ## Erstellung des MultiLine Tracks GeoDataFrame
    gdf_routes = gpd.read_file(filepath, layer="routes", driver="GPX")
    gdf_routes = gdf_routes.set_crs(epsg=4326, allow_override=True).to_crs(epsg=2056)
    gdf_routes = gdf_routes[["geometry"]]
    mls = MultiLineString(gdf_routes.geometry.tolist())
    merged  = linemerge(mls)


    ## Aufteilen der Linie in Segmente gemäss den Waypoints
    points = gdf_waypoints.geometry.to_list()
    projected = [merged.interpolate(merged.project(pt)) for pt in points]
    mp = MultiPoint(projected)
    pieces = split(merged, mp)
    segments = list(pieces.geoms)
    gdf_lines = gpd.GeoDataFrame(
        {'geometry': segments}
    )
    gdf_lines['id'] = range(1, len(gdf_lines)+1)

    ## Weitere Stützpunkte den Linestrings hinzufügen
    gdf_lines['geometry'] = gdf_lines.geometry.apply(lambda ln: densify(ln, interval=100.0))

    ## Umdimensionierung der Segmente GeoDataFrame
    gdf_lines = gdf_lines[["id", "geometry"]]

    ## Diese Codestelle kann verwendet werden, wenn jeder Punkt eine Polyline bei der API abgefragt werden soll.
    ## --> Nächster Abschnitt auskommentieren
    # ## Erstellung 3D-LineStrings
    # gdf_lines_3d = gdf_lines.copy()
    # gdf_lines_3d["geometry"] = [to_3d_linestring(line) for line in gdf_lines.geometry]

    ## Diese Codestelle kann verwendet werden, wenn der LineString bei der API abgefragt werden soll. --> schneller
    ## --> letzter Abschnitt auskommentieren
    ## Erstellung 3D-LineStrings via Profile-API (nur 1 Request pro Segment)
    gdf_lines_3d = gdf_lines.copy()
    gdf_lines_3d["geometry"] = gdf_lines.geometry.apply(lambda ln: to_3d_linestring_profile(ln))

    ## CRS neu setzen
    gdf_waypoints = gdf_waypoints.set_crs(epsg=2056, allow_override=True)
    gdf_lines_3d = gdf_lines_3d.set_crs(epsg=2056, allow_override=True)

    ## Konvertierung der Dataframe für die Ausgabe
    result = combine_waypoints_lines(gdf_lines_3d, gdf_waypoints)

    return result

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

    ## Sortierung Kontrolieren
    # Herausfinden von Start und Endpunkt
    all_vons = set(out['von_pkt_name'])
    all_bis  = set(out['bis_pkt_name'])
    start = (all_vons - all_bis).pop()
    end   = (all_bis  - all_vons).pop()
    # Lookup Dictionary aufbauen
    von_index = {row.von_pkt_name: idx for idx, row in out.iterrows()}
    # Topologie-Reihenfolge herstellen
    ordered_idx = []
    current = start
    while current in von_index:
        idx = von_index[current]
        ordered_idx.append(idx)
        current = out.at[idx, 'bis_pkt_name']
    # neu sortieren
    gdf_sorted = out.loc[ordered_idx].reset_index(drop=True)
    gdf_sorted['segment_id'] = gdf_sorted.index + 1
    gdf_sorted = gdf_sorted.set_geometry('segment_geom')

    ## DType anpassen
    gdf_sorted["segment_id"]     = gdf_sorted["segment_id"].astype("int16")
    gdf_sorted["von_pkt_name"]   = gdf_sorted["von_pkt_name"].astype(str)
    gdf_sorted["bis_pkt_name"]   = gdf_sorted["bis_pkt_name"].astype(str)

    return gpd.GeoDataFrame(gdf_sorted, geometry="segment_geom", crs=gdf.crs)

## <---------------------------------------------------------------------------------------------------------------->
## <---------------------------------------------------------------------------------------------------------------->

def to_3d_Point(pt: Point):
    z = get_height(pt.x, pt.y)
    return Point(pt.x, pt.y, z) 

## <---------------------------------------------------------------------------------------------------------------->
## <---------------------------------------------------------------------------------------------------------------->

def get_height(easting: float, 
               northing: float, 
               max_retries: int = 3):
    """
    Fragt die Höhe für einen Punkt (in LV95) bei der Swisstopo-API ab
    und gibt sie als float zurück.
    """
    HEIGHT_URL = "https://api3.geo.admin.ch/rest/services/height"
    params = {"easting": easting, "northing": northing}
    for attempt in range(max_retries):
        r = requests.get(HEIGHT_URL, params=params, timeout=5)
        if r.status_code == 200:
            return r.json()["height"]
    r.raise_for_status()

## <---------------------------------------------------------------------------------------------------------------->
## <---------------------------------------------------------------------------------------------------------------->

def densify(linestring: LineString, 
            interval: float = 100.0):
    
    total_len = linestring.length
    orig_dists = [linestring.project(Point(x, y)) for x, y in linestring.coords]
    regular_dists = list(np.arange(0, total_len, interval))
    regular_dists.append(total_len)
    all_dists = sorted(set(orig_dists + regular_dists))
    pts = [linestring.interpolate(d) for d in all_dists]

    return LineString([(p.x, p.y) for p in pts])

## <---------------------------------------------------------------------------------------------------------------->
## <---------------------------------------------------------------------------------------------------------------->

def to_3d_linestring(line2d: LineString):

    coords2d = list(line2d.coords)
    coords3d = []
    for x, y in coords2d:
        z = get_height(x, y)
        coords3d.append((x, y, z))

    return LineString(coords3d)

## <---------------------------------------------------------------------------------------------------------------->
## <---------------------------------------------------------------------------------------------------------------->

def to_3d_linestring_profile(line2d: LineString,
                             crs: int = 2056,
                             nb_points: int = 42,
                             offset: int | None = None,
                             distinct_points: bool = True,
                             which: str = "COMB"):

    nb_points = len(line2d.coords)
    geom_geojson = mapping(line2d)

    url = "https://api3.geo.admin.ch/rest/services/profile.json"
    params: dict[str, str] = {
        "geom": json.dumps(geom_geojson),
        "sr": str(crs),
        "nb_points": str(nb_points),
        "distinct_points": str(distinct_points).lower(),
    }
    if offset is not None:
        params["offset"] = str(offset)

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()

    profile = r.json()

    coords3d = [
        (pt["easting"], pt["northing"], pt["alts"][which])
        for pt in profile
    ]

    return LineString(coords3d)