
from PIL import Image
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
import contextily as ctx

from shapely.geometry import LineString
import numpy as np

from shapely.geometry import LineString
from shapely import wkt
import matplotlib.pyplot as plt
import numpy as np

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

    max_elev = max(elevations)
    ax.set_ylim(top=max_elev + 700)
    fig.subplots_adjust(top=0.8)

    for dist, elev, label in labels:
        ax.text(
            dist, elev + 60, label,
            ha='left',
            va='center',
            fontsize=9,
            rotation=90,
            rotation_mode='anchor',
            clip_on=False
        )

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