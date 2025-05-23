
from PIL import Image
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
import contextily as ctx

from shapely.geometry import LineString
import numpy as np
from shapely import wkt

import geopandas as gpd
from shapely import wkt
from shapely.geometry import Point
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.collections as mc
import contextily as ctx
import pandas as pd
import numpy as np

from mpl_toolkits.axes_grid1.inset_locator import inset_axes


def generate_elevation_plot(df):
    fig, ax = plt.subplots(figsize=(10, 3))

    dists = []
    elevations = []
    labels = []
    label_positions = []

    total_dist = 0.0
    started = False

    for idx, row in df.iterrows():
        # Use 'segment_geom' if available, otherwise fallback to 'geometry'
        geom_input = row.get('segment_geom', row.get('geometry'))

        # Convert WKT string to geometry if needed
        if isinstance(geom_input, str):
            geom = wkt.loads(geom_input)
        else:
            geom = geom_input

        if not isinstance(geom, LineString):
            continue

        coords = list(geom.coords)
        segment_start_dist = total_dist

        for i in range(len(coords)):
            curr = coords[i]
            if not started:
                elev = curr[2] if len(curr) == 3 else 0
                dists.append(0.0)
                elevations.append(elev)
                prev = curr
                started = True
                continue

            dx = np.linalg.norm(np.array(curr[:2]) - np.array(prev[:2])) / 1000.0
            total_dist += dx
            elev = curr[2] if len(curr) == 3 else 0
            dists.append(total_dist)
            elevations.append(elev)
            prev = curr

        start_elev = coords[0][2] if len(coords[0]) == 3 else 0
        labels.append((segment_start_dist, start_elev, row.get('von_pkt_name', '')))
        label_positions.append((segment_start_dist, start_elev))

        last_coords = coords

    end_elev = last_coords[-1][2] if len(last_coords[-1]) == 3 else 0
    labels.append((total_dist, end_elev, row.get('bis_pkt_name', '')))
    label_positions.append((total_dist, end_elev))

    ax.plot(dists, elevations, color='green')
    ax.fill_between(dists, elevations, color='yellow', alpha=0.5)

    label_xs, label_ys = zip(*label_positions)
    ax.scatter(label_xs, label_ys, color='green', s=30, zorder=5)

    ax.set_xlabel("Distanz (km)")
    ax.set_ylabel("Höhe (m ü. M.)")
    ax.set_title("Höhenprofil")

    min_elev = min(elevations)
    max_elev = max(elevations)
    buffer = 20  # meters above/below

    # dynamic ylim für platz zwischen box und labels
    label_clearance = 200  # how high above the point labels are placed
    layout_buffer = 100    # extra clearance so labels fit visually

    ax.set_ylim(min_elev - buffer, max_elev + label_clearance + layout_buffer)

    # Generate clean y-ticks only in relevant range
    step = 50  # you can change this to 25 or 20 for finer control
    tick_min = int((min_elev - buffer) // step * step)
    tick_max = int((max_elev + buffer) // step * step + step)

    ax.set_yticks(np.arange(tick_min, tick_max + 1, step))
    fig.subplots_adjust(top=0.8)


    #matplot hat render probleme mit labels, daher hier workaround für shift nach rechts + start/end mit shift nach innen
    for i, (dist, elev, label) in enumerate(labels):
        # Default offset (zentriert)
        x_offset = 5.5
        ha = 'right'

        # Shift start label slightly right   (etwas mehr als ende, wege text render)
        if i == 0:
            x_offset = 13
            ha = 'right'
        
        # Shift end label slightly left
        elif i == len(labels) - 1:
            x_offset = -12
            ha = 'left'

        ax.annotate(
            label,
            xy=(dist, elev),
            xytext=(x_offset, 10),
            textcoords='offset points',
            ha=ha,
            va='bottom',
            fontsize=9,
            rotation=90
        )

    ax.set_xlim(0, total_dist)

    ax.grid(True)
    return fig


def generate_route_map(df):
    df['geometry'] = df['segment_geom'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:2056")

    start_points = gdf.copy()
    start_points['geometry'] = start_points['geometry'].apply(lambda line: Point(line.coords[0]))
    start_points = start_points[['von_pkt_name', 'geometry']].rename(columns={'von_pkt_name': 'name'})

    end_points = gdf.copy()
    end_points['geometry'] = end_points['geometry'].apply(lambda line: Point(line.coords[-1]))
    end_points = end_points[['bis_pkt_name', 'geometry']].rename(columns={'bis_pkt_name': 'name'})

    points = pd.concat([start_points, end_points], ignore_index=True).drop_duplicates()
    points = gpd.GeoDataFrame(points, geometry='geometry', crs="EPSG:2056")

    gdf = gdf.to_crs(epsg=3857)
    points = points.to_crs(epsg=3857)

    fig, ax = plt.subplots(figsize=(10, 7))

    segments = []
    gradients = []

    for line in gdf.geometry:
        coords = list(line.coords)
        for i in range(len(coords) - 1):
            p1, p2 = coords[i], coords[i + 1]
            dx = np.hypot(p2[0] - p1[0], p2[1] - p1[1])
            dz = p2[2] - p1[2] if len(p1) == 3 and len(p2) == 3 else 0
            gradient = (dz / dx) * 100 if dx != 0 else 0

            segments.append([(p1[0], p1[1]), (p2[0], p2[1])])
            gradients.append(gradient)

    norm = colors.Normalize(vmin=min(gradients), vmax=max(gradients))
    cmap = plt.cm.Reds
    lc = mc.LineCollection(segments, cmap=cmap, norm=norm, linewidths=3)
    lc.set_array(np.array(gradients))
    ax.add_collection(lc)

    points.plot(ax=ax, color='skyblue', markersize=25, zorder=5)

    for _, row in points.iterrows():
        ax.annotate(row['name'], xy=(row.geometry.x, row.geometry.y),
                    xytext=(3, 3), textcoords='offset points', fontsize=8)

    try:
        ctx.add_basemap(ax, source=ctx.providers.OpenTopoMap, zoom=14, alpha=0.6)
    except Exception as e:
        print("Basemap konnte nicht hinzugefügt werden:", e)

    # ⛔ Achsenbeschriftung (links/unten) deaktivieren
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # ✅ Gridlines im 1 km-Raster
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    x_ticks = np.arange(int(xlim[0] // 1000) * 1000, int(xlim[1] // 1000 + 1) * 1000, 1000)
    y_ticks = np.arange(int(ylim[0] // 1000) * 1000, int(ylim[1] // 1000 + 1) * 1000, 1000)

    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)
    ax.grid(True, color='gray', linestyle=':', linewidth=0.5)

    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    return fig 

def draw_scaled_image(c, img_path, x, y, max_width):
    img = Image.open(img_path)
    width_px, height_px = img.size
    aspect = height_px / width_px
    draw_width = max_width
    draw_height = draw_width * aspect
    c.drawImage(ImageReader(img_path), x, y, width=draw_width, height=draw_height)