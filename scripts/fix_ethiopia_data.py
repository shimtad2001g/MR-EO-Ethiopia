import ee
import geemap
import rasterio
import os

ee.Initialize()
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\sample_lasac.tif"

if os.path.exists(out_path): os.remove(out_path)

print("Downloading balanced AOI (Mountains + City + River)...")
# Expanded AOI: Entoto Mountains (North) down to the River (South)
roi = ee.Geometry.Rectangle([38.70, 8.90, 38.85, 9.05])

s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
    .filterBounds(roi) \
    .filterDate('2023-01-01', '2023-12-31') \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) \
    .median() \
    .select(['B4', 'B3', 'B2'])

# Download at 20m scale to avoid the 50MB GEE limit
geemap.ee_export_image(s2, filename=out_path, scale=20, region=roi, crs='EPSG:4326', file_per_band=False)
print("✅ Downloaded balanced AOI.")