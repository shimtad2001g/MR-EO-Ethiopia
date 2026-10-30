import rasterio
import os

file_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\sample_lasac.tif"

if os.path.exists(file_path):
    print("✅ File found! Reading spatial metadata...")
    with rasterio.open(file_path) as src:
        print(f"Bounds: {src.bounds}")
        print(f"CRS (Coordinate System): {src.crs}")
        print(f"Resolution (Pixel Size): {src.res}")
        print(f"Dimensions: {src.width} x {src.height} pixels")
        print(f"Number of Bands: {src.count}")
else:
    print(f"❌ File NOT found at {file_path}. Please check the download and file name.")