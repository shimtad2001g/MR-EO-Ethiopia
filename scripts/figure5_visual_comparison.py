import rasterio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import os

print("Generating Publication-Ready Figure 5: Visual Comparison...")

raw_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\s2_aligned.tif"
class_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\landcover_classified.tif"
out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_5_Visual_Comparison.png"

# 1. Read and stretch the raw image
with rasterio.open(raw_path) as src:
    raw = src.read([1, 2, 3])
    raw = np.moveaxis(raw, 0, -1)
    
    # Percentile stretch for better contrast
    p2, p98 = np.percentile(raw, (2, 98))
    raw_rgb = np.clip((raw - p2) / (p98 - p2), 0, 1)

# 2. Read the classified image
with rasterio.open(class_path) as src:
    classified = src.read(1)

# 3. Setup the side-by-side plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))

# Left panel: Raw Image
ax1.imshow(raw_rgb)
ax1.set_title("Raw Sentinel-2 Image (True Color)", fontsize=16, fontweight='bold', pad=15)
ax1.axis('off')

# Right panel: AI Classification
# Define custom colors for the 3 classes: 0=Veg (Green), 1=Urban (Gray), 2=Water (Blue)
cmap = ListedColormap(['#2ca02c', '#7f7f7f', '#1f77b4'])
im2 = ax2.imshow(classified, cmap=cmap, vmin=0, vmax=2)
ax2.set_title("AI-Classified Land Cover (XGBoost)", fontsize=16, fontweight='bold', pad=15)
ax2.axis('off')

# 4. Add a professional legend to the right panel
legend_elements = [
    Patch(facecolor='#2ca02c', edgecolor='black', label='Vegetation (Class 0)'),
    Patch(facecolor='#7f7f7f', edgecolor='black', label='Urban/Bare Soil (Class 1)'),
    Patch(facecolor='#1f77b4', edgecolor='black', label='Water Bodies (Class 2)')
]
ax2.legend(handles=legend_elements, loc='lower right', fontsize=13, 
           framealpha=0.9, edgecolor='black', title="AI Predictions", title_fontsize=14)

# Main Title
plt.suptitle("Figure 5: Visual Comparison of AI Classification", fontsize=20, fontweight='bold', y=0.98)

# rect=[0, 0, 1, 0.95] tells the plot to leave 5% space at the top for the suptitle
plt.tight_layout(rect=[0, 0, 1, 0.95]) 
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ Figure 5 successfully saved to: {out_img}")