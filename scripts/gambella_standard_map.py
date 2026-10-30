import rasterio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, Patch

print("Generating Global Standard Cartographic Map for Gambella...")

# 1. Load the Gambella image
img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\gambella_image.tif"

with rasterio.open(img_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)
    bounds = src.bounds
    crs = src.crs
    
    # Apply Contrast Stretch
    p2, p98 = np.percentile(img, (2, 98))
    img_rgb = np.clip((img - p2) / (p98 - p2), 0, 1)

# 2. Setup the Figure
fig, ax = plt.subplots(figsize=(12, 10))
ax.imshow(img_rgb, extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])

# 3. Axis Labels
ax.set_xlabel("Longitude (°E)", fontsize=14, fontweight='bold')
ax.set_ylabel("Latitude (°N)", fontsize=14, fontweight='bold')

# 4. Title
plt.title("Study Area: Gambella Region, Ethiopia\nSentinel-2 True Color Composite", 
          fontsize=18, fontweight='bold', pad=20)

# 5. Custom Scale Bar (Bottom Right)
deg_per_km = 1.0 / 111.32 
x_start = bounds.right - (bounds.right - bounds.left) * 0.15
y_pos = bounds.bottom + (bounds.top - bounds.bottom) * 0.05
x_end = x_start - deg_per_km

ax.plot([x_end, x_start], [y_pos, y_pos], color='black', linewidth=6, solid_capstyle='butt', zorder=10)
ax.plot([x_end, x_end + (deg_per_km/2)], [y_pos, y_pos], color='white', linewidth=6, solid_capstyle='butt', zorder=10)
ax.text(x_start - (deg_per_km/2), y_pos + 0.001, "1 km", ha='center', va='bottom', fontsize=12, fontweight='bold', 
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2), zorder=10)

# 6. North Arrow (Top Right)
x, y, arrow_length = 0.95, 0.95, 0.08
ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=18, fontweight='bold', 
            xycoords=ax.transAxes, zorder=10)

# 7. Spectral Band Legend (Top Left)
legend_elements = [
    Rectangle((0,0), 1, 1, facecolor='#FF0000', edgecolor='black', label='Band 4 (Red)'),
    Rectangle((0,0), 1, 1, facecolor='#00FF00', edgecolor='black', label='Band 3 (Green)'),
    Rectangle((0,0), 1, 1, facecolor='#0000FF', edgecolor='black', label='Band 2 (Blue)')
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=12, 
          title="Sentinel-2 Bands", title_fontsize=13,
          framealpha=0.9, edgecolor='black')

# 8. Metadata Box (Bottom Left)
metadata_text = (
    f"Projection: {crs.to_string()}\n"
    f"Data Source: Sentinel-2 SR (GEE)\n"
    f"Author: Shimeles Tadesse Zelelew\n"
    f"Date: October 2026"
)
ax.text(0.02, 0.02, metadata_text, transform=ax.transAxes, fontsize=11,
        verticalalignment='bottom', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='black'),
        color='black', fontfamily='monospace', zorder=10)

# 9. Grid and Neatline (Border)
ax.grid(color='white', linestyle='--', linewidth=1, alpha=0.4)
ax.add_patch(Rectangle((bounds.left, bounds.bottom), 
                       bounds.right - bounds.left, 
                       bounds.top - bounds.bottom, 
                       fill=False, edgecolor='black', linewidth=2, zorder=11))

plt.tight_layout()

# 10. Save
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Gambella_Standard_Map_Final.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"✅ Standard Map successfully saved to: {out_path}")