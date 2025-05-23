import geopandas as gpd
import pandas as pd

def show(gdf: gpd.GeoDataFrame):
    # Rename and select required columns for the UI
    gdf_show = pd.DataFrame({
        'Abschnitt': gdf['segment_id'],
        'Von': gdf['von_pkt_name'],
        'Nach': gdf['bis_pkt_name'],
        'Laenge [km]': gdf['cumulative_km'].round(2),
        'Hoehenmeter [m]': gdf['elevation'].round(1),
        'Leistungskm': gdf['Leistungskm [km]'].round(2),
        'Marschzeit [min]': gdf['Marschzeit [min]'].round(0),
        'Hinweis': ""  # Add an empty 'Hinweis' column
    })

    return gdf_show
