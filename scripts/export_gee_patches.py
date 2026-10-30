import ee

ee.Initialize()

# Define an Area of Interest (a broad box over Ethiopia)
aoi = ee.Geometry.Rectangle([37.0, 8.0, 39.0, 10.0])

# Get a cloud-free Sentinel-2 composite
s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
    .filterBounds(aoi) \
    .filterDate('2023-01-01', '2023-12-31') \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) \
    .median() \
    .select(['B2', 'B3', 'B4'])

# Generate 50 random points in the AOI
points = ee.FeatureCollection.randomPoints(aoi, 50)
points_list = points.toList(50)

print("Submitting export tasks to Google Drive...")
for i in range(50):
    point = ee.Feature(points_list.get(i))
    coord = point.geometry().coordinates().getInfo()
    
    # Create a 256x256 pixel box around the point
    patch = ee.Geometry.Point(coord).buffer(1280).bounds() 
    
    task = ee.batch.Export.image.toDrive(
        image=s2.clip(patch),
        description=f'ssl_patch_{i}',
        folder='SSL_Patches',
        scale=10,
        region=patch,
        fileFormat='GeoTIFF'
    )
    task.start()
    print(f"Started export task {i+1}/50")

print("All tasks submitted! Check your Google Drive in a few minutes.")