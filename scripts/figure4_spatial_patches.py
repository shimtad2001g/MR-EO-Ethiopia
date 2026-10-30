import rasterio
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

print("Generating Figure 4: Spatial Distribution of Validation Patches...")

# Load image
img_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\s2_aligned.tif"
with rasterio.open(img_path) as src:
    img = src.read()
    img = np.moveaxis(img, 0, -1)
    img_rgb = np.clip(img / 10000.0, 0, 1)

# Generate the same 100 random coordinates used in validation
np.random.seed(42)
patch_size = 224
coords = []
for _ in range(100):
    y = np.random.randint(0, img.shape[0] - patch_size)
    x = np.random.randint(0, img.shape[1] - patch_size)
    # Center of the patch
    coords.append((x + patch_size//2, y + patch_size//2))

coords = np.array(coords)

# Plot
fig, ax = plt.subplots(figsize=(12, 12))
ax.imshow(img_rgb)

# Plot the validation points
ax.scatter(coords[:, 0], coords[:, 1], c='red', s=60, marker='o', 
           edgecolors='yellow', linewidths=1.5, label='Validation Patch Center', alpha=0.8)

# Add a yellow border around the map
rect = Rectangle((0, 0), img.shape[1], img.shape[0], linewidth=4, edgecolor='yellow', facecolor='none')
ax.add_patch(rect)

ax.set_title("Figure 4: Spatial Distribution of 100 Validation Patches\n(Addis Ababa)", fontsize=18, fontweight='bold')
ax.legend(loc='upper right', fontsize=14, facecolor='black', labelcolor='white')
ax.axis('off')

plt.tight_layout()
out_path = r"C:\Users\SHIMELES_TADESSE\MR-EO-Ethiopia\outputs\Figure_4_Spatial_Patches.png"
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"✅ Figure 4 successfully saved to: {out_path}")