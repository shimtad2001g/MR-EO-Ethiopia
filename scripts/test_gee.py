import ee

# Initialize the Earth Engine API
try:
    ee.Initialize()
    print("✅ GEE successfully initialized!")
except Exception as e:
    print("\n❌ Error initializing GEE. You likely need to provide a Google Cloud Project ID.")
    print(f"Error details: {e}")
    print("\nTo fix this, run: ee.Initialize(project='your-google-cloud-project-id')")
    exit() # Stop the script here if initialization fails

# Test fetching a small piece of free data (Sentinel-2 image over Addis Ababa)
print("\nFetching a sample Sentinel-2 image over Addis Ababa...")
addis_coords = ee.Geometry.Point([38.7578, 9.0192]) # Longitude, Latitude
s2_image = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
    .filterBounds(addis_coords) \
    .filterDate('2024-01-01', '2024-02-01') \
    .first()

# Get the ID of the image to prove we can access the cloud catalog
image_id = s2_image.getInfo()['id']
print(f"✅ Successfully accessed GEE Data! Sample Image ID: {image_id}")