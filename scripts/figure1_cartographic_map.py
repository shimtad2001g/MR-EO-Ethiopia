import rasterio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib_scalebar.scalebar import ScaleBar
import os

print("Generating Cartographically Accurate Study Area Map...")

img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\s2_aligned.tif"

with rasterio.open(img_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)
    bounds = src.bounds
    crs = src.crs
    
    # Contrast Stretch (Makes the image brighter)
    p2, p98 = np.percentile(img, (2, 98))
    img_rgb = np.clip((img - p2) / (p98 - p2), 0, 1)

fig, ax = plt.subplots(figsize=(12, 10))
ax.imshow(img_rgb, extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])

# Correct Axis Labels
ax.set_xlabel("Longitude (°E)", fontsize=14, fontweight='bold')
ax.set_ylabel("Latitude (°N)", fontsize=14, fontweight='bold')

# Title
plt.title("Study Area Map: Addis Ababa, Ethiopia\nSentinel-2 True Color Composite", 
          fontsize=18, fontweight='bold', pad=20)

# Correct Scale Bar for Geographic Coordinates
meters_per_degree = 111320.0
width_meters = (bounds.right - bounds.left) * meters_per_degree
meters_per_pixel = width_meters / img.shape[1]
scalebar = ScaleBar(dx=meters_per_pixel, units='m', location='lower right', 
                    length_fraction=0.25, box_alpha=0.8, 
                    color='black', font_properties={'size': 12, 'weight': 'bold'})
ax.add_artist(scalebar)

# North Arrow
x, y, arrow_length = 0.95, 0.95, 0.08
ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=18, fontweight='bold', 
            xycoords=ax.transAxes)

# COMPATIBLE LEGEND (Explains the RGB bands instead of fake solid colors)
legend_elements = [
    Rectangle((0,0), 1, 1, facecolor='#FF0000', edgecolor='black', label='Band 4 (Red)'),
    Rectangle((0,0), 1, 1, facecolor='#00FF00', edgecolor='black', label='Band 3 (Green)'),
    Rectangle((0,0), 1, 1, facecolor='#0000FF', edgecolor='black', label='Band 2 (Blue)')
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=12, 
          title="Sentinel-2 Bands", title_fontsize=13,
          framealpha=0.9, edgecolor='black')

# Metadata Box (Moved to avoid overlap)
metadata_text = (
    f"Projection: {crs.to_string()}\n"
    f"Data Source: Sentinel-2 SR (GEE)\n"
    f"Project: SSGI Project No. 12\n"
    f"Author: Shimeles T. Zelelew\n"
    f"Date: October 2026"
)
ax.text(0.02, 0.02, metadata_text, transform=ax.transAxes, fontsize=11,
        verticalalignment='bottom', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='black'),
        color='black', fontfamily='monospace')

ax.grid(color='white', linestyle='--', linewidth=1, alpha=0.4)
ax.add_patch(Rectangle((bounds.left, bounds.bottom), 
                       bounds.right - bounds.left, 
                       bounds.top - bounds.bottom, 
                       fill=False, edgecolor='black', linewidth=2))

plt.tight_layout()
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_1_Professional_Map.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"✅ Accurate Map saved to: {out_path}")