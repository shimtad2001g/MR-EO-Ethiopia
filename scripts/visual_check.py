import rasterio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
import os

# Paths
raw_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\s2_aligned.tif"
class_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\landcover_classified.tif"
out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_2_Visual_Comparison.png"

print("Generating Figure 2...")

# Read raw image
with rasterio.open(raw_path) as src:
    raw = src.read()
    raw_rgb = np.transpose(raw, (1, 2, 0))
    # Normalize to 0-1 for matplotlib visualization
    raw_rgb = raw_rgb / 10000.0 
    raw_rgb = np.clip(raw_rgb, 0, 1)

# Read classified image
with rasterio.open(class_path) as src:
    classified = src.read(1)

# Create figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# Plot Raw Sentinel-2
ax1.imshow(raw_rgb)
ax1.set_title("Raw Sentinel-2 Image (Addis Ababa)", fontsize=16, fontweight='bold')
ax1.axis('off')

# Plot AI Classification
# Using a custom colormap: Green (Veg), Gray (Urban), Blue (Water)
cmap = ListedColormap(['#2ca02c', '#7f7f7f', '#1f77b4']) 
im2 = ax2.imshow(classified, cmap=cmap, vmin=0, vmax=2)
ax2.set_title("AI-Classified Land Cover (Self-Supervised)", fontsize=16, fontweight='bold')
ax2.axis('off')

# Add a colorbar legend
cbar = plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04, ticks=[0, 1, 2])
cbar.ax.set_yticklabels(['Vegetation', 'Urban/Bare', 'Water'], fontsize=12)

plt.tight_layout()
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ Figure 2 successfully saved to: {out_img}")