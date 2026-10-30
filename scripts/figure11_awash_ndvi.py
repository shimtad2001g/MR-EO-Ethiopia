import ee
import geemap
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os

print("Generating Pre-print Standard Figure 11: Awash NDVI Map...")

ee.Initialize()
# Upper Awash Basin AOI
wgs84_bounds = [39.75, 8.85, 39.90, 9.00] 
roi = ee.Geometry.Rectangle(wgs84_bounds)

# Fetch Sentinel-2 and calculate NDVI
s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
    .filterBounds(roi).filterDate('2023-01-01', '2023-12-31') \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)).median()

ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI')

out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\ndvi_awash.tif"
if not os.path.exists(out_path):
    print("Downloading Awash NDVI data from GEE (this takes a few seconds)...")
    geemap.ee_export_image(ndvi, filename=out_path, scale=20, region=roi, crs='EPSG:4326')

with rasterio.open(out_path) as src:
    ndvi_data = src.read(1)
    bounds = src.bounds
    crs = src.crs

fig, ax = plt.subplots(figsize=(12, 10))

# Plot NDVI with professional Red-Yellow-Green colormap
im = ax.imshow(ndvi_data, extent=[bounds.left, bounds.right, bounds.bottom, bounds.top], 
               cmap='RdYlGn', vmin=-0.2, vmax=0.8)

# Colorbar
cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('NDVI Value (Vegetation Health)', fontsize=14, fontweight='bold', labelpad=15)
cbar.ax.tick_params(labelsize=12)

# Labels and Title
ax.set_xlabel("Longitude (°E)", fontsize=14, fontweight='bold')
ax.set_ylabel("Latitude (°N)", fontsize=14, fontweight='bold')
plt.title("NDVI (Vegetation Health) Map\n(Upper Awash Basin, Ethiopia)", 
          fontsize=18, fontweight='bold', pad=20)

# 1. Custom Scale Bar (1 km)
deg_per_km = 1.0 / 111.32 
x_start = bounds.right - (bounds.right - bounds.left) * 0.1
y_pos = bounds.bottom + (bounds.top - bounds.bottom) * 0.05
x_end = x_start - deg_per_km

ax.plot([x_end, x_start], [y_pos, y_pos], color='black', linewidth=6, solid_capstyle='butt', zorder=10)
ax.plot([x_end, x_end + (deg_per_km/2)], [y_pos, y_pos], color='white', linewidth=6, solid_capstyle='butt', zorder=10)
ax.text(x_start - (deg_per_km/2), y_pos + 0.001, "1 km", ha='center', va='bottom', fontsize=12, fontweight='bold', 
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2), zorder=10)

# 2. North Arrow
ax.annotate('N', xy=(0.95, 0.95), xytext=(0.95, 0.87),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=18, fontweight='bold', 
            xycoords=ax.transAxes, zorder=10)

# 3. Metadata Box (Top Left)
metadata_text = f"Projection: {crs.to_string()}\nData Source: Sentinel-2 SR (GEE)\nAuthor: Shimeles T. Zelelew"
ax.text(0.02, 0.98, metadata_text, transform=ax.transAxes, fontsize=11,
        verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='black'),
        color='black', fontfamily='monospace', zorder=10)

# 4. Grid and Neatline
ax.grid(color='black', linestyle='--', linewidth=1, alpha=0.3)
ax.add_patch(Rectangle((bounds.left, bounds.bottom), 
                       bounds.right - bounds.left, 
                       bounds.top - bounds.bottom, 
                       fill=False, edgecolor='black', linewidth=2, zorder=11))

plt.tight_layout()

out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_11_Awash_NDVI.png"
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ SUCCESS! Figure 11 saved to: {out_img}")