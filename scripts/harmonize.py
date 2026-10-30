import ee
import geemap
import rasterio
from rasterio.warp import transform_bounds
import os

# Initialize GEE
ee.Initialize()

# Paths
lasac_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\sample_lasac.tif"
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\s2_aligned.tif"

print("1. Reading local file metadata...")
with rasterio.open(lasac_path) as src:
    bounds = src.bounds
    crs = src.crs
    width = src.width
    height = src.height

print(f"   Bounds (UTM): {bounds}")

print("\n2. Translating coordinates to WGS84 (Lat/Lon) for GEE...")
# GEE requires region coordinates in EPSG:4326 (Longitude/Latitude)
wgs84_bounds = transform_bounds(crs, 'EPSG:4326', bounds.left, bounds.bottom, bounds.right, bounds.top)
roi = ee.Geometry.Rectangle(wgs84_bounds)

print("\n3. Requesting Sentinel-2 data from GEE...")
s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
    .filterBounds(roi) \
    .filterDate('2020-01-01', '2025-01-01') \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 50)) \
    .median() \
    .select(['B2', 'B3', 'B4']) \
    .clip(roi)

print("\n4. Downloading and aligning Sentinel-2 back to local UTM grid...")
try:
    geemap.ee_export_image(
        s2,
        filename=out_path,
        scale=10,
        region=roi,
        crs=crs.to_string(), # Tells GEE to save the file in your local UTM projection
        file_per_band=False
    )
    
    # Verify the file actually exists
    if os.path.exists(out_path):
        print(f"\n✅ Harmonization complete! Aligned file saved to: {out_path}")
        with rasterio.open(out_path) as src:
            print(f"   Aligned Bounds: {src.bounds}")
            print(f"   Aligned CRS: {src.crs}")
            print(f"   Aligned Dimensions: {src.width} x {src.height}")
            print(f"   Aligned Bands: {src.count}")
    else:
        print("\n❌ Download failed. GEE did not return a file.")

except Exception as e:
    print(f"\n❌ Download failed. Error: {e}")