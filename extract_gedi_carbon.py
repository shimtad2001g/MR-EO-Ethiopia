# File: extract_gedi_carbon.py
import planetary_computer
import pystac_client
import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
from rasterio.transform import rowcol
import config_gamo_gofa as config

def fetch_gedi_data():
    print("--- Fetching GEDI Carbon (AGBD) Data ---")
    aoi = gpd.read_file(config.AOI_SHAPEFILE)
    bounds = tuple(aoi.total_bounds)
    
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )
    
    print("Searching for GEDI L4A points...")
    search = catalog.search(
        collections=["gedi-l4a"],
        bbox=bounds,
        datetime="2019-01-01/2023-12-31",
        max_items=100
    )
    
    items = list(search.items())
    if not items:
        print("[WARNING] No GEDI data found for this AOI.")
        return False
        
    print(f"Found {len(items)} GEDI items. Downloading points...")
    
    all_gedi_points = []
    for item in items:
        asset = item.assets.get("agbd")
        if not asset: continue
        
        try:
            gdf = gpd.read_file(asset.href)
            # Filter points that fall inside our AOI
            gdf = gdf[gdf.within(aoi.geometry.unary_union)]
            if not gdf.empty:
                all_gedi_points.append(gdf[['agbd', 'geometry']])
        except Exception as e:
            pass
            
    if not all_gedi_points:
        print("[WARNING] No GEDI points intersected the AOI.")
        return False
        
    gedi_df = pd.concat(all_gedi_points)
    print(f"Total GEDI points found in AOI: {len(gedi_df)}")
    
    # Match points to our Sentinel-2 patches
    original_tif = config.RAW_S2_DIR / "gamo_gofa_sample_s2.tif"
    with rasterio.open(original_tif) as src:
        transform = src.transform
        img_height = src.height
        img_width = src.width
        
    matched_data = []
    for _, row in gedi_df.iterrows():
        lon = row.geometry.x
        lat = row.geometry.y
        agbd_val = row['agbd']
        
        row_idx, col_idx = rowcol(transform, lon, lat)
        if 0 <= row_idx < img_height and 0 <= col_idx < img_width:
            patch_row = row_idx // config.PATCH_SIZE
            patch_col = col_idx // config.PATCH_SIZE
            patches_per_row = img_width // config.PATCH_SIZE
            patch_idx = (patch_row * patches_per_row) + patch_col
            patch_name = f"gamo_gofa_sample_s2_patch_{patch_idx}.npy"
            
            matched_data.append({
                'Patch_File': patch_name,
                'Carbon_AGBD': float(agbd_val)
            })
            
    if matched_data:
        df_out = pd.DataFrame(matched_data).groupby('Patch_File').mean().reset_index()
        out_csv = config.OUT_CARBON_MAPS / "carbon_labels.csv"
        df_out.to_csv(out_csv, index=False)
        print(f"[SUCCESS] Extracted {len(df_out)} carbon-labeled patches to {out_csv}")
        return True
    else:
        print("[WARNING] GEDI points did not overlap with downloaded image patches.")
        return False

if __name__ == "__main__":
    fetch_gedi_data()
