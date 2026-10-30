# File: preprocess_gamo_gofa.py
import os
import glob
import numpy as np
import rasterio
from rasterio.windows import Window
from pathlib import Path
import config_gamo_gofa as config

def create_patches():
    print("--- Starting Gamo-Gofa Data Preprocessing ---")
    
    # FIX: Include the C: drive RAW_S2_DIR in the search paths
    search_paths = [
        str(config.RAW_S2_DIR / "*.tif"), # <-- NEW: Look where we just downloaded
        str(config.D_DRIVE_CARBON / "04_Earth_Observation" / "Sentinel_2" / "Preprocessed" / "**" / "*.tif"),
        str(config.D_DRIVE_CARBON / "04_Earth_Observation" / "Sentinel_2" / "Raw" / "**" / "*.tif")
    ]
    
    tif_files = []
    for path in search_paths:
        tif_files.extend(glob.glob(path, recursive=True))
        
    if not tif_files:
        print("[WARNING] No .tif files found in the specified directories.")
        return

    print(f"Found {len(tif_files)} TIF files. Beginning tiling process...")
    
    patch_size = config.PATCH_SIZE
    patch_count = 0
    
    for tif_path in tif_files:
        filename = Path(tif_path).stem
        print(f"Processing: {filename}")
        
        try:
            with rasterio.open(tif_path) as src:
                height = src.height
                width = src.width
                
                for j in range(0, height, patch_size):
                    for i in range(0, width, patch_size):
                        window = Window(i, j, patch_size, patch_size)
                        patch = src.read(window=window)
                        
                        if patch.shape[1] != patch_size or patch.shape[2] != patch_size:
                            continue
                            
                        out_name = f"{filename}_patch_{patch_count}.npy"
                        out_path = config.PROCESSED_DIR / out_name
                        np.save(out_path, patch)
                        patch_count += 1
                        
        except Exception as e:
            print(f"[ERROR] Failed to process {filename}: {e}")

    print(f"\n[SUCCESS] Preprocessing complete. Generated {patch_count} patches.")
    print(f"Saved to: {config.PROCESSED_DIR}")

if __name__ == "__main__":
    create_patches()
