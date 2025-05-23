
from PIL import Image
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
import contextily as ctx

from shapely.geometry import LineString
import numpy as np
from shapely import wkt
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