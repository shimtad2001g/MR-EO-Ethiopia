import rasterio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

print("Generating Pre-print Standard Figure 5: Visual Comparison (Addis Ababa)...")

raw_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\s2_aligned.tif"
class_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\landcover_classified.tif"

# 1. Read and stretch the raw image
with rasterio.open(raw_path) as src:
    raw = src.read([1, 2, 3])
    raw = np.moveaxis(raw, 0, -1)
    p2, p98 = np.percentile(raw, (2, 98))
    raw_rgb = np.clip((raw - p2) / (p98 - p2), 0, 1)

# 2. Read the classified image
with rasterio.open(class_path) as src:
    classified = src.read(1)

# 3. Setup the side-by-side plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))

# Left panel: Raw Image
ax1.imshow(raw_rgb)
ax1.set_title("Raw Sentinel-2 Image (True Color)", fontsize=18, fontweight='bold')
ax1.axis('off')

# Right panel: AI Classification
# Classes: 0=Veg (Green), 1=Urban (Gray), 2=Water (Blue)
cmap = ListedColormap(['#2ca02c', '#7f7f7f', '#1f77b4'])
im2 = ax2.imshow(classified, cmap=cmap, vmin=0, vmax=2)
ax2.set_title("AI-Classified Land Cover (XGBoost)", fontsize=18, fontweight='bold')
ax2.axis('off')

# 4. Add a professional legend to the right panel
legend_elements = [
    Patch(facecolor='#2ca02c', edgecolor='black', label='Vegetation (Class 0)'),
    Patch(facecolor='#7f7f7f', edgecolor='black', label='Urban/Bare Soil (Class 1)'),
    Patch(facecolor='#1f77b4', edgecolor='black', label='Water Bodies (Class 2)')
]
ax2.legend(handles=legend_elements, loc='lower right', fontsize=14, 
           framealpha=0.9, edgecolor='black', title="AI Predictions", title_fontsize=15)

# Main Title
fig.suptitle("Visual Comparison of AI Classification (Addis Ababa)", fontsize=22, fontweight='bold')

# Adjust layout to prevent title overlap
fig.subplots_adjust(top=0.88, wspace=0.05)

# Save high-resolution image
out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_5_V2_Comparison_Final.png"
plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ Figure 5 successfully saved to: {out_img}")