
from PIL import Image
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
import contextily as ctx
from shapely import wkt
from shapely.geometry import LineString
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
        geom = wkt.loads(row['segment_geom'])
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

            dx = np.linalg.norm(np.array(curr[:2]) - np.array(prev[:2])) / 1000.0  # meters to km
            total_dist += dx
            elev = curr[2] if len(curr) == 3 else 0
            dists.append(total_dist)
            elevations.append(elev)
            prev = curr

        # Label the start of the segment with von_pkt_name
        start_elev = coords[0][2] if len(coords[0]) == 3 else 0
        labels.append((segment_start_dist, start_elev, row['von_pkt_name']))
        label_positions.append((segment_start_dist, start_elev))

        # Save last coordinates for labeling the end later
        last_coords = coords

    # Add final label at the end of the last segment
    end_elev = last_coords[-1][2] if len(last_coords[-1]) == 3 else 0
    labels.append((total_dist, end_elev, row['bis_pkt_name']))
    label_positions.append((total_dist, end_elev))

    # Plot elevation profile
    ax.plot(dists, elevations, color='green')
    ax.fill_between(dists, elevations, color='yellow', alpha=0.5)

    # Mark labeled points
    label_xs, label_ys = zip(*label_positions)
    ax.scatter(label_xs, label_ys, color='green', s=30, zorder=5)

    ax.set_xlabel("Distanz (km)")
    ax.set_ylabel("Höhe (m ü. M.)")
    ax.set_title("Höhenprofil")

    # Dynamic vertical space for label rotation
    max_elev = max(elevations)
    label_padding = 700
    ax.set_ylim(top=max_elev + label_padding)

    fig.subplots_adjust(top=0.8)

    # label_offset = 20  # meters above the point

    for dist, elev, label in labels:
        ax.text(
            dist, elev + 30, label,
            ha='left',           # shift start of rotated label over the point
            va='center',
            fontsize=9,
            rotation=90,
            rotation_mode='anchor',
            clip_on=False
        )

    ax.grid(True)
    # fig.tight_layout()
    plt.show()
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