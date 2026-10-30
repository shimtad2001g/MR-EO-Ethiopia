# File: generate_pseudo_labels.py
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import config_gamo_gofa as config

def generate_labels():
    print("--- Generating Pseudo-Labels (K-Means) ---")
    patch_files = sorted(list(config.PROCESSED_DIR.glob("*.npy")))
    
    features = []
    filenames = []
    
    print(f"Extracting spectral features from {len(patch_files)} patches...")
    for f in patch_files:
        patch = np.load(f)
        rgb = patch[:3, :, :] / 10000.0
        
        # Extract Mean and Standard Deviation of each band as our features
        mean_rgb = np.mean(rgb, axis=(1,2))
        std_rgb = np.std(rgb, axis=(1,2))
        
        features.append(np.concatenate([mean_rgb, std_rgb]))
        filenames.append(f.name)
        
    features = np.array(features)
    
    print("Running K-Means clustering (5 clusters)...")
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    labels = kmeans.fit_predict(features)
    
    df = pd.DataFrame({
        'Patch_File': filenames, 
        'Pseudo_Label': labels
    })
    
    out_csv = config.OUT_CROP_MAPS / "pseudo_labels.csv"
    df.to_csv(out_csv, index=False)
    print(f"[SUCCESS] Saved pseudo-labels to: {out_csv}")

if __name__ == "__main__":
    generate_labels()
