import ee
import os
import requests

ee.Initialize()

# Create the local directory if it doesn't exist
out_dir = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\SSL_Patches"
os.makedirs(out_dir, exist_ok=True)

print(f"Created directory: {out_dir}")

# Define a small Area of Interest (Addis Ababa region)
aoi = ee.Geometry.Rectangle([38.5, 8.8, 39.0, 9.3])

# Get Sentinel-2 imagery
s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
    .filterBounds(aoi) \
    .filterDate('2023-01-01', '2023-12-31') \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) \
    .median() \
    .select(['B2', 'B3', 'B4'])

print("Downloading 20 patches directly to local disk...")
for i in range(20):
    # Create a grid of points over the AOI
    x = 38.5 + (i % 5) * 0.05
    y = 8.8 + (i // 5) * 0.05
    point = ee.Geometry.Point([x, y])
    region = point.buffer(1120).bounds() # ~224x224 pixels at 10m res
    
    out_path = os.path.join(out_dir, f"patch_{i}.tif")
    
    try:
        # Generate download URL and save locally
        url = s2.clip(region).getDownloadURL({
            'scale': 10,
            'region': region,
            'format': 'GEO_TIFF'
        })
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(out_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"   Downloaded patch {i+1}/20")
    except Exception as e:
        print(f"   Failed to download patch {i}: {e}")
        
print("\n✅ All patches downloaded successfully!")