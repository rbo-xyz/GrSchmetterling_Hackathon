import xml.etree.ElementTree as ET
import os

import geopandas as gpd
from shapely.geometry import Point, LineString
import gpxpy
from pyproj import Transformer

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
        pass
    if source == "web":
        pass
    if source == "unknown":
        raise ValueError(f"Datei '{filepath}' ist weder von der Swisstopo-App noch vom Siwsstopo-GIS erstellt worden.")

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



def combine_waypoints_lines():
    pass
