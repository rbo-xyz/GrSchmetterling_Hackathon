
from PIL import Image
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
import contextily as ctx

def generate_elevation_plot(df):
    fig, ax = plt.subplots(figsize=(6, 2))
    ax.plot(df["Distanz km"], df["Höhe m.ü.M."], marker='o', color='green')
    ax.fill_between(df["Distanz km"], df["Höhe m.ü.M."], color='yellow', alpha=0.5)
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