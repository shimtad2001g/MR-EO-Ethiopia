import rasterio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

print("Generating FINAL Figure 5...")

raw_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\s2_aligned.tif"
class_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\landcover_classified.tif"
out_img = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_5_FINAL.png"

with rasterio.open(raw_path) as src:
    raw = src.read([1, 2, 3])
    raw = np.moveaxis(raw, 0, -1)
    p2, p98 = np.percentile(raw, (2, 98))
    raw_rgb = np.clip((raw - p2) / (p98 - p2), 0, 1)

with rasterio.open(class_path) as src:
    classified = src.read(1)

# Create figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))

# Left: Raw
ax1.imshow(raw_rgb)
ax1.set_title("Raw Sentinel-2 Image (True Color)", fontsize=16, fontweight='bold')
ax1.axis('off')

# Right: AI
cmap = ListedColormap(['#2ca02c', '#7f7f7f', '#1f77b4'])
im2 = ax2.imshow(classified, cmap=cmap, vmin=0, vmax=2)
ax2.set_title("AI-Classified Land Cover (XGBoost)", fontsize=16, fontweight='bold')
ax2.axis('off')

# Legend
legend_elements = [
    Patch(facecolor='#2ca02c', edgecolor='black', label='Vegetation (Class 0)'),
    Patch(facecolor='#7f7f7f', edgecolor='black', label='Urban/Bare Soil (Class 1)'),
    Patch(facecolor='#1f77b4', edgecolor='black', label='Water Bodies (Class 2)')
]
ax2.legend(handles=legend_elements, loc='lower right', fontsize=13, 
           framealpha=0.9, edgecolor='black', title="AI Predictions", title_fontsize=14)

# THE FIX: Use subplots_adjust to push the subplots down and leave room for the main title
fig.subplots_adjust(top=0.85)

# Main Title
fig.suptitle("Figure 5: Visual Comparison of AI Classification", fontsize=22, fontweight='bold')

plt.savefig(out_img, dpi=300, bbox_inches='tight')
print(f"✅ Figure 5 successfully saved to: {out_img}")