import requests
import os

# The direct WCS URL for the Bishoftu dataset
url = "http://www.ethionsdi.gov.et/geoserver/wcs?service=WCS&version=2.0.1&request=GetCoverage&coverageid=geonode:bishoftu20220204&format=image/tiff"
file_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\sample_lasac.tif"

print("Attempting to download from the Ethiopian Geoportal...")
print("This might take 1-2 minutes. Please wait...")

try:
    # We set a long timeout (120 seconds) to wait for the server to package the file
    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()
    
    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    print(f"✅ Success! File saved to {file_path}")
except Exception as e:
    print(f"❌ Failed to download: {e}")