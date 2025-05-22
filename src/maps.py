
from PIL import Image
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
import contextily as ctx

def generate_elevation_plot(gdf, output_path):
    plt.figure(figsize=(6, 2))
    plt.plot(gdf["cumulative_km"], gdf["elevation"], marker='o', color='green')
    plt.fill_between(gdf["cumulative_km"], gdf["elevation"], color='yellow', alpha=0.5)
    plt.xlabel("Distanz (km)")
    plt.ylabel("Höhe (m ü. M.)")
    plt.title("Höhenprofil – Pfadi Wanderung")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def generate_route_map(gdf, output_path):
    ax = gdf.plot(figsize=(8, 5), column='Abschnittsname', legend=True, linewidth=3)
    ctx.add_basemap(ax, source=ctx.providers.OpenTopoMap)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

def draw_scaled_image(c, img_path, x, y, max_width):
    img = Image.open(img_path)
    width_px, height_px = img.size
    aspect = height_px / width_px
    draw_width = max_width
    draw_height = draw_width * aspect
    c.drawImage(ImageReader(img_path), x, y, width=draw_width, height=draw_height)