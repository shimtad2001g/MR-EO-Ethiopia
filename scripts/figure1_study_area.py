import rasterio
import matplotlib.pyplot as plt
import numpy as np
from rasterio.warp import transform_bounds

print("Generating Figure 1: Study Area Map...")

# Load image
img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\s2_aligned.tif"
with rasterio.open(img_path) as src:
    img = src.read([1, 2, 3])
    img = np.moveaxis(img, 0, -1)
    img_rgb = np.clip(img / 10000.0, 0, 1)
    
    # Get bounds in WGS84 (Lat/Lon) for the axes
    bounds = src.bounds
    crs = src.crs
    wgs84_bounds = transform_bounds(crs, 'EPSG:4326', bounds.left, bounds.bottom, bounds.right, bounds.top)

fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(img_rgb, extent=[wgs84_bounds[0], wgs84_bounds[2], wgs84_bounds[1], wgs84_bounds[3]])

ax.set_title("Figure 1: Study Area Map - Addis Ababa, Ethiopia", fontsize=16, fontweight='bold')
ax.set_xlabel("Longitude (°E)", fontsize=12)
ax.set_ylabel("Latitude (°N)", fontsize=12)

# Add grid lines for a professional map look
ax.grid(color='white', linestyle='--', linewidth=1, alpha=0.5)

# Add a north arrow
x, y, arrow_length = 0.95, 0.95, 0.1
ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=14, xycoords=ax.transAxes)

plt.tight_layout()
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_1_Study_Area.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"✅ Figure 1 saved to: {out_path}")