import ee
import geemap
import os
import rasterio

ee.Initialize()
out_dir = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\SSL_Large_Patches"
os.makedirs(out_dir, exist_ok=True)

regions = [
    [38.70, 8.90, 38.80, 9.00], [38.75, 8.55, 38.85, 8.65], 
    [40.00, 8.50, 40.10, 8.60], [37.50, 7.50, 37.60, 7.60], 
    [39.60, 9.60, 39.70, 9.70], [36.50, 9.50, 36.60, 9.60], 
    [38.40, 7.00, 38.50, 7.10], [39.00, 11.50, 39.10, 11.60], 
    [37.00, 11.50, 37.10, 11.60], [35.50, 9.50, 35.60, 9.60]
]

print("Downloading 10 large Ethiopian tiles to local disk...")
for i, box in enumerate(regions):
    roi = ee.Geometry.Rectangle(box)
    s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(roi).filterDate('2023-01-01', '2023-12-31') \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) \
        .median().select(['B4', 'B3', 'B2'])
        
    out_path = os.path.join(out_dir, f'tile_{i}.tif')
    try:
        geemap.ee_export_image(s2, filename=out_path, scale=20, region=roi, crs='EPSG:4326')
        print(f"✅ Downloaded tile {i+1}/10")
    except Exception as e:
        print(f"❌ Failed tile {i}: {e}")