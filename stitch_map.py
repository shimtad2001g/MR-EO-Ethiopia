# File: stitch_map.py
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window
import config_gamo_gofa as config

def stitch_predictions():
    print("--- Reconstructing Georeferenced Map ---")
    
    # 1. Load the original TIF to get geospatial metadata
    original_tif = config.RAW_S2_DIR / "gamo_gofa_sample_s2.tif"
    with rasterio.open(original_tif) as src:
        meta = src.meta.copy()
        height = src.height
        width = src.width
    
    # Update metadata for a single-band classification map
    meta.update({
        "count": 1,
        "dtype": "uint8",
        "nodata": 0
    })
    
    # 2. Create an empty array for the final map
    final_map = np.zeros((height, width), dtype=np.uint8)
    
    # 3. Load predictions
    pred_csv = config.OUT_CROP_MAPS / "gamo_gofa_predictions.csv"
    df = pd.read_csv(pred_csv)
    
    # Create a dictionary for fast lookup: {"patch_0.npy": 2, "patch_1.npy": 0, ...}
    # Note: We add 1 to the class IDs so that Class 0 (Enset) doesn't conflict with the NoData value (0)
    pred_dict = {row['Patch_File']: row['Predicted_Class_ID'] + 1 for _, row in df.iterrows()}
    
    print("Filling in the map grid...")
    patch_size = config.PATCH_SIZE
    filename = "gamo_gofa_sample_s2"
    patch_idx = 0
    
    # We MUST iterate in the exact same order as the preprocessing script
    for j in range(0, height, patch_size):
        for i in range(0, width, patch_size):
            # Skip incomplete edge patches (exactly like the preprocessing script)
            if height - j < patch_size or width - i < patch_size:
                continue
                
            patch_name = f"{filename}_patch_{patch_idx}.npy"
            
            if patch_name in pred_dict:
                predicted_class = pred_dict[patch_name]
                # Fill the 256x256 block in the final map
                final_map[j:j+patch_size, i:i+patch_size] = predicted_class
                
            patch_idx += 1
            
    # 4. Save the final GeoTIFF
    out_tif = config.OUT_CROP_MAPS / "gamo_gofa_classification_map.tif"
    with rasterio.open(out_tif, "w", **meta) as dest:
        dest.write(final_map, 1)
        
    print(f"\n[SUCCESS] Map successfully stitched and saved to:")
    print(f"  -> {out_tif}")
    print("\nClass ID Legend (for QGIS):")
    print("  1 = Enset (Cluster A)")
    print("  2 = Maize (Cluster B)")
    print("  3 = Barley (Cluster C)")
    print("  4 = Forest (Cluster D)")
    print("  5 = Other/Water/Bare (Cluster E)")

if __name__ == "__main__":
    stitch_predictions()
