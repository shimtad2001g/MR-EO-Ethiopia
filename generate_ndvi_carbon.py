# File: generate_ndvi_carbon.py
import numpy as np
import pandas as pd
import config_gamo_gofa as config

def generate_ndvi_labels():
    print("--- Generating Proxy Carbon Labels (NDVI) ---")
    patch_files = sorted(list(config.PROCESSED_DIR.glob("*.npy")))
    
    data = []
    for f in patch_files:
        patch = np.load(f)
        # Band 3 (index 2) is Red, Band 4 (index 3) is NIR
        red = patch[2, :, :].astype(float)
        nir = patch[3, :, :].astype(float)
        
        # Calculate NDVI: (NIR - Red) / (NIR + Red)
        # Add a tiny number to denominator to avoid division by zero
        ndvi = (nir - red) / (nir + red + 1e-8)
        
        # Get mean NDVI for the patch
        mean_ndvi = np.mean(ndvi)
        
        # Proxy AGBD calculation (e.g., assuming max biomass is 200 tons/ha at NDVI=1.0)
        # We clip negative values to 0
        proxy_agbd = max(0.0, mean_ndvi * 200.0)
        
        data.append({
            'Patch_File': f.name,
            'Carbon_AGBD': proxy_agbd
        })
        
    df = pd.DataFrame(data)
    out_csv = config.OUT_CARBON_MAPS / "carbon_labels.csv"
    df.to_csv(out_csv, index=False)
    print(f"[SUCCESS] Generated proxy carbon labels for {len(df)} patches.")
    print(f"Saved to: {out_csv}")
    print(f"Sample AGBD values (tons/ha):\n{df['Carbon_AGBD'].describe()}")

if __name__ == "__main__":
    generate_ndvi_labels()
