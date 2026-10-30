import ee
import geemap
import rasterio
import os

ee.Initialize()
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\gambella_image.tif"

if os.path.exists(out_path): os.remove(out_path)

print("Downloading Gambella (Forest Zone)...")
# Gambella coordinates
roi = ee.Geometry.Rectangle([34.50, 7.80, 34.70, 8.00])

s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
    .filterBounds(roi) \
    .filterDate('2023-01-01', '2023-12-31') \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) \
    .median() \
    .select(['B4', 'B3', 'B2'])

geemap.ee_export_image(s2, filename=out_path, scale=20, region=roi, crs='EPSG:4326', file_per_band=False)

if os.path.exists(out_path):
    print(f"✅ Success! Gambella image downloaded.")