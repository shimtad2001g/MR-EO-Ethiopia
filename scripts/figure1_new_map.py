import rasterio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib_scalebar.scalebar import ScaleBar

print("GENERATING THE NEW BRIGHT MAP...")

img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\s2_aligned.tif"

with rasterio.open(img_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)
    bounds = src.bounds
    crs = src.crs
    
    # Contrast Stretch to make the city bright
    p2, p98 = np.percentile(img, (2, 98))
    img_rgb = np.clip((img - p2) / (p98 - p2), 0, 1)

fig, ax = plt.subplots(figsize=(12, 10))
ax.imshow(img_rgb, extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])

# Correct Axis
ax.set_xlabel("Longitude (°E)", fontsize=14, fontweight='bold')
ax.set_ylabel("Latitude (°N)", fontsize=14, fontweight='bold')
plt.title("UPDATED Study Area Map: Addis Ababa", fontsize=18, fontweight='bold', pad=20)

# Correct Scale Bar
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

# Correct Legend
legend_elements = [
    Rectangle((0,0), 1, 1, facecolor='#FF0000', edgecolor='black', label='Band 4 (Red)'),
    Rectangle((0,0), 1, 1, facecolor='#00FF00', edgecolor='black', label='Band 3 (Green)'),
    Rectangle((0,0), 1, 1, facecolor='#0000FF', edgecolor='black', label='Band 2 (Blue)')
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=12, 
          title="Sentinel-2 Bands", title_fontsize=13,
          framealpha=0.9, edgecolor='black')

# Metadata (No overlap)
metadata_text = f"Projection: {crs.to_string()}\nData Source: Sentinel-2 SR (GEE)\nProject: SSGI Project No. 12"
ax.text(0.02, 0.02, metadata_text, transform=ax.transAxes, fontsize=11,
        verticalalignment='bottom', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='black'),
        color='black', fontfamily='monospace')

ax.grid(color='white', linestyle='--', linewidth=1, alpha=0.4)

# NEW FILE NAME SO YOU KNOW IT'S THE NEW ONE
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_1_UPDATED_MAP.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"✅ NEW MAP SUCCESSFULLY SAVED TO: {out_path}")