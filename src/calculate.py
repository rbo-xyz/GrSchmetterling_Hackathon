import geopandas as gpd
from shapely import wkt
from shapely.geometry import LineString
import numpy as np
import pandas as pd

def calc_leistungskm (gdf):
    for idx, row in gdf.iterrows():
        line = row.geometry
        
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
        # default Geschwindigkeit von 4km/h
        mz = round((leistungskm / 4 ) * 60, 0) # in Minuten
        
        # In Dataframe schreiben
        gdf.at[idx, 'Laenge [km]'] = km
        gdf.at[idx, 'Hoehendiffernez hm [m]'] = hm
        gdf.at[idx, 'Leistungskm [km]'] = leistungskm
        gdf.at[idx, 'Marschzeit [min]'] = mz

        tot_dist = np.sum(km)
        tot_hm_pos = np.sum(hm<0)
        tot_hm_neg = np.sum(hm>0)
        tot_marschzeit = np.sum(mz)

    return gdf, tot_dist, tot_hm_pos, tot_hm_neg, tot_marschzeit