import geopandas as gpd
from shapely import wkt
from shapely.geometry import LineString
import numpy as np
import pandas as pd

def calc_leistungskm (gdf: gpd.GeoDataFrame,
                      pace: float = 4.0):
    """
    Berechnet verschiedene Strecken- und Höhenmetriken sowie die Marschzeit für jedes Segment in einem GeoDataFrame.

    Für jedes Segment (LineString mit 3D-Koordinaten) werden folgende Werte berechnet und als neue Spalten im GeoDataFrame gespeichert:
        - cumulative_km: Gesamtlänge des Segments in Kilometern
        - elevation: Gesamte Höhendifferenz des Segments in Metern
        - Leistungskm [km]: Leistungskilometer des Segments (Distanz + Höhenmeter)
        - Marschzeit [min]: Marschzeit für das Segment in Minuten (basierend auf pace)

    Zusätzlich werden folgende Gesamtwerte zurückgegeben:
        - tot_dist: Gesamtdistanz aller Segmente in Kilometern
        - tot_hm_pos: Summe aller positiven Höhenmeter
        - tot_hm_neg: Summe aller negativen Höhenmeter
        - tot_marschzeit_h: Gesamte Marschzeit (Stundenanteil)
        - tot_marschzeit_min: Gesamte Marschzeit (Minutenanteil)

    Parameter:
        gdf (gpd.GeoDataFrame): GeoDataFrame mit einer Spalte 'segment_geom' (LineString mit 3D-Koordinaten)
        pace (float): Geschwindigkeit in km/h (Standard: 4.0)

    Returns:
        Tuple:
            - gdf (gpd.GeoDataFrame): GeoDataFrame mit neuen Spalten
            - tot_dist (float): Gesamtdistanz in km
            - tot_hm_pos (float): Summe positiver Höhenmeter
            - tot_hm_neg (float): Summe negativer Höhenmeter
            - tot_marschzeit_h (int): Marschzeit Stundenanteil
            - tot_marschzeit_min (int): Marschzeit Minutenanteil
    """
    #definition leere Variablen für for-schleife
    tot_hm_pos = 0
    tot_hm_neg = 0


    for idx, row in gdf.iterrows():
        line = row.segment_geom
        
        coords = np.array(line.coords)  # extrahiert die Koordinaten als NumPy-Array
        
        # Distanzdifferenz berechnen des Segements
        delta_xy = np.diff(coords[:, :2], axis=0)
        d_segs = np.linalg.norm(delta_xy, axis=1)  # in Meter
        km = np.sum(d_segs) / 1000.0 # in Kilometer
        
        # Hoehendiffernzen berechnen des Segments
        delta_z = np.diff(coords[:, 2])
        h_segs = delta_z.copy()
        hm = round(np.sum(h_segs),0) # in Meter
        
        # Leistungskilometer pro Segement berechnen
        leistungskm_segs = d_segs / 1000.0 + np.absolute(h_segs) / 100.0
        leistungskm = np.sum(leistungskm_segs)

        # Marschzeitberechnung aus den Leistungskilometer
        # default Geschwindigkeit von 4km/h / wird übernommen durch Parameter pace
        mz = round((leistungskm / pace ) * 60,0) # in Minuten
        # 
        # In Dataframe schreiben

        gdf.at[idx, 'cumulative_km'] = km
        gdf.at[idx, 'elevation'] = hm
        gdf.at[idx, 'Leistungskm [km]'] = leistungskm
        gdf.at[idx, 'Marschzeit [min]'] = mz

        #totale Höhendifferenz berechnen
        tot_hm_pos += np.sum(h_segs[h_segs > 0])
        tot_hm_neg += np.sum(h_segs[h_segs < 0])

    # erstellen von Liste aus df Spalten

    km_List = gdf['cumulative_km'].tolist()
    # hm_List = gdf['elevation'].tolist()
    leistungskm_List = gdf['Leistungskm [km]'].tolist()
    mz_List = gdf['Marschzeit [min]'].tolist()
        
    # Berechnungen von Marschzeit und Leistungskilometer
    tot_dist = round(np.sum(km_List),3)
    tot_lkm = round(np.sum(leistungskm_List),3)
    tot_hm_pos = round(tot_hm_pos)
    tot_hm_neg = round(tot_hm_neg)
    tot_marschzeit_h = int(np.sum(mz_List)/60)
    tot_marschzeit_min = int(round((int(np.sum(mz_List)) - tot_marschzeit_h * 60)))

    return gdf, tot_dist, tot_lkm, tot_hm_pos, tot_hm_neg, tot_marschzeit_h, tot_marschzeit_min