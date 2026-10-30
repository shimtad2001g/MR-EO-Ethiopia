import rasterio
import numpy as np

out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\landcover_classified.tif"

with rasterio.open(out_path) as src:
    img = src.read(1)
    
    # Count pixels for each class (0, 1, 2)
    unique, counts = np.unique(img, return_counts=True)
    total_pixels = img.size
    
    print("\n--- Model Validation: Class Distribution ---")
    for cls, count in zip(unique, counts):
        percentage = (count / total_pixels) * 100
        print(f"Class {cls}: {count} pixels ({percentage:.2f}%)")