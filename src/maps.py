
from PIL import Image
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
import contextily as ctx

from shapely.geometry import LineString
import numpy as np

def generate_elevation_plot(df):
    fig, ax = plt.subplots(figsize=(6, 2))

    dists = []
    elevations = []
    total_dist = 0.0

    for geom in df.geometry:
        if not isinstance(geom, LineString):
            continue
        coords = list(geom.coords)
        for i in range(1, len(coords)):
            prev = coords[i - 1]
            curr = coords[i]
            dx = np.sqrt((curr[0] - prev[0])**2 + (curr[1] - prev[1])**2) / 1000.0  # assuming coords in meters (e.g., EPSG:2056)
            total_dist += dx
            elev = curr[2] if len(curr) == 3 else 0
            dists.append(total_dist)
            elevations.append(elev)

    ax.plot(dists, elevations, marker='o', color='green')
    ax.fill_between(dists, elevations, color='yellow', alpha=0.5)
    ax.set_xlabel("Distanz (km)")
    ax.set_ylabel("Höhe (m ü. M.)")
    ax.set_title("Höhenprofil – Pfadi Wanderung")
    ax.grid(True)
    fig.tight_layout()
    return fig


def generate_route_map(gdf):
    fig, ax = plt.subplots(figsize=(8, 5))
    gdf.plot(ax=ax, column='Abschnittsname', legend=True, linewidth=3)
    ctx.add_basemap(ax, source=ctx.providers.OpenTopoMap)
    ax.set_axis_off()
    fig.tight_layout()
    return fig

def draw_scaled_image(c, img_path, x, y, max_width):
    img = Image.open(img_path)
    width_px, height_px = img.size
    aspect = height_px / width_px
    draw_width = max_width
    draw_height = draw_width * aspect
    c.drawImage(ImageReader(img_path), x, y, width=draw_width, height=draw_height)