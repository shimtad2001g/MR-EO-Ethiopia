import ee
import geemap
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os

print("Downloading NDVI Data from GEE...")
ee.Initialize()

# Same AOI as the main project
wgs84_bounds = [38.70, 8.90, 38.85, 9.05]
roi = ee.Geometry.Rectangle(wgs84_bounds)

# Fetch Sentinel-2 and calculate NDVI (B8 = NIR, B4 = Red)
s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
    .filterBounds(roi).filterDate('2023-01-01', '2023-12-31') \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)).median()

ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI')

out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\ndvi.tif"
if not os.path.exists(out_path):
    geemap.ee_export_image(ndvi, filename=out_path, scale=20, region=roi, crs='EPSG:4326')

print("Generating Publication-Ready Figure 6: NDVI Map...")
with rasterio.open(out_path) as src:
    ndvi_data = src.read(1)
    bounds = src.bounds
    crs = src.crs

fig, ax = plt.subplots(figsize=(12, 10))

# Plot NDVI with a professional Red-Yellow-Green colormap
im = ax.imshow(ndvi_data, extent=[bounds.left, bounds.right, bounds.bottom, bounds.top], 
               cmap='RdYlGn', vmin=-0.2, vmax=0.8)

# Add Colorbar
cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('NDVI Value (Vegetation Health)', fontsize=14, fontweight='bold', labelpad=15)
cbar.ax.tick_params(labelsize=12)

# Labels and Title
ax.set_xlabel("Longitude (°E)", fontsize=14, fontweight='bold')
ax.set_ylabel("Latitude (°N)", fontsize=14, fontweight='bold')
plt.title("Figure 6: NDVI (Vegetation Health) Map\n(Addis Ababa, Ethiopia)", 
          fontsize=18, fontweight='bold', pad=20)

# --- CUSTOM SCALE BAR (1 km) ---
deg_per_km = 1.0 / 111.32 
x_start = bounds.right - (bounds.right - bounds.left) * 0.1
y_pos = bounds.bottom + (bounds.top - bounds.bottom) * 0.05
x_end = x_start - deg_per_km
ax.plot([x_end, x_start], [y_pos, y_pos], color='black', linewidth=6, solid_capstyle='butt', zorder=10)
ax.plot([x_end, x_end + (deg_per_km/2)], [y_pos, y_pos], color='white', linewidth=6, solid_capstyle='butt', zorder=10)
ax.text(x_start - (deg_per_km/2), y_pos + 0.001, "1 km", ha='center', va='bottom', fontsize=12, fontweight='bold', 
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=2), zorder=10)

# North Arrow
x, y, arrow_length = 0.95, 0.95, 0.08
ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='black', width=5, headwidth=15),
            ha='center', va='center', fontsize=18, fontweight='bold', 
            xycoords=ax.transAxes, zorder=10)

# Metadata Box
metadata_text = f"Projection: {crs.to_string()}\nData Source: Sentinel-2 SR (GEE)\nProject: SSGI Project No. 12"
ax.text(0.02, 0.02, metadata_text, transform=ax.transAxes, fontsize=11,
        verticalalignment='bottom', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9, edgecolor='black'),
        color='black', fontfamily='monospace', zorder=10)

# Grid and Border
ax.grid(color='black', linestyle='--', linewidth=1, alpha=0.3)
ax.add_patch(Rectangle((bounds.left, bounds.bottom), 
                       bounds.right - bounds.left, 
                       bounds.top - bounds.bottom, 
                       fill=False, edgecolor='black', linewidth=2, zorder=11))

plt.tight_layout()
out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_6_Publication_NDVI.png"
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ Figure 6 successfully saved to: {out_img}")