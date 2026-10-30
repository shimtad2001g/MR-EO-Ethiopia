import requests
import rasterio
from rasterio.io import MemoryFile
import os

# WCS Endpoint and Parameters for SSGI LASAC
wcs_url = "http://www.ethionsdi.gov.et/geoserver/wcs"
params = {
    "service": "WCS",
    "version": "2.0.1",
    "request": "GetCoverage",
    "coverageid": "geonode:bishoftu20220204", # Real SSGI layer
    "format": "image/tiff"
}

out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\data\sample_lasac.tif"

print("Requesting REAL SSGI LASAC data via WCS...")
try:
    response = requests.get(wcs_url, params=params, stream=True, timeout=180)
    response.raise_for_status()
    
    with MemoryFile(response.content) as memfile:
        with memfile.open() as src:
            profile = src.profile
            data = src.read()
            
    with rasterio.open(out_path, 'w', **profile) as dst:
        dst.write(data)
        
    print(f"✅ Success! Real SSGI LASAC data saved to: {out_path}")
except Exception as e:
    print(f"❌ Failed to download from SSGI WCS. Error: {e}")