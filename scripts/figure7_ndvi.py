import ee
import geemap
import rasterio
import numpy as np
import matplotlib.pyplot as plt

print("Downloading NDVI Data from GEE...")
ee.Initialize()

wgs84_bounds = [38.70, 8.90, 38.85, 9.05]
roi = ee.Geometry.Rectangle(wgs84_bounds)

# Fetch Sentinel-2 and calculate NDVI (B8 = NIR, B4 = Red)
s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
    .filterBounds(roi).filterDate('2023-01-01', '2023-12-31') \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)).median()

ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI')

out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\ndvi.tif"
geemap.ee_export_image(ndvi, filename=out_path, scale=20, region=roi, crs='EPSG:4326')

print("Generating NDVI Map...")
with rasterio.open(out_path) as src:
    ndvi_data = src.read(1)

fig, ax = plt.subplots(figsize=(12, 10))
im = ax.imshow(ndvi_data, cmap='RdYlGn', vmin=-0.2, vmax=0.8)
cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('NDVI Value', fontsize=14)

ax.set_title('Figure 7: NDVI (Vegetation Health) of Addis Ababa', fontsize=16, fontweight='bold')
ax.axis('off')

plt.tight_layout()
out_path_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_7_NDVI_Map.png"
plt.savefig(out_path_img, dpi=300, bbox_inches='tight')
print(f"✅ Figure 7 saved to: {out_path_img}")