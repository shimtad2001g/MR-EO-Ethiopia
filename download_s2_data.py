# File: download_s2_data.py
import os
os.environ['GDAL_HTTP_MAX_RETRY'] = '5'
os.environ['GDAL_HTTP_RETRY_DELAY'] = '3'
os.environ['GDAL_HTTP_TIMEOUT'] = '120'

import pystac_client
import rioxarray
import geopandas as gpd
import config_gamo_gofa as config
import xarray as xr

def fetch_sample_data():
    print("--- Starting AWS Earth Search 12-Band Download (Aligned) ---")
    aoi = gpd.read_file(config.AOI_SHAPEFILE)
    bounds = tuple(aoi.total_bounds)
    
    catalog = pystac_client.Client.open("https://earth-search.aws.element84.com/v1")
    
    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bounds,
        datetime="2023-01-01/2023-02-28",
        query={"eo:cloud_cover": {"lt": 10}},
        max_items=1
    )
    
    items = list(search.items())
    if not items:
        print("[ERROR] No imagery found.")
        return
        
    item = items[0]
    print(f"Found scene: {item.id}")
    
    band_mapping = {
        "B01": "coastal", "B02": "blue", "B03": "green", "B04": "red",
        "B05": "rededge1", "B06": "rededge2", "B07": "rededge3", "B08": "nir",
        "B8A": "nir08", "B09": "nir09", "B11": "swir16", "B12": "swir22"
    }
    
    print(f"Downloading and clipping {len(band_mapping)} bands...")
    clipped_data = {}
    reference_da = None
    
    for band_name, asset_key in band_mapping.items():
        print(f"  -> Fetching {band_name} ({asset_key})...")
        asset = item.assets[asset_key]
        da = rioxarray.open_rasterio(asset.href)
        aoi_projected = aoi.to_crs(da.rio.crs)
        da_clipped = da.rio.clip_box(*aoi_projected.total_bounds)
        
        if band_name == "B02":
            reference_da = da_clipped
            
        clipped_data[band_name] = da_clipped
    
    print("  -> Resampling all bands to 10m grid...")
    aligned_data = []
    for band_name in band_mapping.keys():
        da = clipped_data[band_name]
        if reference_da is not None and da.shape != reference_da.shape:
            da = da.rio.reproject_match(reference_da)
        aligned_data.append(da)
    
    print("  -> Stacking bands...")
    stacked = xr.concat(aligned_data, dim="band", join="override")
    stacked["band"] = list(band_mapping.keys())
    
    out_path = config.RAW_S2_DIR / "gamo_gofa_sample_s2.tif"
    stacked.rio.to_raster(out_path)
    print(f"[SUCCESS] Saved 12-band image to: {out_path}")

if __name__ == "__main__":
    fetch_sample_data()