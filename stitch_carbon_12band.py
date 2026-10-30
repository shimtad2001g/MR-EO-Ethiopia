# File: stitch_carbon_12band.py
import numpy as np
import pandas as pd
import rasterio
import config_gamo_gofa as config

def stitch_carbon():
    print("--- Reconstructing 12-Band Carbon GeoTIFF Map ---")
    original_tif = config.RAW_S2_DIR / "gamo_gofa_sample_s2.tif"
    with rasterio.open(original_tif) as src:
        meta = src.meta.copy()
        height = src.height
        width = src.width
        
    meta.update({"count": 1, "dtype": "float32", "nodata": -9999.0})
    final_map = np.full((height, width), -9999.0, dtype=np.float32)
    
    pred_csv = config.OUT_CARBON_MAPS / "carbon_predictions_12band.csv"
    df = pd.read_csv(pred_csv)
    pred_dict = {row['Patch_File']: row['Predicted_Carbon_AGBD'] for _, row in df.iterrows()}
    
    patch_size = config.PATCH_SIZE
    filename = "gamo_gofa_sample_s2"
    patch_idx = 0
    
    for j in range(0, height, patch_size):
        for i in range(0, width, patch_size):
            if height - j < patch_size or width - i < patch_size:
                continue
            patch_name = f"{filename}_patch_{patch_idx}.npy"
            if patch_name in pred_dict:
                final_map[j:j+patch_size, i:i+patch_size] = pred_dict[patch_name]
            patch_idx += 1
            
    out_tif = config.OUT_CARBON_MAPS / "gamo_gofa_carbon_map_12band.tif"
    with rasterio.open(out_tif, "w", **meta) as dest:
        dest.write(final_map, 1)
    print(f"[SUCCESS] Map saved to: {out_tif}")

if __name__ == "__main__":
    stitch_carbon()
