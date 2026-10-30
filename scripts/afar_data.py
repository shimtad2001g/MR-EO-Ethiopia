import ee
import geemap
import rasterio
import os

ee.Initialize()
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\afar_image.tif"

if os.path.exists(out_path): os.remove(out_path)

print("Downloading Afar Region (Arid Zone)...")
# Semera / Afar coordinates
roi = ee.Geometry.Rectangle([40.80, 11.60, 41.00, 11.80])

s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
    .filterBounds(roi) \
    .filterDate('2023-01-01', '2023-12-31') \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) \
    .median() \
    .select(['B4', 'B3', 'B2'])

geemap.ee_export_image(s2, filename=out_path, scale=20, region=roi, crs='EPSG:4326', file_per_band=False)

if os.path.exists(out_path):
    print(f"✅ Success! Afar image downloaded.")