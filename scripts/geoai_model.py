import rasterio
import numpy as np
from sklearn.cluster import KMeans
import os

# Paths
in_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\s2_aligned.tif"
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\landcover_classified.tif"

print("1. Loading the harmonized image...")
with rasterio.open(in_path) as src:
    img_data = src.read()
    profile = src.profile
    
    # Rasterio reads bands as (Bands, Rows, Cols). 
    # We need to reshape it to (Total_Pixels, Bands) for Scikit-Learn
    bands, rows, cols = img_data.shape
    img_2d = img_data.reshape((bands, rows * cols)).T 
    
    # Get the transform and crs to save the output later
    transform = src.transform
    crs = src.crs

print(f"   Image loaded. Shape: {img_data.shape}")

print("\n2. Training the Machine Learning Model (K-Means Clustering)...")
# We will cluster into 3 classes: 0, 1, 2
# Setting a random state ensures we get the same result every time
kmeans = KMeans(n_clusters=3, random_state=42)
print("   Fitting model to pixel data (this might take 10-20 seconds)...")
kmeans.fit(img_2d)

print("\n3. Predicting land cover classes for every pixel...")
predicted_labels = kmeans.labels_

# Reshape the 1D predictions back into a 2D image (Rows x Cols)
classified_img = predicted_labels.reshape((rows, cols))

print("\n4. Saving the classified map...")
# Update the profile to save a single band instead of 3
profile.update(
    dtype=rasterio.uint8,
    count=1,
    compress='lzw'
)

with rasterio.open(out_path, 'w', **profile) as dst:
    dst.write(classified_img.astype(rasterio.uint8), 1)

print(f"\n✅ GeoAI Modeling Complete! Classified map saved to: {out_path}")