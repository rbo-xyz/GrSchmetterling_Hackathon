import geopandas as gpd
from shapely import wkt
from shapely.geometry import LineString
import numpy as np
import pandas as pd

def calc_leistungskm (gdf: gpd.GeoDataFrame,
                      pace: float = 4.0):
    
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
        hm = np.sum(h_segs) # in Meter
        
        # Leistungskilometer pro Segement berechnen
        leistungskm_segs = d_segs / 1000.0 + np.absolute(h_segs) / 100.0
        leistungskm = np.sum(leistungskm_segs)

        # Marschzeitberechnung aus den Leistungskilometer
        # default Geschwindigkeit von 4km/h / wird übernommen durch Parameter pace
        mz = round((leistungskm / pace ) * 60, 0) # in Minuten
        # 
        # In Dataframe schreiben
        gdf.at[idx, 'cumulative_km'] = km
        gdf.at[idx, 'elevation'] = hm
        gdf.at[idx, 'Leistungskm [km]'] = leistungskm
        gdf.at[idx, 'Marschzeit [min]'] = mz

        tot_dist = round(np.sum(km),3)
        tot_hm_pos = round(np.sum(h_segs[h_segs > 0]),0)
        tot_hm_neg = round(np.sum(h_segs[h_segs < 0]),0)
        tot_marschzeit_h = int(np.sum(mz/60))
        tot_marschzeit_min = int(round((int(np.sum(mz/60)) - tot_marschzeit_h) * 60))

    return gdf, tot_dist, tot_hm_pos, tot_hm_neg, tot_marschzeit_h, tot_marschzeit_min